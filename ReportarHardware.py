umbralTempCPU = 80
umbralTempGPU = 70
umbralRamUsada = 75
segundos = 600



import requests
import json

import platform
import subprocess as commands

import sched, time






class ObtenerIP:
    def __init__(self):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.ipEquipo = s.getsockname()[0]
        s.close()

    def getIP(self):
        return self.ipEquipo


myIP = ObtenerIP().getIP()











nombreEstacion = ""
req = requests.get(
    'https://paul.fcv.org:8443/NurcallApp/NurcallAppServlet?Proceso=listNurcall&Estacion=00&raspberry=' + myIP,
    verify=False,
    timeout=5)
respuesta = str(req.text)
listaDispositivosNurcall = []
if len(req.text)>5:
    res = json.loads(req.text)
    nombreEstacion = ""
    for objeto in res:
        listaDispositivosNurcall.append((objeto["ipLampara"], objeto["descripcionLampara"]))
        nombreEstacion = objeto["nombreEstacion"]
        break






TOKEN = "673863930:AAHnDKVX2HyWXJfAuWS3gzs2kGq_3WRNmvE"
DestinatarioTelegram = -356316070
class TelegramService():
    """

    AUTHOR: WISROVI

    """
    Token = ""
    def __init__(self, token):
        self.Token = token


    def sendMessageForUrl(self, Id_group, Mensaje):
        url = "https://api.telegram.org/bot" + self.Token
        url += "/sendMessage?chat_id=" + str(Id_group)
        url += "&text=" + Mensaje
        respuestaGet = requests.get(url, timeout=15)
        if respuestaGet.status_code == 200:
            return True
        else:
            return False

    def verActualizacionesBot(self):
        url = "https://api.telegram.org/bot" + self.Token
        url += "/getUpdates"
        respuestaGet = requests.get(url)
        if respuestaGet.status_code == 200:
            print(respuestaGet.content)
        else:
            print("Error solicitar info sobre los chat del bot")



telegram = TelegramService(TOKEN)






def get_cpu_temp():
    tempFile = open("/sys/class/thermal/thermal_zone0/temp")
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp) / 1000
    # Mostrar temperatura en grados Fahrenheit
    # return float(1.8*cpu_temp)+32


def get_gpu_temp():
    gpu_temp = commands.getoutput('/opt/vc/bin/vcgencmd measure_temp').replace('temp=', " ").replace("'C", " ")
    return float(gpu_temp)
    # Mostrar temperatura en grados Fahrenheit
    # return float(1.8* gpu_temp)+32




# Return RAM information (unit=kb) in a list
# Index 0: total RAM
# Index 1: used RAM
# Index 2: free RAM
def getRAMinfo():
    p = os.popen('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            return(line.split()[1:4])

def obtenerPorcentajeRamUsada():
    ram = getRAMinfo()
    return round((float(ram[1]) * 100) / float(ram[0]))



s = sched.scheduler(time.time, time.sleep)


import os
import os.path as path

if path.exists("CPU.rpi") == False:
    archivo = open("CPU.rpi", "w")
    archivo.write(str(round(get_cpu_temp())))
    archivo.close()

if path.exists("GPU.rpi") == False:
    archivo = open("GPU.rpi", "w")
    archivo.write(str(round(get_gpu_temp())))
    archivo.close()

if path.exists("RAM.rpi") == False:
    archivo = open("RAM.rpi", "w")
    archivo.write(str(obtenerPorcentajeRamUsada()))
    archivo.close()

primerInicio = True
def do_something(sc):
    archivo = open("CPU.rpi", "r")
    cpuTemp = float(archivo.read())
    archivo.close()

    archivo = open("GPU.rpi", "r")
    gpuTemp = float(archivo.read())
    archivo.close()

    archivo = open("RAM.rpi", "r")
    gpuRam = float(archivo.read())
    archivo.close()

    if primerInicio:
        cpuTemp = 0
        gpuTemp = 0
        gpuRam = 0

    temperaturaCPUactual = round(get_cpu_temp())
    temperaturaGPUactual = round(get_gpu_temp())
    ramActual = obtenerPorcentajeRamUsada()

    hayMensajeReportar = False
    infoEnviar = "Esto es una alerta del sistema de:" + nombreEstacion + "\n"
    #infoEnviar += "Soy la raspberry con IP: " + myIP + "\n"
    #infoEnviar += "SO: " + platform.system() + "\n"
    #infoEnviar += "Nombre equipo: " + platform.node() + "\n"
    #infoEnviar += "Procesador: " + platform.machine() + "\n"
    #infoEnviar += "Arquitectura: " + platform.architecture()[0] + "\n"
    #infoEnviar += "Version Python: " + platform.python_version() + "\n"
    if temperaturaCPUactual >= umbralTempCPU:
        if cpuTemp != temperaturaCPUactual:
            hayMensajeReportar = True
            infoEnviar += "Mi temperatura de CPU es: " + str(temperaturaCPUactual) + "C" + "\n"

    if temperaturaGPUactual >= umbralTempGPU:
        if gpuTemp != temperaturaGPUactual:
            hayMensajeReportar = True
            infoEnviar += "Mi temperatura de GPU es: " + str(temperaturaGPUactual) + "C"  + "\n"

    if ramActual >= umbralRamUsada:
        if gpuRam != ramActual:
            hayMensajeReportar = True
            infoEnviar += "Mi RAM usada es: " + str(ramActual) + "%"  + "\n"

    if hayMensajeReportar:
        telegram.sendMessageForUrl(DestinatarioTelegram, infoEnviar)



    archivo = open("GPU.rpi", "w")
    archivo.write(str(temperaturaGPUactual))
    archivo.close()

    archivo = open("CPU.rpi", "w")
    archivo.write(str(temperaturaCPUactual))
    archivo.close()

    archivo = open("RAM.rpi", "w")
    archivo.write(str(ramActual))
    archivo.close()

    s.enter(segundos, 1, do_something, (sc,))
s.enter(segundos, 1, do_something, (s,))
s.run()


