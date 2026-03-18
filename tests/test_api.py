import requests
 
print("Testing FastAPI endpoint...")
print("(Make sure server is running: uvicorn app.main:app --reload)")
print("-" * 50)
 
url = "http://127.0.0.1:8000/ask"
 
payload = {"question": "Show me all sale transactions"}
 
response = requests.post(url, json=payload)
 
if response.status_code == 200:
    data = response.json()
    print("API endpoint working!")
    print(f"   Status  : {response.status_code}")
    print(f"   Question: {data['question']}")
    print(f"   SQL     : {data['sql']}")
    print(f"   Answer  : {data['answer'][:80]}...")
else:
    print(f"API failed with status {response.status_code}")
    print(f"   Error: {response.text}")
 