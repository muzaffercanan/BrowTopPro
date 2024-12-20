import asyncio
import json
import pathlib
import ssl
import psutil
import base64
import platform
import subprocess
from aiohttp import web
import time
import struct

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
    log_path = "/var/log/syslog"  # Correctly mapped from the host
    try:
        with open(log_path, "r") as file:
            logs = file.readlines()[-50:]  # Last 50 lines
            return logs if logs else ["No logs available"]
    except FileNotFoundError:
        return ["System log file not found!"]
    except PermissionError:
        return ["Permission denied while reading system logs."]
    except Exception as e:
        return [f"Error reading system logs: {e}"]


# Fetch logged-in users using psutil
def get_logged_users():
    try:
        users = psutil.users()
        if not users:
            return ["No logged-in users"]
        
        # Format the logged-in user information
        formatted_users = [
            f"User: {user.name}, Terminal: {user.terminal}, Host: {user.host}, Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user.started))}, PID: {user.pid}"
            for user in users
        ]
        return formatted_users
    except Exception as e:
        return [f"Error fetching logged-in users: {e}"]


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
            process_list.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    sorted_processes = sorted(process_list, key=lambda x: x.get(sort_by, 0), reverse=True)
    try:
        disk_info = psutil.disk_usage("/")
    except Exception as e:
        disk_info = {"error": f"Disk usage fetch failed: {e}"}

    stats = {
    "cpu": psutil.cpu_percent(interval=1),
    "memory": psutil.virtual_memory()._asdict(),
    "disk": disk_info if isinstance(disk_info, dict) else disk_info._asdict(),
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

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.text:
                req = json.loads(msg.data)
                action = req.get("action", "stats")
                sort_by = req.get("sort", "cpu")

                if action == "stats":
                    data = await get_system_stats(sort_by)
                    await ws.send_str(json.dumps(["stats", data]))
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("WebSocket connection closed.")
    return ws

# Serve the monitor page
async def monitor(request):
    path = pathlib.Path(__file__).parent.joinpath("monitor.html")
    if not path.exists():
        print(f"Monitor file not found at: {path}")
        return web.Response(status=404, text="Monitor file not found.")
    return web.FileResponse(path)

# SSL Configuration
def create_ssl_context():
    cert_file = pathlib.Path(__file__).parents[1].joinpath("cert/localhost.crt")
    key_file = pathlib.Path(__file__).parents[1].joinpath("cert/localhost.key")
    try:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert_file, key_file)
        return ssl_context
    except Exception as e:
        print(f"Error loading SSL certificates: {e}")
        raise

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

