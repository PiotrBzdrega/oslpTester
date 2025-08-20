# from paramiko import SSHClient, AutoAddPolicy
# from paramiko.channel import Channel
# import time
from fabric import Connection
from invoke import Responder
import logging

# ="2024-05-20 12:00:00"

def connect_root(ssh_user :str, user_password :str, root_password :str, ip :str, cmd :str):
    logging.getLogger('paramiko').setLevel(logging.WARNING)
    logging.getLogger('invoke').setLevel(logging.WARNING)
    logging.getLogger('fabric').setLevel(logging.WARNING)
    
    logging.getLogger('paramiko.transport').setLevel(logging.WARNING)
    logging.getLogger('paramiko.client').setLevel(logging.WARNING)
    # Establish SSH connection
    conn = Connection(
        host=ip,  # or IP address
        user=ssh_user,
        connect_kwargs={
            "password": user_password,  # or use SSH key
            # "key_filename": "/path/to/private_key.pem",
        },
    )
    
    # Set up a responder for the su password prompt
    su_pass = Responder(
        pattern=r"Password:",  # Regex to match the prompt
        response=f"{root_password}\n",  # Response + newline
    )

    # Run su with automated password input
    result = conn.run(
        # "podman image inspect localhost/futex-investigation --format '{{index .RepoTags 0}}'",
        cmd,
        pty=True,
        watchers=[su_pass],  # Now it works!
        hide=True, # No stdout/stderr printed
        warn=True # Prevents exception
    )
    
    if result.failed:
        print(f"Failed! STDERR: {result.stdout}")
    # else:
    #     print(f"Success! STDOUT: {result.stdout}")

def connect(ssh_user :str, user_password :str, ip :str, cmd :str):
    logging.getLogger('paramiko').setLevel(logging.WARNING)
    logging.getLogger('invoke').setLevel(logging.WARNING)
    logging.getLogger('fabric').setLevel(logging.WARNING)
    
    logging.getLogger('paramiko.transport').setLevel(logging.WARNING)
    logging.getLogger('paramiko.client').setLevel(logging.WARNING)
    # Establish SSH connection
    conn = Connection(
        host=ip,  # or IP address
        user=ssh_user,
        connect_kwargs={
            "password": user_password,  # or use SSH key
            # "key_filename": "/path/to/private_key.pem",
        },
    )
    
    result = conn.run(cmd,
        hide=True, # No stdout/stderr printed
        warn=True # Prevents exception
    )
    
    if result.failed:
        print(f"Failed! STDERR: {result.stdout}")
    else:
        # print(f"Success! STDOUT: {result.stdout}")
        return result.stdout