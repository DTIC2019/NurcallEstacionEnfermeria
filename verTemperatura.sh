#!/bin/bash
 # Shell script: temp.sh
 # Autor: Santiago Crespo
 cpu=$(cat /sys/class/thermal/thermal_zone0/temp)
 echo "$(date) @ $(hostname)"
 echo "-------------------------------------------"
 echo "Temp.CPU => $((cpu/1000))'Cº"
 echo "Temp.GPU => $(/opt/vc/bin/vcgencmd measure_temp)"
 echo "Nivel critico que ralentiza la raspberry 75Cº"
 echo "-------------------------------------------"
