@echo off
title Standalone MySQL/MariaDB Server
echo Starting standalone MySQL database server on port 3306...
"%~dp0mariadb_server\bin\mysqld.exe" --console
pause
