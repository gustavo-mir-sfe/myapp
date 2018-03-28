import time
import socket
import requests
import subprocess

#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#s.connect(("10.0.0.86",80))

#requests.get("http://10.0.0.86/restTurneroApp/sucursal/setIpKiosco?id=1&ip=" + s.getsockname()[0])

#s.close()

while True:
    try:
        r = requests.get("http://10.0.0.86/restTurneroApp/sucursal/getComandoKiosco?idSucursal=1")
        if(r.text != ""):
            subprocess.call(r.text)
        time.sleep(60)
    except:
        time.sleep(60)
