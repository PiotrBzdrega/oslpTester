### **Setup virtual environment**
```shell
wsl --version
    WSL version: 2.4.12.0
    Kernel version: 5.15.167.4-1
    WSLg version: 1.0.65
    MSRDC version: 1.2.5716
    Direct3D version: 1.611.1-81528511
    DXCore version: 10.0.26100.1-240331-1435.ge-release
    Windows version: 10.0.22621.4037

python3 --version
    Python 3.12.3

git clone ${this repo}
cd ${repodir}
sudo apt update
sudo apt install python3-tk
sudo apt install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
pip3 install protobuf==5.29.3
pip3 install cryptography
```
### vscode
```text
To run from vscode, make sure that virtual environment is used as interpreter:
CTRL+SHIFT+P 
Python:Select Interpreter
```


### connect to server
```shell
nc -v localhost 12123
```


### deactivate virtual environment
```shell
deactivate
```