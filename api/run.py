import os
from fastapi import FastAPI, HTTPException
import pymongo
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

_user = os.getenv("DB_USERNAME")
_password = os.getenv("DB_PASSWORD")
_host = os.getenv("DB_HOST")

print(f"DB_USER: {_user}, DB_HOST: {_host}")

# SETUP ================================================================
app = FastAPI()
client = pymongo.MongoClient(
    f"mongodb://{_user}:{_password}@{_host}:27017/?authSource=admin&tlsAllowInvalidCertificates=true"
)

enrollDatabase = client["enrollDatabase"]
enrollCollection = enrollDatabase["enrollCollection"]
ageGroupCollection = enrollDatabase["ageGroupCollection"]
messageCollection = enrollDatabase["messageCollection"]

# SCHEMA ===============================================================
from pydantic import BaseModel


class AgeGroup(BaseModel):
    min_age: int
    max_age: int
    description: str


class Enroll(BaseModel):
    name: str
    cpf: str
    age: int
    age_group: AgeGroup
    status: str


class EnrollCreateDTO(BaseModel):
    name: str
    cpf: str
    age: int

class EnrollUpdateDTO(BaseModel):
    name: str | None = None
    cpf: str | None = None
    age: int | None = None


class Message(BaseModel):
    enroll_id: str


# UTILS ================================================================
from bson import json_util
import json


def parse_json(data):
    return json.loads(json_util.dumps(data))


# ENDPOINTS ============================================================
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/enroll/{enroll_id}")
def get_enroll(enroll_id: str):
    try:
        # Convert string to ObjectId for MongoDB query
        object_id = ObjectId(enroll_id)
        enroll = enrollCollection.find_one({"_id": object_id})
        if enroll:
            # enroll["_id"] = str(enroll["_id"])
            # enroll["age_group_id"] = str(enroll["age_group_id"])
            return {"enroll": parse_json(enroll)}
        return {"error": "Enroll not found"}, 404
    except Exception as e:
        return {"error": f"Invalid ID format: {str(e)}"}, 400


@app.get("/enroll")
def list_enrolls():
    enrolls = enrollCollection.find()
    enrolls = list(enrolls)
    # Convert ObjectId to string for JSON serialization
    return {"enrolls": parse_json(enrolls)}


@app.post("/enroll")
def create_enroll(enroll: EnrollCreateDTO):
    age_group = ageGroupCollection.find_one(
        {"min_age": {"$lte": enroll.age}, "max_age": {"$gte": enroll.age}}
    )

    if not age_group:
        raise HTTPException(status_code=400, detail="No age group found for this age")

    new_enroll = enrollCollection.insert_one(
        {**enroll.model_dump(), "age_group": age_group, "status": "pending"}
    )

    message = messageCollection.insert_one({"enroll_id": str(new_enroll.inserted_id)})

    return {"id": str(new_enroll.inserted_id)}


@app.put("/enroll/{enroll_id}")
def update_enroll(enroll_id: str, enroll: EnrollUpdateDTO):
    try:
        # Convert string to ObjectId for MongoDB query
        object_id = ObjectId(enroll_id)
        result = enrollCollection.update_one(
            {"_id": object_id}, {"$set": enroll.model_dump()}
        )
        return {
            "modified_count": result.modified_count,
            "matched_count": result.matched_count,
        }
    except Exception as e:
        return {"error": f"Invalid ID format: {str(e)}"}, 400


@app.get("/age-groups")
def list_age_groups():
    age_groups = ageGroupCollection.find()
    age_groups = list(age_groups)
    # Convert ObjectId to string for JSON serialization
    for age_group in age_groups:
        age_group["_id"] = str(age_group["_id"])
    return {"age_groups": age_groups}


@app.post("/age-groups")
def create_age_group(age_group: AgeGroup):
    ageGroupCollection.insert_one(age_group.model_dump())
    return age_group


@app.put("/age-groups/{age_group_id}")
def update_age_group(age_group_id: str, age_group: AgeGroup):
    try:
        # Convert string to ObjectId for MongoDB query
        object_id = ObjectId(age_group_id)
        result = ageGroupCollection.update_one(
            {"_id": object_id}, {"$set": age_group.model_dump()}
        )
        return {
            "modified_count": result.modified_count,
            "matched_count": result.matched_count,
        }
    except Exception as e:
        return HTTPException(status_code=400, detail=f"Invalid ID format: {str(e)}")


@app.delete("/enroll/{enroll_id}")
def delete_enroll(enroll_id: str):
    try:
        # Convert string to ObjectId for MongoDB query
        object_id = ObjectId(enroll_id)
        result = enrollCollection.delete_one({"_id": object_id})
        print(f"\n\n\n======================================\n{ageGroupCollection.find()}\n\n\n")
        if result.deleted_count == 1:
            return {"message": "Enroll deleted successfully"}
        return {"error": "Enroll not found"}, 404
    except Exception as e:
        return {"error": f"Invalid ID format: {str(e)}"}, 400


@app.delete("/age-groups/{age_group_id}")
def delete_age_group(age_group_id: str):
    try:
        # Convert string to ObjectId for MongoDB query
        object_id = ObjectId(age_group_id)
        result = ageGroupCollection.delete_one({"_id": object_id})
        if result.deleted_count == 1:
            return {"message": "Age group deleted successfully"}
        return {"error": "Age group not found"}, 404
    except Exception as e:
        return {"error": f"Invalid ID format: {str(e)}"}, 400
