from fastapi.testclient import TestClient

from app.main import app


def main():
    client = TestClient(app)
    health = client.get("/")
    assert health.status_code == 200
    assert health.json() == {"status": "running", "service": "Think9 Brain"}

    invalid = client.post("/verify", json={})
    assert invalid.status_code == 422
    print("API health and request validation PASSED")


if __name__ == "__main__":
    main()
