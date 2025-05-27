@echo off
setlocal
set DIR=%~dp0
java -jar "%DIR%\.mvn\wrapper\maven-wrapper.jar" %*
