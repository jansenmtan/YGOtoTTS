#!/usr/bin/env bash
python3 -m pip install pyinstaller
python3 -m pip install -r "requirements.txt"
python3 -OO -m PyInstaller -F -n "YGOtoTTS-$(uname -s)" "./YGOtoTTS/core.py"