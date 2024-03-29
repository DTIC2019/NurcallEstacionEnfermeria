import platform
import commands
 
def get_cpu_temp():
    tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp)/1000
    #Mostrar temperatura en grados Fahrenheit
    #return float(1.8*cpu_temp)+32
 
def get_gpu_temp():
    gpu_temp = commands.getoutput( '/opt/vc/bin/vcgencmd measure_temp' ).replace('temp=', " " ).replace( "'C", " " )
    return  float(gpu_temp)
    #Mostrar temperatura en grados Fahrenheit
    # return float(1.8* gpu_temp)+32
 
def main():
    print("Umbral temperatura", 80)
    print( "Temperatura CPU: ", round(get_cpu_temp()))
    print( "Temperatura GPU: ", round(get_gpu_temp()))

    print( "Sistema operativo: ",platform.system())
    print( "Nombre equipo", platform.node())
    print( "Procesador: ",platform.machine())
    print( "Version python:", platform.python_version())
    print( "Arquitectura procesador:", platform.architecture()[0])
 
if __name__ == '__main__':
    main()

