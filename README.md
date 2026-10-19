### **Setup virtual environment**
```shell
git clone https://github.com/PiotrBzdrega/oslpTester
cd oslpTester
sudo apt update
sudo apt install python3-tk
sudo apt install python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
pip3 install protobuf==6.31.1
pip3 install cryptography
pip3 install paramiko
pip3 install fabric
# generate protobuf contract
protoc --python_out=. oslp.proto

#make directory keys and certs in oslpTester/
mkdir keys certs

### start app
$ ./.venv/bin/python3 main.py

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

## WINDOWS
```shell
install python (make sure tkinter is already there)
git clone https://github.com/PiotrBzdrega/oslpTester.git
cd oslpTester
### create virtual env
.venv\Scripts\activate
pip3 install protobuf==6.31.1
pip3 install cryptography
pip3 install paramiko
pip3 install fabric

### start app
.venv\Scripts\python.exe main.py
```

### TODO:
* animation that server is running
* use logger instead print or merged solution to avoid 