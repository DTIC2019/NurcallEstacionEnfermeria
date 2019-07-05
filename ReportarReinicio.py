"""###
Creado por William Rodriguez
Ingeniero Electronico
WISROVI
###"""

import os

os.system("git clone https://github.com/DTIC2019/HorariosEjecucionNurcallApp")


from HorariosEjecucionNurcallApp.HorariosProcesos import *


import requests
import json

import os.path as path
import pandas as pd
import sched, time
import matplotlib
matplotlib.use('Agg') #necesario para poder guardar una imagen de matplotlib, sin tener interfaz grafica en la ejecucion del codigo
import matplotlib.pyplot as plt


segundos = 30


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
#myIP = "172.30.131.25"
nombreArchivo = "Reporte.nurcall"
nombreImagen = "Reporte.jpg"
print(myIP)



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

TOKEN = "673863930:AAHnDKVX2HyWXJfAuWS3gzs2kGq_3WRNmvE"
DestinatarioTelegram = -356316070
telegram = TelegramService(TOKEN)

def UpdateClock():
    try:
        req = requests.get(
            'https://paul.fcv.org:8443/NurcallApp/NurcallAppServlet?Proceso=clock',
            verify=False,
            timeout=5)
        respuesta = str(req.text)
    except:
        respuesta = ""

    if len(respuesta) > 2:
        os.system("sudo date " + respuesta)



def VerListadoNurcallPorIpEstacion(address, primerInicio = False):
    nombreEstacion = ""
    try:
        req = requests.get(
            'https://paul.fcv.org:8443/NurcallApp/NurcallAppServlet?Proceso=listNurcall&Estacion=00&raspberry=' + address,
            verify=False,
            timeout=5)
        respuesta = str(req.text)
    except:
        respuesta = ""

    NurcallEstaEstacion = []
    if len(respuesta)>5:
        listaTemporalNurcall = []
        res = json.loads(respuesta)

        for objeto in res:
            datoGuardar = (objeto["ipLampara"], objeto["descripcionLampara"])
            if datoGuardar not in listaTemporalNurcall:
                listaTemporalNurcall.append(datoGuardar)
            nombreEstacion = objeto["nombreEstacion"]

        print(nombreEstacion)
        if primerInicio:
            mensaje = """
                Hola, soy la estación de enfermería %s con ip %s y me acabo de reiniciar.
                """ % (nombreEstacion, myIP)
            primerInicioRobot = path.exists("robot.rpi")
            if primerInicioRobot == False:
                mensaje += "\n" + "************* \nEste es el primer inicio del robot V2.1"
                mensaje += "\n" + "Adicionalmente el robot reiniciara la estacion de enfermeria en los siguientes horarios: "
                h = ""
                for hora, minuto in horasReinicio:
                    h += str(hora) + ":" + str(minuto) + " - "
                h = h[:len(h)-3]
                mensaje += "\n" + h	
                mensaje += "\n" + "Esto con el fin de reducir la probabilidad de bloqueo de la estacion, borrar la caché, " \
                                  "darle un tiempo para bajar la temperatura, limpiar la memoria RAM de los subprocesos" \
                                  " y borrar archivos temporales que no son explisitamente necesarios "
                t = ""
                for hora, minuto in horasEnviarTelegram:
                    t += str(hora) + ":" + str(minuto) + " - "
                t = t[:len(t)-3]
                mensaje += "\n" + "Seguidamente el robot enviará reporte de los llamado de enfermeria que el robot no haya podido solucionar. "
                mensaje += "Estos reportes se enviaran en los siguientes horarios: " + t	
				
                i = ""
                for hora, minuto in horasEnviarFoto:
                    i += str(hora) + ":" + str(minuto) + " - "
                i = i[:len(t)-3]
                mensaje += "\n" + "Finalmente el robot enviará un reporte gráfico de la estación de enfermeria: " + nombreEstacion + ". "
                mensaje += "Estos reportes se enviaran en los siguientes horarios: " + i	
                mensaje += "\n*************"
								  

            if ProcesoEnviarTelegram(mensaje):
                hoy = "Fecha y hora primer inicio robot version 2.0: " + time.strftime("%c")
                archivo = open("robot.rpi", "w")
                archivo.write(hoy)
                archivo.close()
            else:
                print("Error enviando Telegram")
            print("Enviando telegram primer inicio:", not primerInicioRobot)

        conteo = 0
        for nurcall in listaTemporalNurcall:
            NurcallEstaEstacion.append((conteo, nurcall[0], nurcall[1]))
            conteo += 1

    return NurcallEstaEstacion, nombreEstacion

def EvaluarNurcall(address, timeout=5):
    try:
        req = requests.get("http://" + address + "/nurcall?L-P&", timeout=timeout)
    except:
        pass

    try:
        rta = req.text
    except:
        rta = "No Funciona esta lampara"

    rta = rta.replace(",", "")
    rta = rta.replace("\n", "")
    rta = rta.replace("\t", "")
    rta = rta.replace("\r", "")
    if len(rta) > 7:
        if rta.find("usted desplego el mensaje")>0:
            return 500  # error interno
        else:
            if rta.__eq__("No Funciona esta lampara"):
                return 404 #no encontrada
            else:
                return 304  #independietne
    else:
        if rta[0].__eq__("Y"):
            return 200  #Conecxion correcta
        else:
            return 500 #error interno

def ResetearNurcall(address, timeout=5):
    textoBuscar = "usted esta reiniciando la lampara"
    try:
        req = requests.get("http://" + address + "/nurcall?R-A&", timeout=timeout)
    except:
        pass

    try:
        rta = req.text
    except:
        rta = "No Funciona esta lampara"

    rta = rta.replace(",", "")
    rta = rta.replace("\n", "")
    rta = rta.replace("\t", "")
    rta = rta.replace("\r", "")
    if len(rta) > 7:
        if rta.find("usted desplego el mensaje")>0:
            return 500  # error interno
        else:
            if rta.__eq__("No Funciona esta lampara"):
                return 404 #no encontrada
            else:
                if rta.find(textoBuscar) > 0:
                    return 200  # Conecxion correcta
                else:
                    return 500 #error interno
    else:
        return 304  #independietne

def LeerCSV():
    NombresCampos = ['Nurcall', '200', '404', '304', '500']
    return pd.read_csv(nombreArchivo,
                         header=None,
                         sep=',',
                         names=NombresCampos)

def GuardarCSV(dataframe):
    dataframe.to_csv(nombreArchivo, index=None, header=None)

def LeerArchivo(listado):
    if path.exists(nombreArchivo) == False:
        df = pd.DataFrame([])#, columns=NombresCampos
        GuardarCSV(df)

    dframe = LeerCSV()

    if dframe.shape[0] == 0:
        for nurcall in listado:
            NombresCampos = ['Nurcall', '200', '404', '304', '500']
            df2 = pd.DataFrame([[nurcall[0], 0, 0, 0, 0]], columns=NombresCampos)
            dframe = pd.concat([dframe, df2])
        GuardarCSV(dframe)

        return LeerCSV()
    else:
        return dframe

def ReemplazarEnDataframe(dataframe, indexFila, indexColumna, valor):
    dataframe.iat[indexFila, indexColumna] = valor
    return dataframe

def ReemplazarEnDataframeString(dataframe, indexFila, indexColumna, valor):
    dataframe.iat[indexFila, indexColumna] = valor
    return dataframe

def LeerCeldaDataframe(dataframe, indexFila, nombreColumna):
    return dataframe.iloc[indexFila][nombreColumna]

def ActualizarDataframeParaCadaNurcall(dataframe, rta, tuplaNurcall):
    if rta == 200:
        valorActual = LeerCeldaDataframe(dataframe, tuplaNurcall[0], '200')
        dataframe = ReemplazarEnDataframe(dataframe=dataframe, indexFila=tuplaNurcall[0], indexColumna=1, valor=valorActual+1)
        #print("OK", tuplaNurcall)
    elif rta == 404:
        valorActual = LeerCeldaDataframe(dataframe, tuplaNurcall[0], '404')
        dataframe = ReemplazarEnDataframe(dataframe=dataframe, indexFila=tuplaNurcall[0], indexColumna=2, valor=valorActual+1)
        #print("Sin conexion", tuplaNurcall)
    elif rta == 304:
        valorActual = LeerCeldaDataframe(dataframe, tuplaNurcall[0], '304')
        dataframe = ReemplazarEnDataframe(dataframe=dataframe, indexFila=tuplaNurcall[0], indexColumna=3, valor=valorActual+1)
        #print("Independiente", tuplaNurcall)
    elif rta == 500:
        valorActual = LeerCeldaDataframe(dataframe, tuplaNurcall[0], '500')
        dataframe = ReemplazarEnDataframe(dataframe=dataframe, indexFila=tuplaNurcall[0], indexColumna=4, valor=valorActual+1)
        #print("Error interno", tuplaNurcall)
    return dataframe

def BuscarFalloQueNoSePuedeResolver(lampara, rta):
    if rta != 200:
        rta = ResetearNurcall(lampara[0], 8)
        if rta != 200:
            return True
        else:
            return False
    else:
        return False

def ProcesoGrafica(sumarioConteoCodigos, nombreEstacion, lista):
    sumarioConteoCodigos = sumarioConteoCodigos.rename(columns={
        "200": "OK",
        "404": "Sin conexion",
        "304": "Independiente",
        "500": "Error interno"})
    sumarioConteoCodigos['Descripcion'] = 'NULL'
    sumarioConteoCodigos = sumarioConteoCodigos.drop(['Nurcall'], axis=1)

    conteoIndex = 0
    for NuevoNombre in lista:
        sumarioConteoCodigos = ReemplazarEnDataframeString(sumarioConteoCodigos, conteoIndex, 4, NuevoNombre[2])
        conteoIndex += 1

    sumarioConteoCodigos.set_index("Descripcion", drop=True, inplace=True)
    print(sumarioConteoCodigos)
    try:
        ax = sumarioConteoCodigos.plot.bar(figsize=(10, 5))
        ax.set_title("Resultados " + nombreEstacion)
        plt.ylabel("Sondeo Datos (Minutos) ultimas 4 horas")
        plt.xlabel("Lamparas evaluadas por el robot.")
        plt.savefig(nombreImagen, bbox_inches="tight")
    except Exception as inst:
        print(inst.args)
        print(inst)
        print("Problema con el guardado de la imagen")
    finally:
        pass
    #plt.show()

def ProcesoEnviarTelegram(infoEnviar):
    return telegram.sendMessageForUrl(DestinatarioTelegram, infoEnviar)

def ProcesoEstacionEnfermeriaNurcall():
    hour = int(time.strftime("%H"))
    minute = int(time.strftime("%M"))
    second = int(time.strftime("%S"))
    try:
        temp = nombreEstacion
    except:
        nombreEstacion = ""

    try:
        size = len(listaLamparasRequierenReinicioManual)
    except:
        listaLamparasRequierenReinicioManual = []

    for hora, minuto in horasEjecutarRobot:
        if hour == hora and minute == minuto:
            time.sleep(30)
            listaLamparasRequierenReinicioManual = []
            listadoNurcallEstacion, nombreEstacion = VerListadoNurcallPorIpEstacion(myIP)
            df = LeerArchivo(listadoNurcallEstacion)
            for nurcall in listadoNurcallEstacion:
                rta = EvaluarNurcall(nurcall[1], 8)
                df = ActualizarDataframeParaCadaNurcall(df, rta, nurcall)
                if BuscarFalloQueNoSePuedeResolver(nurcall, rta):
                    listaLamparasRequierenReinicioManual.append(nurcall)
            GuardarCSV(df)
            ProcesoGrafica(df.copy(), nombreEstacion, listadoNurcallEstacion)
            break

    for hora, minuto in horasEnviarTelegram:
        if hour == hora and minute == minuto:
            time.sleep(30)
            if len(listaLamparasRequierenReinicioManual) > 0:
                infoEnviar = "Estas lamparas de la estación de enfermería " + nombreEstacion + ", requieren ser revisadas fisicamente: \n"
                for lamparaFallando in listaLamparasRequierenReinicioManual:
                    infoEnviar += lamparaFallando[2] + "\n"
                ProcesoEnviarTelegram(infoEnviar)
            break
	
    print(hour, ":", minute, ":", second)


def do_something(sc):
    ProcesoEstacionEnfermeriaNurcall()
    sc.enter(segundos, 1, do_something, (sc,))

UpdateClock()
VerListadoNurcallPorIpEstacion(myIP, True)

s = sched.scheduler(time.time, time.sleep)
s.enter(5, 1, do_something, (s,))
s.run()





