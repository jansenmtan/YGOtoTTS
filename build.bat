@echo off
python -m pip install pyinstaller
python -m pip install -r "./requirements.txt"
python -OO -m PyInstaller -F -n "YGOtoTTS-win32" "./YGOtoTTS/__main__.py"
