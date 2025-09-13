import random
from time import sleep
from pydantic import BaseModel
import pymongo
from bson import ObjectId
from dotenv import load_dotenv

client = pymongo.MongoClient(
    "mongodb://daniel:daniel@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true"
)

enrollDatabase = client["enrollDatabase"]
enrollCollection = enrollDatabase["enrollCollection"]
messageCollection = enrollDatabase["messageCollection"]


class Message(BaseModel):
    enroll_id: str


def process_message(message: Message) -> bool:
    print(f"Start processing message enroll_id: {message.enroll_id}...")
    sleep(random.randint(1, 3))
    rnd = random.randint(1, 10)
    if rnd < 3:
        print(f"Failed to process message for enroll_id: {message.enroll_id}")
        return False

    enroll = enrollCollection.find_one({"_id": ObjectId(message.enroll_id)})
    if not enroll:
        print(f"Enroll with id {message.enroll_id} not found.")
        return False  # Consider as processed to remove from queue

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
            print(f"Message for enroll_id: {message.enroll_id} processed successfully.")


def run():
    while True:
        main_loop()
        sleep(10)
        print(f"\n\n---\n\n")


if __name__ == "__main__":
    run()
