import requests

url = "https://thales-chatbot-247661586830.us-central1.run.app/api/v1/query"
payloads = [
    {"grade_filter": "1PUC", "language_preference": "en", "question": "What is electrostatic potential?"},
    {"language_preference": "en", "question": "What is electrostatic potential?"},
    {"grade_filter": "1PUC", "question": "What is electrostatic potential?"},
    {"question": "What is electrostatic potential?"}
]

for p in payloads:
    try:
        r = requests.post(url, json=p)
        print(list(p.keys()), r.status_code, r.text)
    except Exception as e:
        print("FAILED", e)
