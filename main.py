echo "from fastapi import FastAPI, Request
import hmac
import hashlib
import requests
import os

app = FastAPI()

ZADARMA_KEY = os.getenv('ZADARMA_KEY')
ZADARMA_SECRET = os.getenv('ZADARMA_SECRET')
MONDAY_API_TOKEN = os.getenv('MONDAY_API_TOKEN')
MONDAY_BOARD_ID = os.getenv('MONDAY_BOARD_ID')

def verify_zadarma_signature(request_body, expected_signature):
 calculated_signature = hmac.new(
     ZADARMA_SECRET.encode(), request_body, hashlib.sha1
 ).hexdigest()
 return calculated_signature == expected_signature

@app.post('/zadarma-webhook')
async def zadarma_webhook(request: Request):
 headers = request.headers
 request_body = await request.body()
 
 if not verify_zadarma_signature(request_body, headers.get('Signature', '')):
     return {'status': 'error', 'message': 'Invalid signature'}
 
 data = await request.json()
 
 call_id = data.get('call_id')
 caller_number = data.get('caller_id')
 destination_number = data.get('destination')
 call_duration = data.get('duration')
 call_status = data.get('status')

 monday_url = 'https://api.monday.com/v2'
 query = f\"\"\"
 mutation {{
     create_item (
         board_id: {MONDAY_BOARD_ID},
         item_name: 'Звонок от {caller_number}',
         column_values: '{{
             \\"Телефон клиента\\": \\"{caller_number}\\",
             \\"Номер назначения\\": \\"{destination_number}\\",
             \\"Длительность\\": \\"{call_duration} сек\\",
             \\"Статус\\": \\"{call_status}\\"
         }}'
     ) {{
         id
     }}
 }}
 \"\"\"

 response = requests.post(
     monday_url,
     headers={{
         'Authorization': MONDAY_API_TOKEN,
         'Content-Type': 'application/json'
     }},
     json={{'query': query}}
 )

 return {{'status': 'success', 'monday_response': response.json()}}" > main.py
