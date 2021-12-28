from machine import Pin, SoftSPI
from time import sleep
#import st7789py as st7789
import st7789
import segments

logo=[
[0xffffffff,0xfffff800],
[0xffffffff,0xfffff800],
[0xffffffff,0xfffff800],
[0xffffffff,0xfffff800],
[0xffffffff,0xfffff800],
[0xffffffff,0xfffff000],
[0xfe000000,0x0003f800],
[0xfe000000,0x0003f800],
[0xfe000003,0xf003f800],
[0xfe0000ff,0xfc03f800],
[0xfe000fff,0xfe03f800],
[0xfe007fff,0xfe03f800],
[0xfe01ffff,0xfc03f800],
[0xfe03ffff,0xf803f800],
[0xfe07ffff,0xf003f800],
[0xfe0fffff,0xe003f800],
[0xfe0fffff,0x8003f800],
[0xfe07fffc,0x0003f800],
[0xfe03ffc0,0x0003f800],
[0xfe00fc00,0x0003f800],
[0xfe000000,0x0003f800],
[0xfe000003,0xf003f800],
[0xfe0000ff,0xfc03f800],
[0xfe000fff,0xfe03f800],
[0xfe007fff,0xfe03f800],
[0xfe01ffff,0xfc03f800],
[0xfe03ffff,0xf803f800],
[0xfe07ffff,0xf003f800],
[0xfe0fffff,0xe003f800],
[0xfe0fffff,0x8003f800],
[0xfe07fffc,0x0003f800],
[0xfe03ffc0,0x0003f800],
[0xfe00fc00,0x0003f800],
[0xfe000000,0x0003f800],
[0xfe000003,0xf003f800],
[0xfe0000ff,0xfc03f800],
[0xfe000fff,0xfe03f800],
[0xfe007fff,0xfe03f800],
[0xfe01ffff,0xfc03f800],
[0xfe03ffff,0xf803f800],
[0xfe07ffff,0xf003f800],
[0xfe0fffff,0xe003f800],
[0xfe0fffff,0x8003f800],
[0xfe07fffc,0x0003f800],
[0xfe03ffc0,0x0003f800],
[0xfe00fc00,0x0003f800],
[0xfe000000,0x0003f800],
[0xfe000000,0x0003f800],
[0xffffffff,0xfffff800],
[0xffffffff,0xfffff800],
[0xffffffff,0xfffff800],
[0xffffffff,0xfffff800],
[0xffffffff,0xfffff800],
[0xffffffff,0xfffff800],
]
fecha0=""; hora0=""; temp0=""; hum0=""; co20=""; tvoc0=""; msg0=""

def text(display, font, message, row=32, column=0, color=st7789.WHITE):
    '''
    Write `text` on `display` starting at `row`,`column` using
    the `font` file in `color`

    Args:
        display: The display device to write on
        font: The font file to use
        message (str): The message to write
        row: Row to start at, defaults to 32
        column: Column to start at, defaults to 0
        color: The color to write in
    '''
    from_x = to_x = pos_x = column
    from_y = to_y = pos_y = row

    with open(font, "rb", buffering=0) as file:
        characters = int.from_bytes(file.read(2), 'little')
        if characters > 96:
            begins = 0x00
            ends = characters
        else:
            begins = 0x20
            ends = characters + 0x20

        for char in [ord(char) for char in message]:
            penup = True
            if begins <= char <= ends:
                file.seek((char-begins+1)*2)
                file.seek(int.from_bytes(file.read(2), 'little'))
                length = ord(file.read(1))
                left, right = file.read(2)

                left -= 0x52            # Position left side of the glyph
                right -= 0x52           # Position right side of the glyph
                width = right - left    # Calculate the character width

                for vect in range(length):
                    vector_x, vector_y = file.read(2)
                    vector_x -= 0x52
                    vector_y -= 0x52

                    if vector_x == -50:
                        penup = True
                        continue

                    if not vect or penup:
                        from_x = pos_x + vector_x - left
                        from_y = pos_y + vector_y

                    else:
                        to_x = pos_x + vector_x - left
                        to_y = pos_y + vector_y

                        display.line(from_x, from_y, to_x, to_y, color)

                        from_x = to_x
                        from_y = to_y

                    penup = False

                pos_x += width


def logo_tft(tft,x,y):
    for y in range (len(logo)):
        k=logo[y][0]
        l=logo[y][1]
        m=0x80000000
        for x in range (32):        
            if k&m :
                tft.pixel (x,y,st7789.GREEN)
            m=m >>1
        m=0x80000000
        for x in range (32):        
            if l&m :
                tft.pixel (x+32,y,st7789.GREEN)
            m=m >>1
    
def ini_tft(tft,sensor):
    tft.init()
    tft.fill_rect(  0,  0,240, 60,st7789.color565(  0,  0,155))
    tft.fill_rect(  0, 60,240,120,st7789.color565(115,115,115))
    tft.fill_rect(  0,180,239, 60,st7789.color565(155,  0,  0))
    #fecha
    #titulos
    text (tft, 'lib/tft/romancs.fnt', "CO2"               , 90,  2,st7789.color565(115,  0, 0))
    text (tft, 'lib/tft/romancs.fnt', "ppm"               ,110,  2,st7789.color565(115,  0, 0))
    if sensor=="CCS811":
        text (tft, 'lib/tft/romancs.fnt', "tVOC"              ,150,  2,st7789.color565(  0,255,255))
        text (tft, 'lib/tft/romancs.fnt', "ppb"               ,150,180,st7789.color565(  0,255,255))
    text (tft, 'lib/tft/romancs.fnt', "T:     C Hum:   %",220,  2,st7789.color565(  0,255,255))
    logo_tft(tft,1,1)
    
def tft_display(tft,sensor,fecha,hora,temp,hum,co2,tvoc,msg):
    global fecha0, hora0, co20,tvoc0, temp0, hum0, estable0,msg0
    if fecha!=fecha0:
        text (tft, 'lib/tft/romancs.fnt', fecha0       , 10,135,st7789.color565(  0,  0,155))
        text (tft, 'lib/tft/romancs.fnt', fecha        , 10,135,st7789.color565(  0,255,255)); fecha0=fecha
    if hora!=hora0:
        text (tft, 'lib/tft/romancs.fnt', hora0        , 35,150,st7789.color565(  0,  0,155))
        text (tft, 'lib/tft/romancs.fnt', hora         , 35,150,st7789.color565(  0,255,255)); hora0=hora
    if co20!=co2:
#        text (tft, 'lib/tft/romant.fnt' , co20         , 90, 80,st7789.color565(115,115,115)) 
#        text (tft, 'lib/tft/romant.fnt' , co2          , 90, 80,st7789.color565(255,255,255)); co20=co2ç
        segments.texto (co2, tft, x0=70, y0=80, size=16, cf=st7789.color565(255,255,255), cb=st7789.color565(115,115,115),TipoOled=False)
        if msg0!=msg:
            text (tft, 'lib/tft/romancs.fnt',msg0,160,60,st7789.color565(115,115,115))
            text (tft, 'lib/tft/romancs.fnt',msg ,160,60,st7789.color565(  0,255,255)) ;msg0=msg
    if sensor=="CCS811":
        if tvoc0!=tvoc:    
            text (tft, 'lib/tft/romant.fnt' , tvoc0        ,150, 80,st7789.color565(115,115,115))
            text (tft, 'lib/tft/romant.fnt' , tvoc         ,150, 80,st7789.color565(255,255,255)) ; tvoc0=tvoc
    if temp0!=temp:
        text (tft, 'lib/tft/romancs.fnt', temp0        ,220, 20,st7789.color565(155,  0,  0))
        text (tft, 'lib/tft/romancs.fnt', temp         ,220, 20,st7789.color565(255,255,255)); temp0=temp
    if hum0!=hum:
        text (tft, 'lib/tft/romancs.fnt', hum0         ,220,155,st7789.color565(155,  0,  0))
        text (tft, 'lib/tft/romancs.fnt', hum          ,220,155,st7789.color565(255,255,255)); hum0=hum

wifi_db=[[0x0180,0x03c0,0x03c0,0x180],[0x0ff0,0x1ff8,0x0c30,0x0000],[0x1ff8, 0x7ffe, 0xfc3f,0x6006]]
old_rssi=0



def show_rssi(tft,x0,y0,valor,cf,cb):
    global old_rssi
    def wifilogo(tft,x0,y0,dat,cf):
        for y in range (len(dat)):
            k=dat[y]
            m=0x8000
            for x in range (16):        
                if k&m :
                    tft.pixel (x+x0,y+y0,cf)
                m=m >>1
            
    n=0
    if valor>-60:
        n=3
    elif valor>-70:
        n=2
    elif valor>-80:
        n=1
    if n!=old_rssi:
        if old_rssi==3:
            wifilogo(tft,x0,y0,wifi_db[2],cb)
        if n==3:
            wifilogo (tft,x0,y0,wifi_db[2],cf)
        if old_rssi>=2:
            wifilogo(tft,x0,6+y0,wifi_db[1],cb)
        if n>=2:
            wifilogo (tft,x0, 6+y0,wifi_db[1],cf)
        if old_rssi>=1:
            wifilogo(tft,x0,12+y0,wifi_db[0],cb)
        if n>=1:
            wifilogo (tft,x0,12+y0,wifi_db[0],cf)
    old_rssi=n



def main():
    tft = st7789.ST7789(
        SoftSPI( baudrate=80000000, polarity=1, phase=0, sck=Pin(19), mosi=Pin(21), miso=Pin(0)),
        240,
        240,
        reset=Pin(5, Pin.OUT),
        dc=Pin(17, Pin.OUT),
        cs=Pin(16, Pin.OUT),
        backlight=Pin(4, Pin.OUT))


    ini_tft(tft,None)

    #CO2, tVOC

    while 1:
        fecha="12-06-21"
        hora="16:56"
        temp="  24.6"
        hum ="   47"
        co2 =" 1234"
        tvoc="   45"
        tft_display(tft,None,fecha,hora,temp,hum,co2,tvoc)
        sleep (1)
        fecha="15-06-21"
        hora="10:56"
        temp="  23.6"
        hum ="   49"
        co2 =" 1004"
        tvoc="   46"
        tft_display(tft,None,fecha,hora,temp,hum,co2,tvoc)
        sleep (1)

if __name__=="__main__":
    main()
    