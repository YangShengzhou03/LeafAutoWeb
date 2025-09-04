import os
import subprocess
import sys
import time

from server_manager import start_vue_server, open_browser



flask_process = subprocess.Popen(
    ['python', 'app.py'],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True
)


for i in range(5):
    
    time.sleep(1)


start_vue_server()


open_browser()



try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    
    flask_process.kill()
    
    sys.exit(0)
