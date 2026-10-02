#!/usr/bin/env python3
"""
AgriTech – Crop Batch Management & Analytics Portal
Unified Application Runner
"""

import sys
import os
import time
import socket
import threading
import webbrowser
import subprocess
from pathlib import Path

# Add current directory to Python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0

def start_embedded_mysql_if_needed():
    """Ensure a MySQL/MariaDB server is running on localhost:3306."""
    if is_port_in_use(3306):
        print(" [OK] MySQL Database Server is running on port 3306.")
        return None

    mariadb_exe = ROOT_DIR / "mariadb_server" / "bin" / "mysqld.exe"
    if mariadb_exe.exists():
        print(" [INFO] Starting standalone MySQL/MariaDB engine on port 3306...")
        proc = subprocess.Popen(
            [str(mariadb_exe), "--console"],
            cwd=str(ROOT_DIR / "mariadb_server"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        for _ in range(12):
            time.sleep(0.5)
            if is_port_in_use(3306):
                print(" [OK] MySQL Server started successfully on port 3306.")
                return proc
        print(" [INFO] Proceeding with database connection.")
        return proc
    else:
        print(" [INFO] Standalone MySQL folder not found. Attempting configured host.")
        return None

def open_browser_delayed(url: str, delay: float = 1.5):
    """Open default web browser after server starts."""
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
        except Exception:
            pass
    t = threading.Thread(target=_open, daemon=True)
    t.start()

def main():
    print("=" * 70)
    print("  AGRITECH - CROP BATCH MANAGEMENT & ANALYTICS PORTAL")
    print("=" * 70)

    # 1. Database Check
    start_embedded_mysql_if_needed()

    # 2. Start Flask Application
    from backend.app import create_app
    app = create_app()

    port = int(os.getenv("PORT", 5000))
    portal_url = f"http://127.0.0.1:{port}/login.html"
    db_engine = app.config.get("ACTIVE_DB_ENGINE", "mysql")

    print("-" * 70)
    print(f" * Portal URL:        {portal_url}")
    print(f" * REST API Base:     http://127.0.0.1:{port}/api")
    print(f" * Database Engine:   {db_engine.upper()} (agritech_db on port 3306)")
    print("-" * 70)
    print(" DEFAULT CREDENTIALS FOR TESTING & VIVA:")
    print("  [ADMIN]  Email: admin@agritech.com          Password: Admin@123")
    print("  [FARMER] Email: farmer.ramesh@agritech.com   Password: Farmer@123")
    print("=" * 70)
    print(f" Opening web app in your browser: {portal_url}")

    # Launch browser automatically
    open_browser_delayed(portal_url, delay=1.5)

    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
