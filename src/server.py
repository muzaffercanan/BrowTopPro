import asyncio
import json
import pathlib
import ssl
import psutil
import base64
import platform
import subprocess
from datetime import timedelta
from aiohttp import web
import time

# Username and Password
USERNAME = "admin"
PASSWORD = "password"

# Middleware: HTTP Basic Authentication
async def auth_middleware(app, handler):
    async def middleware_handler(request):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Basic "):
            return web.Response(status=401, headers={"WWW-Authenticate": 'Basic realm="Secure Area"'})
        
        auth_decoded = base64.b64decode(auth_header.split(" ")[1]).decode("utf-8")
        user, pwd = auth_decoded.split(":")
        if user != USERNAME or pwd != PASSWORD:
            return web.Response(status=401, text="Unauthorized")
        return await handler(request)
    return middleware_handler

# Fetch system logs
def get_system_logs():
    if platform.system() == "Windows":
        try:
            logs = subprocess.check_output("wevtutil qe System /c:50 /f:text", shell=True, text=True).strip()
            return logs.splitlines() if logs else ["No logs available"]
        except Exception as e:
            return [f"Error fetching Windows logs: {e}"]
    else:
        try:
            with open("/var/log/syslog", "r") as file:
                return file.readlines()[-50:]
        except FileNotFoundError:
            return ["System log file not found"]


# Fetch logged-in users
def get_logged_users():
    if platform.system() == "Windows":
        try:
            logged_users = subprocess.check_output("query user", shell=True, text=True).strip()
            return logged_users.splitlines() if logged_users else ["No logged-in users"]
        except Exception as e:
            return [f"Error fetching logged-in users: {e}"]
    else:
        return subprocess.getoutput("who").splitlines()


# Get system uptime
def get_uptime():
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)
    uptime_hours, remainder = divmod(uptime_seconds, 3600)
    uptime_minutes, _ = divmod(remainder, 60)
    return f"{uptime_hours} hours, {uptime_minutes} minutes"


# Collect system stats
async def get_system_stats(sort_by="cpu"):
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            # Safely append process information
            process_list.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Ignore processes that raise these exceptions
            continue

    # Sort the processes based on the selected field (default: CPU)
    sorted_processes = sorted(
        process_list, key=lambda x: x.get(sort_by, 0), reverse=True
    )

    stats = {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage("C:\\" if platform.system() == "Windows" else "/")._asdict(),
        "load_avg": "Not supported on Windows" if platform.system() == "Windows" else psutil.getloadavg(),
        "processes": sorted_processes,
        "uptime": get_uptime(),
        "logged_users": get_logged_users(),
        "logs": get_system_logs()
    }
    return stats



# WebSocket Endpoint for real-time stats
async def send_stats(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.text:
            req = json.loads(msg.data)
            action = req.get("action", "stats")
            sort_by = req.get("sort", "cpu")

            if action == "stats":
                data = await get_system_stats(sort_by)
                await ws.send_str(json.dumps(["stats", data]))
        elif msg.type == web.WSMsgType.close:
            break

    return ws

# Serve the monitor page
async def monitor(request):
    path = pathlib.Path(__file__).parents[0].joinpath("monitor.html")
    return web.FileResponse(path)

# SSL Configuration
def create_ssl_context():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    cert_file = pathlib.Path(__file__).parents[1].joinpath("cert/localhost.crt")
    key_file = pathlib.Path(__file__).parents[1].joinpath("cert/localhost.key")
    ssl_context.load_cert_chain(cert_file, key_file)
    return ssl_context

# Start the server
def run():
    ssl_context = create_ssl_context()
    app = web.Application(middlewares=[auth_middleware])
    app.add_routes([
        web.get("/ws", send_stats),
        web.get("/monitor", monitor),
    ])
    print("Server is running at https://localhost:8765")
    web.run_app(app, port=8765, ssl_context=ssl_context)

if __name__ == "__main__":
    print("Starting the server...")
    run()
