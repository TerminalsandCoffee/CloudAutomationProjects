@echo off
set fdate=%date:~-4,4%%date:~-7,2%%date:~-10,2%
set ftime=%time:~-0,2%%time:~-8,2%%time:~-5,2%
set folder=C:\Documents\LogsSDF-%fdate%-%ftime%
echo .
echo creating folder:  %folder%
echo %folder%
echo .
MKDIR "%folder%"

echo .
echo . .
cd C:\windows\system32
echo creating backup of Brink Logs
wevtutil epl Brink "%folder%\Brink-%fdate%.evtx"
echo .
echo creating backup of Application Logs
wevtutil epl Application "%folder%\Application-%fdate%.evtx"
echo .
echo creating backup of System Logs
wevtutil epl System "%folder%\System-%fdate%.evtx"
echo .
cd \
echo creating backing up of current SDF file
COPY C:\Brink\POS\Register.sdf "%folder%\Register-%fdate%.sdf"
echo .
echo Zipping up Logs and SDF file
echo .
echo .
echo Set objArgs = WScript.Arguments > _zipIt.vbs
echo InputFolder = objArgs(0) >> _zipIt.vbs
echo ZipFile = objArgs(1) >> _zipIt.vbs
echo CreateObject("Scripting.FileSystemObject").CreateTextFile(ZipFile, True).Write "PK" ^& Chr(5) ^& Chr(6) ^& String(18, vbNullChar) >> _zipIt.vbs
echo Set objShell = CreateObject("Shell.Application") >> _zipIt.vbs
echo Set source = objShell.NameSpace(InputFolder).Items >> _zipIt.vbs
echo objShell.NameSpace(ZipFile).CopyHere(source) >> _zipIt.vbs
echo wScript.Sleep 2000 >> _zipIt.vbs
echo .
echo zipit!
echo .
CScript  _zipIt.vbs  %folder%  %folder%.zip
echo .
echo zip is done!
echo .
echo move zip file
COPY "%folder%.zip" "%folder%"
DEL "%folder%.zip"
DEL _zipIt.vbs
echo .
echo .
echo creating backup of Brink POS Backup folder
XCOPY /E /I "C:\Brink\POS\Backup" "%folder%\Backup-%fdate%"
echo .
echo . .
echo . . .
echo done!
