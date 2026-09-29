import requests
urls = ["github.com", "wikipedia.org", "whatsapp.com", "amazon.in"]
for u in urls:
    r = requests.post("http://127.0.0.1:8000/predict", json={"text": u})
    print(u, r.json()["label"], r.json()["confidence"])
