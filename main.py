from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import ipaddress

app = FastAPI()

def _is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except Exception:
        return False

def get_client_ip(request: Request) -> str:
    """
    Priority:
      1. X-Forwarded-For (first entry)
      2. X-Real-IP
      3. request.client.host (FastAPI/TestClient fills this)
    """
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        # could be comma-separated list; take first
        ip = xff.split(",")[0].strip()
        if _is_valid_ip(ip):
            return ip

    xri = request.headers.get("X-Real-IP") or request.headers.get("X-Real-Ip")
    if xri and _is_valid_ip(xri):
        return xri

    client = request.client
    if client and _is_valid_ip(client.host):
        return client.host

    return ""

@app.get("/ipconfig")
async def ipconfig(request: Request):
    ip = get_client_ip(request)
    if not ip:
        return JSONResponse(status_code=400, content={"error": "could not determine client IP"})
    return JSONResponse(content={"ip": ip})

@app.get("/healthz")
async def healthz():
    return JSONResponse(content={"status": "ok"})
