import os
import random
from time import sleep
from pydantic import BaseModel
import pymongo
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

_user = os.getenv("DB_USERNAME")
_password = os.getenv("DB_PASSWORD")
_host = os.getenv("DB_HOST")

print(f"DB_USER: {_user}, DB_HOST: {_host}")

client = pymongo.MongoClient(
    f"mongodb://{_user}:{_password}@{_host}:27017/?authSource=admin&tlsAllowInvalidCertificates=true"
)

enrollDatabase = client["enrollDatabase"]
enrollCollection = enrollDatabase["enrollCollection"]
messageCollection = enrollDatabase["messageCollection"]


class Message(BaseModel):
    enroll_id: str


def process_message(message: Message) -> bool:
    enroll = enrollCollection.find_one({"_id": ObjectId(message.enroll_id)})
    if not enroll:
        print(f"Enroll with id {message.enroll_id} not found.")
        return False  # Consider as processed to remove from queue


    print(f"Start processing message for {enroll['name']}...")
    sleep(random.randint(2, 3))
    rnd = random.randint(1, 10)
    if rnd < 4:
        print(f"Failed to process message for {enroll['name']}. Will retry later.")
        return False

    new_status = ["granted", "denied"][random.randint(0, 1)]
    enrollCollection.update_one(
        {"_id": ObjectId(message.enroll_id)}, {"$set": {"status": new_status}}
    )
    return True


def main_loop():
    messages = messageCollection.find()
    messages = list(messages)
    print(f"Found {len(messages)} messages in the queue.")
    for msg in messages:
        message = Message(enroll_id=msg["enroll_id"])
        if process_message(message):
            messageCollection.delete_one({"_id": msg["_id"]})
            enroll = enrollCollection.find_one({"_id": ObjectId(message.enroll_id)})
            print(f"Message for {enroll['name']} processed successfully.")
        print("-")


def run():
    while True:
        main_loop()
        print(f"---\n\n")
        sleep(10)


if __name__ == "__main__":
    run()
