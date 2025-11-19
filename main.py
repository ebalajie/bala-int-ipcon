from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import ipaddress

app = FastAPI(
    title="IP Config Service",
    version="1.0.0",
    description="Returns the real client IP address (works behind AWS NLB with Proxy Protocol).",
)


def _is_valid_ip(ip: str) -> bool:
    """Validate IPv4/IPv6."""
    try:
        ipaddress.ip_address(ip)
        return True
    except Exception:
        return False


def get_client_ip(request: Request) -> str:
    """
    Extract real client IP behind Load Balancers.

    Priority:
    1. X-Forwarded-For (first IP)
    2. X-Real-IP
    3. request.client.host (fallback)
    """

    # X-Forwarded-For: "203.0.113.10, 10.0.0.1"
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        first_ip = xff.split(",")[0].strip()
        if _is_valid_ip(first_ip):
            return first_ip

    # X-Real-IP
    xri = request.headers.get("X-Real-IP") or request.headers.get("X-Real-Ip")
    if xri and _is_valid_ip(xri):
        return xri

    # Fallback
    client = request.client
    if client and _is_valid_ip(client.host):
        return client.host

    return ""


@app.get("/ipconfig")
async def ipconfig(request: Request):
    """Return the real client IP"""
    ip = get_client_ip(request)
    if not ip:
        return JSONResponse(
            status_code=400,
            content={"error": "could not determine client IP"},
        )
    return JSONResponse(content={"ip": ip})


@app.get("/healthz")
async def healthz():
    """Liveness/Readiness endpoint"""
    return {"status": "ok"}


# Notes:
# When running under Kubernetes with NLB + Proxy Protocol,
# use this Uvicorn command:
#
# uvicorn main:app --host 0.0.0.0 --port 8000 --proxy-headers
#
# (Helm chart already uses this)
