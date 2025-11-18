from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_x_forwarded_for():
    resp = client.get("/ipconfig", headers={"X-Forwarded-For": "203.0.113.45, 198.51.100.17"})
    assert resp.status_code == 200
    assert resp.json()["ip"] == "203.0.113.45"

def test_x_real_ip():
    resp = client.get("/ipconfig", headers={"X-Real-IP": "198.51.100.99"})
    assert resp.status_code == 200
    assert resp.json()["ip"] == "198.51.100.99"

def test_remote_addr():
    # TestClient sets client.host to 127.0.0.1
    resp = client.get("/ipconfig")
    assert resp.status_code == 200
    ip = resp.json()["ip"]
    assert ip in ("127.0.0.1", "::1")  # Accept IPv4 or IPv6 localhost

def test_bad_request_when_no_ip():
    # craft a request with invalid headers and invalid client host by mocking
    # We simulate an invalid X-Forwarded-For and X-Real-IP; TestClient will still have client.host valid
    # For real negative test, call handler directly:
    from fastapi import Request
    from starlette.datastructures import Address
    scope = {"type": "http", "method": "GET", "path": "/ipconfig", "headers": []}
    # create a Request with no client info (edge case)
    req = Request(scope)
    # call get_client_ip directly
    from main import get_client_ip
    assert get_client_ip(req) == ""
