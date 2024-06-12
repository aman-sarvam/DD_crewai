import http.client
import json
from dotenv import load_dotenv
import os 

load_dotenv()

serper_api_key = os.getenv("SERPER_API_KEY")
print(serper_api_key)

conn = http.client.HTTPSConnection("google.serper.dev")
payload = json.dumps({
  "q": "apple inc"
})
headers = {
  'X-API-KEY': serper_api_key
  ,
  'Content-Type': 'application/json'
}
conn.request("POST", "/search", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))