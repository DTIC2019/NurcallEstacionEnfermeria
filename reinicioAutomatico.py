from HorariosEjecucionNurcallApp.HorariosProcesos import *

import sched, time

time.sleep(30)



s = sched.scheduler(time.time, time.sleep)
segundos = 20

import os
import os.path as path
nombreArchivo = "Reporte.nurcall"

def EnviarFoto():
    if path.exists(nombreArchivo):
        try:
            os.system("python3 EnviarFoto.py")
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
            print("No se pudo enviar la foto")

def do_something(sc):
    hour = int(time.strftime("%H"))
    minute = int(time.strftime("%M"))
    second = int(time.strftime("%S"))

    for hora, minuto in horasReinicio:
        if hour == hora and minute == minuto:
            time.sleep(30)
            os.system('sudo reboot')

    for hora, minuto in horasBorrarFoto:
        if hour == hora and minute == minuto:
            time.sleep(30)
            os.system("sudo rm -rf " + nombreArchivo)

    for hora, minuto in horasEnviarFoto:
        if hour == hora and minute == minuto:
            EnviarFoto()
            time.sleep(30)

    print(hour, ":", minute, ":", second)
    s.enter(segundos, 1, do_something, (sc,))

print("Sistema de autoreinicio iniciado.")
s.enter(segundos, 1, do_something, (s,))
s.run()
