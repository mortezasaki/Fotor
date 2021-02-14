# Jan 04 2021
# For interact with procces like telegram cli when ask a user for input

import subprocess
import select
from time import sleep
import logging
import re

def start(executable_file):
    return subprocess.Popen(
        executable_file,
        stdout=subprocess.PIPE
    )

# https://stackoverflow.com/a/43276598/9850815
def is_running(process):
    poll = process.poll()
    if poll is None:
        return True
    return False

def read(process):
    out = process.stdout
    if out is not None:
        return process.stdout.readline().decode("utf-8").strip()


def write(process, message):
    process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
    process.stdin.flush()


def terminate(process):
    process.stdin.close()
    process.terminate()
    process.wait(timeout=0.2)

# https://stackoverflow.com/a/12523371/9850815
def tail(filename,searched = None, match = True):
    f = subprocess.Popen(['tail','-F',filename],\
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    
    p = select.poll()
    p.register(f.stdout)

    while True:
        try:
            if p.poll(1):
                log = f.stdout.readline().decode("utf-8").strip()
                pattern = r'^\d{4}-\d{2}-\d{2}( )\d{2}(:)\d{2}(:)\d{2}( - )\d{8,}( - )\w+' # EX 2021-02-14 11:37:46 - 6283840238778 - Disconnecting
                if match and re.match(pattern, log): # solution for issue 13 only print logs
                    if searched is not None:
                        if searched in log:
                            print (log)
                    else:
                        print(log)
                elif not match:
                    print(log)

                
            sleep(.1)
        except KeyboardInterrupt:
            f.kill()
            break
        except BrokenPipeError: # Solution for issue 13 
            pass
        except Exception as e:
            logging.info(type(e).__name__)
    f.kill()
