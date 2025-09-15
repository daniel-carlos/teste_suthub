def _seed_age_groups(client):
    client.post("/age-groups", json={"min_age": 0, "max_age": 12, "description": "child"})
    client.post("/age-groups", json={"min_age": 13, "max_age": 17, "description": "teen"})
    client.post("/age-groups", json={"min_age": 18, "max_age": 64, "description": "adult"})


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"Hello": "World"}


def test_create_enroll_and_list(client):
    _seed_age_groups(client)

    payload = {"name": "Ana", "cpf": "12345678900", "age": 20}
    resp = client.post("/enroll", json=payload)
    assert resp.status_code == 200
    assert "id" in resp.json()

    list_resp = client.get("/enroll")
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert "enrolls" in data
    assert len(data["enrolls"]) == 1
    e = data["enrolls"][0]
    assert e["name"] == "Ana"
    assert e["status"] == "pending"
    print(f"\n\n\n{e}\n\n\n")
    assert e["age_group"]["description"] == "adult"


def test_get_update_delete_enroll(client):
    _seed_age_groups(client)
    payload = {"name": "Bob", "cpf": "98765432100", "age": 15}
    created = client.post("/enroll", json=payload).json()
    _id = created["id"]

    # get
    g = client.get(f"/enroll/{_id}")
    assert g.status_code == 200
    assert g.json()["enroll"]["name"] == "Bob"

    # update (change age only)
    upd = client.put(f"/enroll/{_id}", json={"age": 16})
    assert upd.status_code == 200
    assert upd.json()["matched_count"] == 1
    assert upd.json()["modified_count"] == 1

    # delete
    dele = client.delete(f"/enroll/{_id}")
    assert dele.status_code == 200
    assert dele.json() == {"message": "Enroll deleted successfully"}
