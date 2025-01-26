"""
#This is using pythong


import os

for filename in os.listdir('.'):
    if filename.endswith('.sdf'):
        newname = filename.replace('.sdf', '_new.sdf')
        os.rename(filename, newname)
        
import os

for filename in os.listdir('.'):
    if filename.endswith('.sdf'):
        newname = filename[:-4] + '_old.sdf'
        os.rename(filename, newname)
       
        
"""


#batch

@echo off
setlocal enabledelayedexpansion
for %%f in (*.sdf) do (
  set "filename=%%~nf"
  ren "%%f" "!filename!_new.sdf"
)


#cmd
ren oldname.sdf newname.sdf
