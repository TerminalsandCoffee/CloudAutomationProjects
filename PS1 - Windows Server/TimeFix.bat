@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION

:: ADD SYSTEM32 TO PATH
SET "PATH=%PATH%;C:\windows\system32"

(
:: QUERY TIME SERVICE STATUS
sc query w32time >CON:

:: SET SERVICE TO AUTOMATIC (IN THE CASE ITS DISABLED OR MANUAL)
sc config w32time start=auto

:: Restart time service
net stop w32time
net start w32time

:: Configure new time servers (0x8 sets to use Min/Max polling time intervals and adjust if time is accurate or not)
w32tm /config /manualpeerlist:"time.windows.com,0x8" /syncfromflags:manual /update

:: Set new SpecialPollingInterval as a precaution
reg add HKLM\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpClient /v SpecialPollInterval /t reg_dword /d 3600 /f

:: Make Windows Time Service start/stop based on network activity
sc triggerinfo w32time delete
sc triggerinfo w32time start/networkon stop/networkoff

:: Resync time
SET "BEFORE_SYNC=%TIME: =0%"
w32tm /config /update
w32tm /resync /rediscover
SET "AFTER_SYNC=%TIME: =0%"

:: Get Time Difference
set "end=!AFTER_SYNC:%time:~8,1%=%%100)*100+1!"  &  set "start=!BEFORE_SYNC:%time:~8,1%=%%100)*100+1!"
set /A "elapsed=((((10!end:%time:~2,1%=%%100)*60+1!%%100)-((((10!start:%time:~2,1%=%%100)*60+1!%%100)"

echo. >CON:
echo -- TIMES -- >CON:
echo BEFORE SYNC: %BEFORE_SYNC% >CON:
echo AFTER  SYNC: %AFTER_SYNC% >CON:
echo DIFFERENCE: %elapsed% SECONDS >CON:
) > timefix-%DATE:~10,4%_%DATE:~4,2%_%DATE:~7,2%%TIME:~0,2%_%TIME:~3,2%_%TIME:~6,2%.log
:: Self-destruct
:: (goto) 2>nul & del "%~f0"
