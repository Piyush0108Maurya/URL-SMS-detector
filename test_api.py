import requests

with open("demo_test.csv", "rb") as f:
    r = requests.post("http://127.0.0.1:8000/predict-batch", files={"file": f})
    
print(r.json())
