import importlib
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path

import mongomock
import pymongo
import pytest
from fastapi.testclient import TestClient

# adiciona a raiz do repo ao sys.path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# patcha o pymongo para usar mongomock ANTES de importar a app
pymongo.MongoClient = mongomock.MongoClient  # type: ignore[attr-defined]

# importe sua FastAPI app
from api.run import app  # ajuste se a app estiver em outro módulo


@dataclass
class _InsertOneResult:
    inserted_id: Any


@dataclass
class _UpdateResult:
    matched_count: int
    modified_count: int


@dataclass
class _DeleteResult:
    deleted_count: int


class FakeCollection:
    def __init__(self):
        self.docs: List[Dict[str, Any]] = []

    def _match_filter(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        if not query:
            return True
        # Support by _id equality
        if "_id" in query:
            return doc.get("_id") == query["_id"]
        # Support age group lookup: {min_age: {"$lte": X}, max_age: {"$gte": X}}
        if "min_age" in query and isinstance(query["min_age"], dict) and "$lte" in query["min_age"]:
            age = query["min_age"]["$lte"]
            return doc.get("min_age") <= age <= doc.get("max_age")
        return False

    def find_one(self, query: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        for d in self.docs:
            if self._match_filter(d, query or {}):
                return d
        return None

    def find(self, query: Optional[Dict[str, Any]] = None):
        if not query:
            return iter(self.docs)
        return iter([d for d in self.docs if self._match_filter(d, query)])

    def insert_one(self, document: Dict[str, Any]):
        if "_id" not in document:
            document["_id"] = ObjectId()
        # Deep copy isn't necessary for these simple tests
        self.docs.append(document)
        return _InsertOneResult(inserted_id=document["_id"])

    def update_one(self, filter: Dict[str, Any], update: Dict[str, Any]):
        matched = 0
        modified = 0
        for d in self.docs:
            if self._match_filter(d, filter):
                matched += 1
                if "$set" in update:
                    d.update(update["$set"])
                modified += 1
                break
        return _UpdateResult(matched_count=matched, modified_count=modified)

    def delete_one(self, filter: Dict[str, Any]):
        for i, d in enumerate(self.docs):
            if self._match_filter(d, filter):
                del self.docs[i]
                return _DeleteResult(deleted_count=1)
        return _DeleteResult(deleted_count=0)


class FakeDB:
    def __init__(self):
        self._collections: Dict[str, FakeCollection] = {
            "enrollCollection": FakeCollection(),
            "ageGroupCollection": FakeCollection(),
            "messageCollection": FakeCollection(),
        }

    def __getitem__(self, name: str) -> FakeCollection:
        if name not in self._collections:
            self._collections[name] = FakeCollection()
        return self._collections[name]


class FakeMongoClient:
    def __init__(self, *_: Any, **__: Any):
        self._dbs: Dict[str, FakeDB] = {}

    def __getitem__(self, name: str) -> FakeDB:
        if name not in self._dbs:
            self._dbs[name] = FakeDB()
        return self._dbs[name]


@pytest.fixture
def app_module(monkeypatch):
    # Patch pymongo.MongoClient before importing the app module
    monkeypatch.setattr(pymongo, "MongoClient", FakeMongoClient)
    module = importlib.import_module("api.run")
    # Ensure a fresh import each time to reset in-memory DB
    module = importlib.reload(module)
    return module


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
