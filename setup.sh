#!/bin/bash

Installpip(){
    echo "[+] Installing pip3"
    chk=`whoami`
    if [ "$chk" == "root" ]
    then
        apt install python3-pip -y
    else
        sudo apt install python3-pip -y
    fi
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
    chk=`whoami`
    if [ "$chk" == "root" ]
    then
        apt install python3 -y
    else
        sudo apt install python3 -y
    fi
    Installpip
fi
echo "[+] Installation process completed."
