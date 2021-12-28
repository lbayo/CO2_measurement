#                This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
# lector C02

# Para tener diferentes fonts, hay que instalar la libreria oled mediante (desde el shell de python)
# import upip
# upip.install("micropython-oled")
#
# referencia : https://micropython-oled.readthedocs.io/en/latest/content/getting_started.html
#
# Programacion OLED : https://www.esploradores.com/oled_ssd1306/

# librerias 

from machine import Pin, SoftI2C, ADC, reset, unique_id, freq, TouchPad, UART, SoftSPI, TouchPad, time_pulse_us
import ssd1306
import sh1106
from utime import sleep, localtime, time, time_ns
import ntptime
import usocket as socket
import network, ubinascii
from ubinascii import hexlify
from calendario import Hz
from oled import Write, GFX, SSD1306_I2C
from oled.fonts import ubuntu_mono_15, ubuntu_mono_20
import dht
import gc
from mqtt_as import MQTTClient, config
import uasyncio as asyncio
import ubinascii
from e_syslogo import *
import json
import st7789
from tft_lib import ini_tft, tft_display,text,show_rssi
import segments

# Definiciones HARDWARE y programables
# cfguración por defecto

cfg={
'Version'     :  19.1,                            # version del programa
'VersionDate' : '11-07-2021',                   # fecha version del programa
'frecuencia'  :  240,                           # frecuencia de reloj del micro en MHz
'touchpad'    : False,                          #
'touchpin'    :  15,
'touchlevel'  : 180,                            #
'touchstop'   : True,                             # touch to stop program
'touchstoppin':   2,                             # touch to stop program
'touchstoplev':  300,                          
'led'         : True,                           # Hay LED?
'ledpin'      :   32,                           # Pin para led de aviso
'keepalive'   : 120,
'wifi'        : True,
                                                 # lista de ssid paswords de WiFi
'ssidx'       : [
                ],       
'nmaxlan'     :  4,                             # maximo numero de lans memorizadas
'lasttry'     :  0,                             # ñultimo intento de conexions a la ssid
'tmout1'      :  200,                           # segundos. Time out para entrar SSID y password 2 veces 
'tmout2'      :  300,                           # segundos. Time out para entrar SSID y password 2 veces 

'display'     : True,                           # enable display
'displaytype' : 'TFT',                          # SPI o I2C (if SPI fixed pinout)
'SCL'         :   22,                           # I²C Pin scl
'SDA'         :   13,                           # I²C Pin sda
'SPI_SCK'     :   19,
'SPI_MOSI'    :   21,
'SPI_MISO'    :   23,
'SPI_DC'      :   17,
'SPI_RES'     :    5,
'SPI_CS'      :   16,
'TFT_BACK'    :    0,
'sensorCO2'   : 'MH-Z19B',                      # TIPO: MH-Z19B
'autocero'    : True,                           # autocero as described in datasheet (MH-Z19B only)
'rx'          :   25,                           # serial Rx for MH-Z19B sensor (only)
'tx'          :   27,                           # serial Tx for MH-Z19B sensor (only)
'BATERIA'     :   34,                           # pin lector batería (fondo escala 1 voltio)
'TEMPERATURA' :   33,                           # pin lector temperatura DHT-11 o DHT-22
'TIPOLECTOR'  : "DHT11",                       # tipo de lector de temperatura
'mqtt'        : True,                           # enable MQTT protocol
'server'      : 'e-sys.ddns.net',               # IP address or URL for MQTT broker
'port'        : 1883,
'qos'         :    0,                           # mqtt quality of service 
'prefijo'     : '',                             # prefijo  a  todos los topics
'topic_pub'   : 'CO2',                          # sender (puplish) topic
'topic_sub'   : 'MONITOR',                      # topic for monitor 
'topic_msg'   : 'MSG',                          # topic for messages
'BatLow'      : 2790,                           # valor del conversor A/D para batería baja    (nivel 0, 4.5 v aprox)
'BatHigh'     : 3150,                           # valor del conversor A/D para batería cargada (nivel 3, 5.0 v aprox)
'estabilidad' :  0.1,                           # criterio de estabilidad 10%
'NMAX_MEDIDAS':    6,                           # tamanño fifo para hacer medias
'NOESTABLE'   : '-',                            # simbolo para lectura no estable
'WARMUP'      : '?',                            # simbolo de período de calentamiento
'T_WARMUP'    :   5,                            # tiempo de calentamiento (minutos)
'NIVELES_LED' : [700,1000,1600],                # niveles CO2 de centelleo LED
'T_BASELINE'  : 3600,                           # intervalo de tiempo (segundos) para correccion baseline
'PAUSA'       :    2,                           # pausa entre dos iteraciones (segundos)
'VERBOSE'     : True,                           # modo silencioso (False), sin imprimir nada
'PINACCION'   :    4,                           # pin para disparo ventilaación
'NIVELES'     : [0,1],                          # niveles logicos  [OFF,ON] de ventilación
'VENTVALOR'   : [800,1200],                     # nivel de activación y desactiavcion (trigger schmitt)
'AvisoVent'   : True,                           # aviso sonoro de ventilador
'AvisoNivel'  : True,                           # aviso niveles CO2
'Avisos'      :[[ 600,'Niveles de C O 2 superan ', 'Niveles de C O 2 inferiores a'],  # lista ordenada por CO2 de los avisos
                [1200,'Atencion, niveles de C O 2 superan ', 'Niveles de C O 2 inferiores a'],  # al superar el valor se envia el mensaje por el topic <topic_pub>/MSG
                [1800,'Alarma, Niveles de C O 2 superan ', 'Niveles de C O 2 inferiores a']],
'ymin'        :     0,                          # minimo Y en grafico
'ymax'        :  2000,                          # minimo Y en grafico
'xinter'      :     4,                          # intervalo de medidas en X para grafico (tomar 1 de cada xinter) 
'debug'       :     1,    # 1: trace data  2:trace times 4:trace WiFi 8:miscelaneous data
'LedGreen'    :    22,
'LedBlue'     :    18,
'LedRed'      :    22,
'watchdogtime':    30
 }


offx=0; offy=0
def Xaxis(oled,color):
    oled.line (3+offx,60+offy,123+offx,60+offy,color)
    oled.pixel (121+offx,58+offy,color);oled.pixel (121+offx,59+offy,color);oled.pixel (121+offx,61+offy,color)
    oled.pixel (121+offx,62+offy,color);oled.pixel (122+offx,59+offy,color);oled.pixel (122+offx,61+offy,color)

def Yaxis(oled,color):
    oled.line (2+offx,60+offy,2+offx,0+offy,color) # eje
    oled.pixel (0+offx, 2+offy,color) ; oled.pixel (1+offx, 1+offy,color); oled.pixel (1+offx, 2+offy,color)
    oled.pixel (3+offx, 1+offy,color) ; oled.pixel (3+offx, 2+offy,color); oled.pixel (4+offx,2+offy,color) # flecha
    # divisiones cada multiplo de 500 : 
    for i in range ((cfg['ymax']-cfg['ymin'])/500-1):
        y=cfg['ymin']+(i+1)*500
        y=pp=int((y-cfg['ymin'])*60/(cfg['ymax']-cfg['ymin']))
        oled.pixel (1+offx,y+offy,color);oled.pixel (3+offx,y+offy,color)

def draw (oled,p,color):
    x0=0; y0=p[0]
    for i in range (1,len(p)):
        oled.line(x0+2+offx,60-y0+offy,i+2+offx,60-p[i]+offy,color)
        x0=i; y0=p[i]
    
def plot (x,p):
    pp=int((x-cfg['ymin'])*60/(cfg['ymax']-cfg['ymin']))
    pp=min(max(0,pp),60)
    p+=[pp]
    if len (p)>120:
        p.pop(0)
        
def do_grafic(oled,tipo, p,coloraxis,colorgraf):
    if cfg['displaytype']=="TFT":
        oled.fill_rect(offx, offy, 128, 64, 0) 
        Xaxis(oled,coloraxis)
        Yaxis(oled,coloraxis)
        draw (oled,p,colorgraf)
#        text (oled, 'lib/tft/romancs.fnt', "%4d"%co2+" ppm", 90+offx,  2+offy,st7789.color565(  0,255,255))
    else:
        oled.fill(0) 
        Xaxis(oled,coloraxis)
        Yaxis(oled,coloraxis)
        draw (oled,p,colorgraf)
        tipo.text ("%4d"%co2+" ppm", 5,1)
        oled.show()    
    

def time_ms():
    return float(time_ns())

async def robin():
    await asyncio.sleep(0)

mqtt_queue=[]

async def mqttSend():
    global mqtt_queue, client
    while Run:
        while len(mqtt_queue)>0:
            if client.isconnected():
                top,msg=mqtt_queue.pop(0)
                await client.publish(top, msg.encode(), qos = cfg['qos'])
            await asyncio.sleep(0.5)
        await asyncio.sleep (0.5)


async def publica (top,msg):
    global mqtt_queue
    mqtt_queue.append ((top,msg))       
        
    
 
lans=[]    
v_estado=0;
pin_vent=0
aviso=False
n1=0
n0=0
niv=0

def automata_ventilacion(init):
    global fan,v_estado,pin_vent, n1,n0,aviso,niv
    if init:
        pin_vent=Pin(cfg['PINACCION'], Pin.OUT)
        v_estado=0                             # estado inicial
        pin_vent.value (cfg['NIVELES'][v_estado])   # poner salida
        n1=cfg['VENTVALOR'][1]
        n0=cfg['VENTVALOR'][0]
        aviso=not cfg["AvisoVent"]
        niv=cfg['NIVELES']
    if v_estado==0:                           # estado OFF
        if co2>n1:           # si supera valor alto, cambia estado
            v_estado=1
            fan="ON "
    else:                                     # estado ON
        if co2<n0:
            v_estado=0                        # si menos del nivel bajo, cambia estado
            fan="OFF"
           
    if aviso:
        fan="   "
        
    pin_vent.value (niv[v_estado])      # seta salida correspondiente 

estado=0
siguiente_estado=0
mensaje=""

def automata_avisos():
    global mensaje,estado, siguiente_estado
    cc=co2
    if estado==0 and cc>cfg['Avisos'][0][0]:
        siguiente_estado=1
    if estado==1 and cc>cfg['Avisos'][1][0]:
        siguiente_estado=2
    if estado==1 and cc<=cfg['Avisos'][0][0]:
        siguiente_estado=0
    if estado==2 and cc>cfg['Avisos'][2][0]:
        siguiente_estado=3
    if estado==2 and cc<=cfg['Avisos'][1][0]:
        siguiente_estado=1
    if estado==3 and cc<=cfg['Avisos'][2][0]:
        siguiente_estado=2
           
    if siguiente_estado !=estado:
        if siguiente_estado>estado:
            mensaje=cfg['Avisos'][estado][1]+str(cfg['Avisos'][estado][0])+ " P P M "
        else:
            mensaje=cfg['Avisos'][siguiente_estado][2]+str(cfg['Avisos'][siguiente_estado][0])+ " P P M "
        estado =siguiente_estado
        print ("Mensaje:"+mensaje)
    else:
        mensaje=""        
    if not cfg['AvisoNivel']:   # si no hay que dar mensaje  ...
        mensaje=""

# blink status en Pin 32
# si niveles OK --- breve destello
# si niveles cerca de limite --- destello intermitente
# si niveles por encima limite --- led fijo
async def ledblink():   
    pin = Pin(cfg["ledpin"], Pin.OUT)
    while Run:
        ton=0.33*blinklevel+0.01
        toff=1-ton
        pin.value(1)
        await asyncio.sleep(ton)
        pin.value(0)
        await asyncio.sleep(toff)



# visualizar bateria con nivel de carga
# aplicar a pin 35 la tensión de alimentación después de divisor por 2
# tension de 5 v --- 3 rayas, 4.5 v -- cero rayas
# indicador de carga excesiva o baja
def bateria (oled,x0,y0):
    # Matriz de puntos
    ICONO = [                           
        [ 0, 0],
        [ 0, 1],
        [ 0, 1],
        [ 1, 1],
        [ 1, 1],    
        [ 1, 0],    
        [ 1, 0],    
        [ 0, 0],
    ]
    n=nivel()
    if n in [0,1,2,3]:
        for y, fila in enumerate(ICONO):       # Dibuja los puntos de la matriz  
            for x, c in enumerate(fila):
                if n>2:
                    oled.pixel(x0+x+ 4, y0+y, c)
                else:
                    oled.pixel(x0+x+ 4, y0+y, 0)
                if n>1:
                    oled.pixel(x0+x+ 8, y0+y, c)
                else:
                    oled.pixel(x0+x+ 8, y0+y, 0)
                if n>0:
                    oled.pixel(x0+x+12, y0+y, c)
                else:
                    oled.pixel(x0+x+12, y0+y, 0)
        oled.rect (x0+2,y0+0,14,9,1)
        oled.fill_rect (x0+0,y0+2,2,4,1)
    else:
        if n>=4:  # sobrecarga o alimentación externa
           oled.fill_rect(x0, y0, 16, 9, 0)
           oled.line (x0+ 2,y0+ 6,x0+ 6,y0+ 2,1)
           oled.line (x0+ 6,y0+ 2,x0+10,y0+ 6,1)
           oled.line (x0+10,y0+ 6,x0+13,y0+ 3,1)
           oled.line (x0+12,y0+ 2,x0+14,y0+ 2,1)
           oled.line (x0+14,y0+ 2,x0+14,y0+ 4,1)
        else:        # muy descargada (blink)
           oled.fill_rect(x0, y0, 16, 9, 0)
 
# cakcular nivel (0 a 3) en función de entrada A/D
def nivel ():
    x=adc.read()
    z=int(4*(x-cfg["BatLow"])/(cfg["BatHigh"]-cfg["BatLow"]))
    z=min(max (-1,z),9)
    return z

# tiempo de funcionamiento 
def running_time():
    global tStart
    return time()-tStart 

# convierte  un string en una variable de tipo int, float, boolean, list o string (según corresponda)
def convert(x):
    try:            # probar si es entero
        z=int(x)
    except:
        try:            # provar si es float
            z=float(x)
        except:
            X=x.upper()
            if X in ["TRUE", "FALSE"]: # miarar si es booleano
              z=(X=="TRUE")
            elif len(x)>=2:  # puede ser una lista ?
                if (x[0]=="[") and (x[-1]=="]"): #si empeiza por [ y acaba por ] es uan lista
                    z=x[1:-1].split(",")
                    lst=[]
                    for i in range (len(z)):
                        lst+=[convert(z[i])]
                    z=lst
                else:
                    if x[0]=="'" and x[-1]=="'" or x[0]=='"' and x[-1]=='"':
                        z=x[1:-1]
                    else:
                        z=x
            else:  # es un string
                if x[0]=="'" and x[-1]=="'" or x[0]=='"' and x[-1]=='"':
                    z=x[1:-1]
                else:
                    z=x
    return z
    
# stop program (set Run to false) if stop touchpad is set
async def WatchStop():
    global Run
    if cfg['touchstop']:
        StpSwt=TouchPad(Pin(cfg['touchstoppin']))
        R0=True
        while Run:
            z=StpSwt.read()
            R1= (z>cfg['touchstoplev'])
            Run=Run and (R0 or R1)
            R0=R1
            await asyncio.sleep (0.5)
        print ("** user stop **",z, R0, R1)

#---------------------------------
# Receive a message by MQTT protocol an returns it
# if message is 'stop', stops the program and returns False
# implemented commands:
#   stop       .......... stop program
#   time ................ sends UTC time
#   <any cfg variable> .. send the value of this variable
#   <variable> <value> .. sets variable to value
#   save ................ writes all variables to permanent memory

def sub_cb(topic, msg, retain):
    global Run, station, client, cfg
    tsub=cfg["prefijo"]+cfg["topic_sub"]
    tpub=cfg["prefijo"]+cfg["topic_pub"]
    tmsg=cfg["prefijo"]+cfg["topic_msg"]
    dg=cfg['debug']
    tpc=topic.decode()
    mss=msg.decode()
    if tpc == tsub:
      nl=mss.split()
      if len(nl)==0:
          return
      Run= Run and (nl[0]!='STOP')
      if not Run:
          print ("** MQTT stop request **")
          return
      if nl[0]=='TIME':
        anyo,mes,dia,hora,minuto,segundos,x,y=localtime()  # hora UTC
        mss='UTC Time:%2d-%02d-%02d %2d:%02d:%02d'%(anyo%100,mes,dia,hora,minuto,segundos)
        mqtt_queue.append((tpub, mss))
      elif nl[0]=='SAVE':
        with  open('config.json', 'w') as f:
            json.dump(cfg, f)
            f.close()
        mss="Data saved !!"
        mqtt_queue.append((tpub, mss))
      elif nl[0]=='SHOW':
        for i in cfg:
          mss= i+"."*(30-len(i))+":"+str(cfg[i])
          mqtt_queue.append((tpub, mss))
      elif nl[0]=='RESET':
          reset()
      else:
        if len(nl)==1: # una variable
            try:
               x=cfg[nl[0]]
               mss=nl[0]+" is "+str(x)
               mqtt_queue.append((tpub, mss))
            except:
               mss="Unknow data "+nl[0]
               mqtt_queue.append((tpub, mss))
        elif len(nl)>=2: # poner valor a variable
            if nl[0]=="MSG":
                mm=msg.decode()[3:]
                mqtt_queue.append((tmsg, mm))
            else:
                try:                    
                    item=nl[0]
                    valor=nl[1]
                    cfg[item]=convert(valor)
                    mss=item+" is set to "+str(valor)
                    mqtt_queue.append((tpub, mss))
                except:
                    mss="Error. Unknow data "+nl[0]
                    mqtt_queue.append((tpub, mss))
    return 
      


# calcula la media de las ultimas medidas y
# y devuelve un simbolo ~ si hay fluctuaciones y
# un espacio en blanco si es estable
def media (fifo):
    n=len(fifo)
    t0,s0=0,0
    for x in fifo:    # media
        t0+=x
    t0=t0/n
    for x in fifo:    # desviacion standard
        s0+=(x-t0)*(x-t0)
    s0=(s0/n)**(1/2)
    if running_time()>cfg["T_WARMUP"]*60:   
        estable0=' ' if cfg["estabilidad"]*t0+5>=max(s0,2) else cfg["NOESTABLE"]  # estabilidad 10%
    else:
        estable0=cfg["WARMUP"]
    return t0,estable0



def set_autocero_MH_Z19B(auto):
    global uart
    if auto:
        cmd=bytearray((0xff,0x01,0x79,0xA0,0,0,0,0,0xE6))
    else:
        cmd=bytearray((0xff,0x01,0x79,0x00,0,0,0,0,0x86))
    uart.write(cmd)
    

def sensorReady(sensortype):
    global sensor, fifo, estableCO2, blibklevel, uart
    co2=0
    ready=False
    cmd=bytearray((0xff,0x01,0x86,0,0,0,0,0,0x79))
    uart.write(cmd)
    if uart.any():
        z=uart.read()
        chksum=0 
        for x in z:
            chksum+=x
        if  len (z)==9 and (chksum & 0xFF==0xFF) :
            co2=256*z[2]+z[3]
            ready=True
    if ready:
        fifo.append(co2)
        if len(fifo)>cfg["NMAX_MEDIDAS"]:
            fifo.pop(0)
        co2,estableCO2=media(fifo)
        if co2<cfg["NIVELES_LED"][0]:
            blinklevel=0
        elif co2>cfg["NIVELES_LED"][2]:
            blinklevel=3
        else:
            blinklevel=3/(cfg["NIVELES_LED"][2]-cfg["NIVELES_LED"][0])*(co2-cfg["NIVELES_LED"][0])            
    return co2


def ini_oled(oled, write20,write15):
    global WiFi
    oled.fill(0)
    txt="CO2"; write20.text(txt, 0, 13)
    txt="ppm"; write20.text(txt, 0, 30)
    txt="T:     C  Hum:   %"; write15.text(txt, 0, 52)
    # HORA ACTUAL
    t=localtime()
    t=Hz(t[0]%100,t[1],t[2],t[3],t[4],t[5])
    if WiFi:
        if ntpFlag:
            s="%2d-%02d-%02d %2d:%02d"%(t[2],t[1],t[0]%100,t[3],t[4])
            if display:
                write15.text(s, 0, 0)
    else:
        if display:
            write15.text("No WiFi", 0, 0) 


# initial setup for wifi data (ssid and pasword)
# program switch to Access Point mode (ssid:e-sys, no password),
# acts as a web server at 192.168.4.1 and send a form web page to client 192.168.4.2 (normally)
# this form allows setting ssid and password for further use
# this mode finish at end of data entry or a fter a timeout time
# timeout for connect tro e-sys WiFI is tmout1 (default 180 s)
# timeout for entry ssi and password is tmout2 (default 240 s)
def WiFiSetup():    
    global response
    # retorna err, ssid , password
    # no ssid  0 .....................OK
    # no ssid  1 .....................No ssid
    # no ssid  2 .....................Np pasw1
    # no ssid  3 .....................No pasw2
    # no ssid  4 .....................pasw1 <> pasw2
    # no ssid  5 .....................red no existente

    def extract (s):
        i=s.find("ssid=")
        if i<0:
            return 1,None,None
        j=s.find("pswd=")
        if j<0:
            return 2,None,None

        k=s.find("pswd2")
        if k<0:
            return 3,None,None
        ssid=s[i+5:j-1]
        pssw=s[j+5:k-1]
        pss2=s[k+6:-1]
        
        if pssw!=pss2:
            return 4,None,None   # passwords diferentes
        if ExistSSID(ssid):
            return 0,ssid, pssw
        return 5,ssid,pssw
        
    def ExistSSID(ssid): # says if a ssid exist really 
        station = network.WLAN(network.STA_IF)
        station.active (True)
        # mirar redes presentes
        for red in station.scan():
            if red[0].decode()==ssid:
                return True
        return False
        
    ssid="e-sys"
    print ('** WIFI SETUP. Connect to SSID',ssid,', please')
    
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password="")

    while not ap.active():
      pass

    print('Connection successful',ssid)
    print(ap.ifconfig())

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    s.settimeout (cfg['tmout1'])  # 10 segons 
    error=None
    tmout=False
    while not error in [0,5]:
      gc.collect()
      try:
          conn, addr = s.accept()
          print('Got a connection from %s' % str(addr))
      except:
          print ("--TOUT 1: no connect")
          s.close()  
          ap.active (False)
          return None
      try:
          s.settimeout (cfg['tmout2'])  
          request = str(conn.recv(1024))
      except:
          print ("--TOUT 2: no connect")
          s.close()  
          ap.active (False)
          ap.disconnect()
          return None
          
      error,ssid,pswd= extract(request)
      gc.collect()
      print ("mem:",gc.mem_free())
      with open("CO2.html") as f:
        response=f.read()
      conn.send(response)
      conn.close()
    s.close()  
    ap.active (False)
    ap.disconnect()
    gc.collect()
    return [ssid,pswd]


def clockSetup(ss,pw):
    global ntpFlag
    # set fecha/hora por protocolo NTP
    s=network.WLAN(network.STA_IF)
    s.active(True)
    s.connect (ss,pw)
    n=10 
    while s.status()!=network.STAT_GOT_IP and n>0:
        n-=1
        sleep (1)
    ntpFlag=False
    if s.isconnected():       
        ok=False
        n=5
        print("** Get time from net",end="")
        while not ok and n>0:
            try:
                ntptime.settime()
                ok=True
            except:
                print (".",end="")
                n-=1
                ok=False
                sleep(1)
        ntpFlag=(n>0)
        s.disconnect()
    if ntpFlag:
        print ("\n** clock OK")
    else:
        print ("\n** clock down")
    t=localtime()
    print("** UTC time %2d-%02d-%04d %2d:%02d:%02d" %(t[2],t[1],t[0],t[3],t[4],t[5]))
    

def load_config():
    global cfg
    # factory reset
    Factory_reset_Pin= Pin(cfg['touchstoppin'], Pin.IN, Pin.PULL_UP)
    if Factory_reset_Pin()==0: # dos lecturas del pin a 0.5 seg
        sleep (0.5)
        if Factory_reset_Pin()==0:
            print ("\n** Factory reset. Default assumed **")
            with  open('config.json', 'w') as f:
                json.dump(cfg, f)
                f.close()
            print ("*** Release 'Fact Reset' pin ***")
            while Factory_reset_Pin()==0:
                sleep (0.2)
            return
    try:
        with  open('config.json', 'r') as f:
            cfg1 = json.load(f)
            f.close()
        if abs(cfg1["Version"]-cfg["Version"])<1: # si versiones difieren en menos de 1 => la misma cfguración
            with  open('config.json', 'r') as f:
                cfg = json.load(f)
                f.close()
            print ("\n** Loading stored conf **")
        else: # ha cambiado la version es el entero, grabar la nueva por defecto
            with  open('config.json', 'w') as f:
                json.dump(cfg, f)
                f.close()
            print ("\n** Conf file to default val **")
    except:
        with  open('config.json', 'w') as f:
            json.dump(cfg, f)
            f.close()
        print ("\n** No conf file. Get def val.**")

# returns available wifi nets as a list (ssid,passw,rssi)
# first element is the most powerfull (if any)
def FiltraSSID():
    g2=[]
    good=[]
    if not cfg['wifi']:
        return []
    for ss,pw in cfg['ssidx']:
        s=network.WLAN(network.STA_IF)
        s.active(True)
        s.connect (ss,pw)
        n=10 
        st=s.status()
        while st!=network.STAT_GOT_IP and n>0:
            n-=1
            sleep (1)
            st=s.status()
        if s.isconnected():
            if not [ss,pw] in good:
                g2.append([ss,pw,s.status('rssi')])
            s.disconnect()
    g2=sorted(g2,key=lambda x:x[2], reverse=True)
    for i in range(len(g2)):
        if not (g2[i][0],g2[i][1]) in good:
            good.append((g2[i][0],g2[i][1]))
    return good


def AddNewSSID():
    s,p=WiFiSetup()                              # programar  uno
    if s!=None:                                  # se ha entrado un ssid correctamente  
        cfg['ssidx']=[(s,p)]+cfg['ssidx']        # ponerlo al principio de la lista
        if len(cfg['ssidx'])>cfg['nmaxlan']:     # si la lista sobrepasa el màximo, quitar el último
            cfg['ssidx']=cfg['ssidx'][1:]
        with  open('config.json', 'w') as f:     # escribir en FLASH la nueva configuración
            json.dump(cfg, f)
            f.close()
        print ("New SSID added %s  %s"%(s,p))
    print ("** SYSTEM REBOOT IN 10 SEC")
    sleep (10)
    reset()                         # RESET y BOOT de nuevo. El sistema arrancará con la primera ssid
    
# --------------------
# MAIN LOOP
#---------------------

async def mainProgram(client):
    global cfg, Run, station, WiFi, blinklevel, fifo, tfifo, mqttFlag, ntpFlag
    global display, haysensor, i2c, vspi, adc, s11, temp, hum, co2, oled, uart, mensaje
    global StpSwt,GfxSwt,sensor, semMQTT,rssi, mqtt_queue, estableCO2
    global WatchDogFlag ,WatchDogRun
    tvoc=0
# connect
    mqttFlag=cfg["mqtt"] and WiFi
    if mqttFlag:
        n=1
        ok=False
        while n<3 and not ok:
            try:
                await client.connect()
                ok=True
            except OSError:
                print('Connection failed.',n)
                await asyncio.sleep (2)
                n+=1
                
        mqttFlag=ok
        if ok:
            asyncio.create_task (mqttSend())

# touchpads
    if cfg['touchpad']:
        GfxSwt=TouchPad(Pin(cfg['touchpin']))

    # inicializa displays y sensores
    haysensor=True
    display=True
    if cfg['displaytype']=="TFT":
        vspi = SoftSPI(baudrate=80000000, polarity=1, phase=0, sck=Pin(cfg['SPI_SCK']), mosi=Pin(cfg['SPI_MOSI']), miso=Pin(cfg['SPI_MISO']))
#        tft = st7789.ST7789(vspi, 240, 240,    dc=Pin(cfg['SPI_DC'],Pin.OUT), reset=Pin(cfg['SPI_RES'],Pin.OUT), cs=Pin(cfg['SPI_CS'],Pin.OUT), backlight=Pin(4, Pin.OUT))
        tft = st7789.ST7789(vspi, 240, 240,    dc=Pin(cfg['SPI_DC'],Pin.OUT), reset=Pin(cfg['SPI_RES'],Pin.OUT), backlight=Pin(cfg['TFT_BACK'], Pin.OUT))
#        backlight=Pin(cfg['TFT_BACK'], Pin.OUT); backlight.value(1)
        print ("** Display type: TFT")
    else:
        vspi = SoftSPI(baudrate=80000000, polarity=0, phase=0, bits=8, firstbit=SoftSPI.MSB, sck=Pin(cfg['SPI_SCK']), mosi=Pin(cfg['SPI_MOSI']), miso=Pin(cfg['SPI_MISO']))
        oled=sh1106.SH1106_SPI( 128, 64, vspi, dc=Pin(cfg['SPI_DC']), res=Pin(cfg['SPI_RES']), cs=Pin(cfg['SPI_CS']))
        print ("** Display type: OLED")

    adc = ADC(Pin(cfg["BATERIA"]))                     # instancia entrada A/D en pin 34
    if display and cfg['displaytype']!="TFT":
        gfx = GFX(128, 64, oled.pixel)              # instancia gestor gráfico
        
    if cfg['TIPOLECTOR']=='DHT11':
        s11=dht.DHT11(Pin(cfg["TEMPERATURA"]))         # instancia sensor temperatura DHT22
        for i in range(2):
            s11.measure()
            temp=s11.temperature()
            hum=s11.humidity()
        if (temp<5 and hum<5) or (temp>100 and hum>100):
            cfg['TIPOLECTOR']=='DHT22'
            s11=dht.DHT22(Pin(cfg["TEMPERATURA"]))
    else:
        s11=dht.DHT22(Pin(cfg["TEMPERATURA"]))
    s11.measure()
    temp=s11.temperature()
    hum=s11.humidity()
        
    # logo
    if display :
        if cfg['displaytype']=="TFT":
            ini_tft(tft,cfg['sensorCO2'])
            await asyncio.sleep (2)
        else:
            oled.fill(0)
            write15 = Write(oled, ubuntu_mono_15)  
            write20 = Write(oled, ubuntu_mono_20)
            ini_oled(oled,write20,write15)
            gc.collect()
            logo(oled)
            tx=time()
            write20.text("Medidor"  ,60, 0)
            write20.text("de CO2"   ,60,16)
            write15.text("R.Carreno",60,34)
            write15.text("L.Bayo"   ,60,46)
            oled.pixel (110,37,1); oled.pixel (111,37,1); oled.pixel (112,37,1); oled.pixel (113,37,1) # Ñ
            oled.pixel ( 99,49,1); oled.pixel (100,48,1); oled.pixel (101,47,1) # Ó
            try:
                oled.show()
                Copyright(oled)
            except:
                display=False
                print ("-- Error writing OLED display. OLED disabled")
            await asyncio.sleep (2)
            ini_oled(oled,write20,write15)
            
    gc.collect()         

    print ("\n** Medidor CO2 . Version "+str(cfg["Version"])+"  "+cfg["VersionDate"]+" **")
    
     # set CO2 sensor
    uart=UART(1, baudrate=9600, tx=cfg['tx'],rx=cfg['rx'])
    set_autocero_MH_Z19B(cfg['autocero'])


    # bucle principal 
    t_old=-1
    count=0
    grafic=False
    init=True
    dg=cfg['debug']
    asyncio.create_task(WatchDog())
    tx=time_ns()
    # bucle principal 
    while Run:
        if dg & 2:
            print ("t0:%12.3f"%((time_ns()-tx)/1E6)); tx=time_ns()
        WatchDogFlag=1
        if  mqttFlag and not client.isconnected():
            try:
                await client.connect()
            except OSError:
                print('Connection failed.')
                mqttFlag=False
 
        gc.collect()
        
        # muestra carga batería
        if dg & 2:
            print ("t1:%12.3f"%((time_ns()-tx)/1E6)); tx=time_ns()
        # HORA ACTUAL
        t=localtime()
        t=Hz(t[0]%100,t[1],t[2],t[3],t[4],t[5])
        if t[4]!=t_old:  # ejecutar si cambia de minuto
            if WiFi:
                if ntpFlag:
                    s="%2d-%02d-%02d %2d:%02d"%(t[2],t[1],t[0]%100,t[3],t[4])
                    if display and cfg['displaytype']!="TFT":
                        write15.text(s, 0, 0)
            else:
                if display and cfg['displaytype']!="TFT":
                    write15.text("No WiFi", 0, 0)
            t_old=t[4]
        if dg & 2:
            print ("t2:%12.3f"%((time_ns()-tx)/1E6)); tx=time_ns()
                
        #lectura temperatura y humedad (sensor en pin 33)
        try:
            s11.measure(); await robin()
            temp=s11.temperature()
            hum=s11.humidity()
            tfifo.append(temp)
            hfifo.append(hum)
            if len(tfifo)>cfg["NMAX_MEDIDAS"]:
                tfifo.pop(0)
                hfifo.pop(0)
            temp,testable=media(tfifo);  await robin()
            hum ,hestable =media(hfifo); await robin()
        except:
            print ("----DHT fail")
            pass         
        if dg & 2:        
            print ("t3:%12.3f"%((time_ns()-tx)/1E6)); tx=time_ns()
        
        # lectura CO² y TVOC
        co2=sensorReady(cfg['sensorCO2'])
        if count % cfg['xinter']==0:
            plot(co2,pt)
        count+=1
        if not cfg['touchpad']:
            if count % 10 ==0:
                grafic= not grafic
                if not grafic:
                    if display and cfg['displaytype']!="TFT":
                        ini_oled(oled,write20,write15)
#                    else:
#                        ini_tft (tft)
        if dg & 2:
            print ("t4:%12.3f"%((time_ns()-tx)/1E6)); tx=time_ns()
        # visualizar datos
        if display:
            if cfg['displaytype']!="TFT":
                if grafic:
                    await robin()
                    do_grafic(oled,write15,pt,st7789.color565(115,115,115),st7789.color565(255,0,0))
                else:
                    txt="%4d%c"%(co2 ,estableCO2)
#                    write20.text(txt, 48, 12)
                    segments.texto(txt,oled,32,18,6)
                    await robin()
                    txt="%4.1f"%temp ; write15.text(txt, 16, 52)
                    txt="%2d"%(hum)  ; write15.text(txt,100, 52)
                    show_rssi(oled,110,0,-199,1,0)
                    await robin()
                    show_rssi(oled,110,0,rssi,1,0)
                    oled.show()
            else:
                if co2<cfg['VENTVALOR'][0]:
                    cl=st7789.GREEN
                elif co2<cfg['VENTVALOR'][1]:
                    cl=st7789.YELLOW
                else:
                    cl=st7789.RED

                await robin()
                do_grafic(tft,None,pt,st7789.WHITE,cl)
                if estableCO2==cfg["WARMUP"]:
                    msg="WARM UP"
                elif estableCO2==cfg["NOESTABLE"]:
                    msg="NO ESTABLE"
                else:
                    msg="   ESTABLE"
                await robin()
                tft_display(tft,cfg['sensorCO2'],"%2d.%02d.%02d"%(t[2],t[1],t[0]),"%2d:%02d"%(t[3],t[4]),"%5.1f"%temp,"%4d"%hum,"%5d"%co2,"%5d"%tvoc,msg)
                await robin()
                show_rssi(tft,20,160,rssi,st7789.BLUE,st7789.color565(115,115,115))
        if dg & 2:
            print ("t5:%12.3f"%((time_ns()-tx)/1E6)); tx=time_ns()

        # enviar por mqtt y por salida
        s="%2d-%02d-%02d %2d:%02d:%02d"%(t[2],t[1],t[0]%100,t[3],t[4],t[5])
        fan2=fan if cfg["AvisoVent"] else "   "
        msg=s+" eCO2:%4d ppm"%co2+" TVOC:%4d ppb"%tvoc+" Temp: %2dC  Hum:%2d%%"%(temp,hum)+" bateria:%2d"%nivel()+" fan:"+fan2
        if cfg["VERBOSE"]:
            print (msg)
        automata_ventilacion(init); init=False
        if cfg['AvisoNivel']:
            automata_avisos()
        if WiFi and mqttFlag:
            if client.isconnected():
                tpub=cfg["prefijo"]+cfg["topic_pub"]
                mqtt_queue.append((tpub, msg))
                if mensaje>"":
                    tmsg=cfg["prefijo"]+cfg["topic_msg"]
                    mqtt_queue.append((tmsg, mensaje))
                    mensaje=""
        if dg & 2:
            print ("t6:%12.3f"%((time_ns()-tx)/1E6)); tx=time_ns()
        await asyncio.sleep (cfg["PAUSA"])
#        await pausa(cfg["PAUSA"])
    print ("*"*14+"\n System STOP\n"+"*"*14)
    await asyncio.sleep(3) 

#-----------------------------------------------------------
# ROUTINES AUXILIARES DE WiFi y MQTT

async def conn_han(client): 
    tsub=cfg["prefijo"]+cfg["topic_sub"]
    tmsg=cfg["prefijo"]+cfg["topic_msg"]
    await client.subscribe(tsub, cfg['qos'])
#    await client.subscribe(tmsg, cfg['qos'])

async def wifi_han(state):
    global outages
#    wifi_led(not state)  # Light LED when WiFi down
    if state:
        print('We are connected to broker.')
    else:
        outages += 1
        print('WiFi or broker is down.')
    await asyncio.sleep(1)
    
async def get_rssi():
    global rssi
    s = network.WLAN()
    ssid = config['ssid'].encode('UTF8')
    nets= s.scan()
    while True:
        try:
            tx=time_ns()
            rssi = [x[3] for x in nets if x[0] == ssid][0]
            if cfg['debug'] & 2:
                print ("rssi:%12.3f  rssi:%4d db"%((time_ns()-tx)/1E6, rssi)); 
        except:
            rssi = -199
        await asyncio.sleep(10)

async def WatchDog():
    global WatchDogFlag
    WatchDogFlag=1
    while WatchDogRun:
        await asyncio.sleep (cfg['watchdogtime'])  # 30 segundos
        if not WatchDogFlag:
            print ("***Watchdog reset***")
            reset()
        WatchDogFlag=0

def FastBlinkAndWaitKey():
    led = Pin(cfg["ledpin"], Pin.OUT)
    tecla=TouchPad(Pin(cfg['touchpin']))
    t0=time()
    r1=False
    ld=1
    print ("Wait for touchpad (15 sec)" )
    while (time()-t0)<15:
        sleep (0.1)
        led.value(ld); ld=1-ld
        r0=r1
        r1=(tecla.read()<cfg['touchlevel'])
        if (r1 and r0):
            led.value(0)
            return 1
    led.value(0)
    return 0


#-------------------------------------------
#  MAIN BLOCK
#-------------------------------------------

# Globals
WiFi=False
station=None
grfstate=0
fan="OFF"
s=""
fifo=[]
tfifo=[]
tStart=0  # hora de arranque
estableCO2=cfg["NOESTABLE"]
tx=time()
mensaje=""
uart=None
oled=None
sensor=None
pt=[]
write15=None
write20=None
auth=('open','WEP','WPA-PSK','WPA2-PSK','WPA/WPA2-PSK')
visible=('visible','hidden')
blinklevel=0                                # nivel de blink segun CO2
fifo=[]                                     # fifo de medidas
tfifo=[]                                    # fifo de temperaturas
hfifo=[]
mqttFlag= False
ntpFlag= False
client=None
client_id = ubinascii.hexlify(unique_id())         # id client (ESP-32 Id number)
display=None
temp=0
hum=0
co2=0
uart=None
StpSwt,GfxSwt=None, None
gc.collect()
semMQTT=False
outages=0
rssi=-199
WatchDogFlag=True
response=" "*2000
gc.enable()

# configuration
load_config()
print ("\n** START **")
gc.collect()
freq(int(cfg["frecuencia"]*1E6)) #  Clock 

if cfg['wifi']:
    print ("** WiFi scanning. ")
    lans=FiltraSSID()
    if lans!=[]:
        WiFi=True
        config['ssid'], config['wifi_pw'] = lans[0]  # el de mayor potencia
    else:   # no se detecta wifi
        if FastBlinkAndWaitKey():
            print ("Connect to esys")
            AddNewSSID()
        else:
            WiFi=False
#     config['ssid'], config['wifi_pw'] = cfg["ssidx"][0]

Run=True

# Set up client. Enable optional debug statements.
mqttFlag=cfg['mqtt'] and WiFi

if mqttFlag :
# datos de configuracion dinámicos
    config['subs_cb'] = sub_cb                                    # callback routine -----> def sub_cb(topic, msg, retained)
    config['wifi_coro'] = wifi_han                                # SHOW WIFI STATUS -----> async def wifi_han(state)  
    config['will'] = (cfg["prefijo"]+cfg["topic_pub"], '', False, 0)             # mensaje de despedida
    config['connect_coro'] = conn_han                             # connect coroutine
    config['keepalive'] = 30                                     # timempo para considerar que una conexion está perdida
    config['server'] = cfg['server']   
    MQTTClient.DEBUG = True
    client = MQTTClient(config)

if WiFi:
    clockSetup(config['ssid'], config['wifi_pw'])
    asyncio.create_task(get_rssi())

tStart=time()
WatchDogRun=True
asyncio.create_task (ledblink())
asyncio.create_task (WatchStop())

try:
    asyncio.run(mainProgram(client))
finally:  # Prevent LmacRxBlk:1 errors.
    if mqttFlag:
        client.close()
    WatchDogRun=False
    asyncio.new_event_loop()
    print("*** PROGRAM STOP ***")

