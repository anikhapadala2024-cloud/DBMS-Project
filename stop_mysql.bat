@echo off
title Stop MySQL/MariaDB Server
echo Shutting down MySQL server...
"%~dp0mariadb_server\bin\mysqladmin.exe" -u root shutdown
echo Done.
pause
