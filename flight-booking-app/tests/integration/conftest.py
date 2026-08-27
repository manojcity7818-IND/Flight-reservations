import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[2]
PORTS = {
    "flight": 18001,
    "booking": 18002,
    "payment": 18003,
    "notification": 18004,
    "user": 18005,
    "gateway": 18080,
}
SERVICE_DIRS = {
    "flight": "flight-search-service",
    "booking": "booking-service",
    "payment": "payment-service",
    "notification": "notification-service",
    "user": "user-service",
    "gateway": "api-gateway",
}


def _port_open(port: int) -> bool:
    with socket.socket() as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


@pytest.fixture(scope="session")
def stack():
    env = os.environ.copy()
    env["FLIGHT_SEARCH_URL"] = f"http://127.0.0.1:{PORTS['flight']}"
    env["BOOKING_SERVICE_URL"] = f"http://127.0.0.1:{PORTS['booking']}"
    env["PAYMENT_SERVICE_URL"] = f"http://127.0.0.1:{PORTS['payment']}"
    env["NOTIFICATION_SERVICE_URL"] = f"http://127.0.0.1:{PORTS['notification']}"
    env["USER_SERVICE_URL"] = f"http://127.0.0.1:{PORTS['user']}"

    processes = []
    for name, port in PORTS.items():
        if _port_open(port):
            continue
        cwd = ROOT / "services" / SERVICE_DIRS[name]
        processes.append(
            subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
                cwd=cwd,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        )
    try:
        for _ in range(80):
            try:
                if all(
                    httpx.get(f"http://127.0.0.1:{port}/health", timeout=0.2).status_code == 200
                    for port in PORTS.values()
                ):
                    break
            except Exception:
                time.sleep(0.1)
        else:
            pytest.fail("Services did not start")
        yield f"http://127.0.0.1:{PORTS['gateway']}"
    finally:
        for proc in processes:
            proc.terminate()
            proc.wait(timeout=5)
