# from paramiko import SSHClient, AutoAddPolicy
# from paramiko.channel import Channel
# import time
from fabric import Connection
from invoke import Responder

def connect():
    # Establish SSH connection
    conn = Connection(
        host="ip",  # or IP address
        user="user",
        connect_kwargs={
            "password": "password",  # or use SSH key
            # "key_filename": "/path/to/private_key.pem",
        },
    )
    
    # Set up a responder for the su password prompt
    su_pass = Responder(
        pattern=r"Password:",  # Regex to match the prompt
        response="password\n",  # Response + newline
    )

    # Run su with automated password input
    result = conn.run(
        "su -c 'date -s \"2024-05-20 12:00:00\"'",
        pty=True,
        watchers=[su_pass],  # Now it works!
        hide=True, # No stdout/stderr printed
        warn=True # Prevents exception
    )
    
    if result.failed:
        print(f"Failed! STDERR: {result.stdout}")
    else:
        print(f"Success! STDOUT: {result.stdout}")


# def connect2():
#     client = SSHClient()
#     #client.load_system_host_keys()
#     #client.load_host_keys('~/.ssh/known_hosts')
    
#     client.set_missing_host_key_policy(AutoAddPolicy())
#     client.connect('172.20.73.44', username='administrator', password='admin')
#     _stdin, _stdout,_stderr = client.exec_command("df")
#     print(_stdout.read().decode())
    
    
    
#     """ DOES NOT WORK """
#     # cmd = "su -c 'date -s '2025-07-25 20:59:55''"
#     # # cmd = 'sudo su -c "date -s \\"2025-07-25 20:59:55\\""'
#     # # cmd ="su"
#     # # cmd ='su -c "whoami" root'
#     # # cmd ="su -l root"
#     # stdin, _stdout,_stderr = client.exec_command(command=cmd, get_pty=True)
    
#     # # print(_stdout.read().decode())
#     # # print(_stderr.read().decode())
#     # # time.sleep(1)
#     # # exit()
#     # stdin.write("syndis" + '\n')
#     # stdin.flush()
#     # # time.sleep(1)
#     # # print(_stderr.read().decode())

#     # # _stdin, _stdout,_stderr = client.exec_command("whoami")
#     # # print(_stdout.read().decode())
    
#     # # _stdin, _stdout,_stderr = client.exec_command("date -s \"2025-07-25 20:59:55\"")
#     # # print(_stderr.read().decode())
    
#     # _stdin, _stdout,_stderr = client.exec_command("date")
#     # print(_stdout.read().decode())
#     """  """
    
#     """ WORKS """
#     channel:Channel = client.invoke_shell()
#     print(type(channel))
#     channel_data = str()
    
#     while channel.recv_ready():
#         time.sleep(0.5)
#         continue
    
#     channel.send("su\n")
#     time.sleep(1)
#     print(str(channel.recv(999)))
#     time.sleep(1)
#     channel.send("syndis\n")
#     print(str(channel.recv(999)))
#     time.sleep(1)
#     channel.send("date -s \"2025-07-25 20:59:55\""+"\n")
#     print(str(channel.recv(999)))  
#     """  """
    
#     client.close()