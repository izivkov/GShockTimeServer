import subprocess
import time

def ensure_bt_ready():
    for _ in range(10):
        try:
            output = subprocess.check_output(["bluetoothctl", "show"]).decode()
            if "Powered: yes" in output:
                return True
            subprocess.run(["bluetoothctl", "power", "on"], input=b"yes\n", timeout=2)
        except:
            pass
        time.sleep(1)
    return False
