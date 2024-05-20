from fastapi import FastAPI, Response
from fastapi.testclient import TestClient
app = FastAPI()

client = TestClient(app)
response = client.get("/api/test/")
print(response.json())
