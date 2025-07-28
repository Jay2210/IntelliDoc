import uuid
from app.s3_storage import save_json, load_json

def test_s3_roundtrip(monkeypatch):
    key = f"test/{uuid.uuid4().hex}.json"
    data = {"foo": "bar"}
    # monkeypatch bucket to use a dict...
    save_json(key, data)
    loaded = load_json(key)
    assert loaded == data
