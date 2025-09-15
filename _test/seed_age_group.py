import json
import requests

def run():
    data = [
        {"min_age": 13, "max_age": 19, "description": "Teen"},
        {"min_age": 20, "max_age": 60, "description": "Adult"},
        {"min_age": 61, "max_age": 100, "description": "Senior"},
    ]
    for ag in data:
        url = "http://localhost:8000/age-groups"

        payload = json.dumps({
            "min_age": ag["min_age"],
            "max_age": ag["max_age"],
            "description": ag["description"]
        })
        headers = {
        'Content-Type': 'application/json',
        'Cookie': 'NEXT_LOCALE=en-US'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            print(f"Successfully created age group {ag['description']}.")
        else:
            print(f"Failed to create age group {ag['description']}. Status code: {response.status_code}, Response: {response.text}")
        print(ag)
        print("-")
    
if __name__ == "__main__":
    run()