from random import randint
from time import sleep
from faker import Faker
import requests
import sys
fake = Faker("pt_BR")

def generate_fake_data():
    return {
        "name": fake.name(),
        "age": fake.random_int(min=1, max=90),
        "cpf": fake.cpf()
    }


def run():
    # Get count from command line argument or use random value
    if len(sys.argv) > 1:
        try:
            print(f"Generating {sys.argv[1]} fake data entries.")
            count = int(sys.argv[1])
        except ValueError:
            print("Invalid count argument. Using random value between 2 and 8.")
            count = randint(2, 8)
    else:
        print("No count argument provided. Using random value between 2 and 8.")
        count = randint(2, 8)
    
    for _ in range(count):
        data = generate_fake_data()
        response = requests.post("http://localhost:8000/enroll", json=data)
        if response.status_code == 200:
            print(f"Successfully created enroll for {data['name']}.")
        else:
            print(f"Failed to create enroll for {data['name']}. Status code: {response.status_code}, Response: {response.text}")
        print(data)
        print("-")
    
if __name__ == "__main__":
    run()