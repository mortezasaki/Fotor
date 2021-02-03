# Jan 04 2021
# For interact with procces like telegram cli when ask a user for input

import subprocess

def start(executable_file):
    return subprocess.Popen(
        executable_file
    )

# https://stackoverflow.com/a/43276598/9850815
def is_running(process):
    poll = process.poll()
    if poll is None:
        return True
    return False

def read(process):
    return process.stdout.readline().decode("utf-8").strip()


def write(process, message):
    process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
    process.stdin.flush()


def terminate(process):
    process.stdin.close()
    process.terminate()
    process.wait(timeout=0.2)