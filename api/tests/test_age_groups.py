from bson import ObjectId


def _login(client):
    r = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert r.status_code == 200
    return r.json()["token"]


def test_list_age_groups_initially_empty(client):
    resp = client.get("/age-groups")
    assert resp.status_code == 200
    assert resp.json() == {"age_groups": []}


def test_create_and_list_age_groups(client):
    token = _login(client)
    payload = {"min_age": 0, "max_age": 17, "description": "Kids"}
    resp = client.post("/age-groups", json=payload, headers={"X-Token": token})
    assert resp.status_code == 200
    assert resp.json() == payload

    resp2 = client.get("/age-groups")
    data = resp2.json()
    assert resp2.status_code == 200
    assert "age_groups" in data
    assert len(data["age_groups"]) == 1
    assert data["age_groups"][0]["description"] == "Kids"
    assert isinstance(data["age_groups"][0]["_id"], str)


def test_update_and_delete_age_group(client):
    token = _login(client)
    # create
    payload = {"min_age": 18, "max_age": 30, "description": "Young"}
    created = client.post("/age-groups", json=payload, headers={"X-Token": token})
    assert created.status_code == 200

    # find id by listing
    listed = client.get("/age-groups").json()["age_groups"]
    _id = listed[0]["_id"]

    # update
    update_payload = {"min_age": 18, "max_age": 35, "description": "Young+"}
    upd = client.put(f"/age-groups/{_id}", json=update_payload, headers={"X-Token": token})
    assert upd.status_code == 200
    assert upd.json()["matched_count"] == 1
    assert upd.json()["modified_count"] == 1

    # delete
    dele = client.delete(f"/age-groups/{_id}", headers={"X-Token": token})
    assert dele.status_code == 200
    assert dele.json() == {"message": "Age group deleted successfully"}
