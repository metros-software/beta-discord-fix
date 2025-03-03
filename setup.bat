@echo off
pip install -r requirements.txt
pyinstaller -y -w -F --uac-admin --icon=.web\icons\icon.ico discord-fix.py
pause>nul