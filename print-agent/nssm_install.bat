@echo off
REM sphotel Print Agent — Windows Service installer using NSSM
REM Run as Administrator

SET AGENT_DIR=%~dp0
SET NSSM=%AGENT_DIR%nssm.exe

echo Installing sphotel Print Agent as Windows Service...

%NSSM% install SpHotelPrintAgent "%AGENT_DIR%launcher.exe"
%NSSM% set SpHotelPrintAgent AppDirectory "%AGENT_DIR%"
%NSSM% set SpHotelPrintAgent DisplayName "sphotel Print Agent"
%NSSM% set SpHotelPrintAgent Description "Receives print jobs from sphotel cloud and sends to thermal printer"
%NSSM% set SpHotelPrintAgent Start SERVICE_AUTO_START
%NSSM% set SpHotelPrintAgent AppRestartDelay 5000
%NSSM% set SpHotelPrintAgent AppStdout "%AGENT_DIR%logs\agent.log"
%NSSM% set SpHotelPrintAgent AppStderr "%AGENT_DIR%logs\agent.log"
%NSSM% set SpHotelPrintAgent AppRotateFiles 1
%NSSM% set SpHotelPrintAgent AppRotateOnline 1
%NSSM% set SpHotelPrintAgent AppRotateSeconds 86400

mkdir "%AGENT_DIR%logs" 2>nul

%NSSM% start SpHotelPrintAgent

echo.
echo Done! Service "SpHotelPrintAgent" installed and started.
echo Log file: %AGENT_DIR%logs\agent.log
echo.
echo To uninstall: nssm remove SpHotelPrintAgent confirm
pause
