#!/bin/bash 

Installpip(){
    echo "[+] Installing pip"
    python -m pip install --upgrade pip
    echo "[+] Installing requirements"
    pip install -r requirements.txt
}

echo "[+] Creating directories"
mkdir -p {RunnerLogs,logs,repo}
if which python3 >> /dev/null
then
    Installpip
else
    echo "[+] Installing python3"
    sudo apt install python3 -y
    Installpip
fi
echo "[+] Installation process completed."
