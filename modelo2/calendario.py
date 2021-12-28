#--------------------------------------------
# retorna la data del diumenge de pasqua (mes i dia) de l'any x
def DiumengePasqua(x):
    a = x%19
    b = x%4
    c = x%7
    d = (19*a+24)%30
    e = (2*b+4*c+6*d+5)%7
    f = 22+d+e
    g = f%31
    if f<=31:
        return 3,g
    else:
        return 4,g
    
#-------------------------------------------------------
# congruencia de Zeller
# devuelve el dia de la semana (0:domingo, 1:lunes, ... etc)
def Zeller(anno,mes,dia):
    if mes<=2:
        mes+=10
        anno-=1
    else:
        mes-=2
    a = anno % 100;
    b = anno // 100;
    resultado = (700 +((26*mes-2)//10)+dia+a+a//4+b//4-2*b)%7;
    return resultado;

#----------------------------------
# devuelve la fecha/hora UTC de cambio a horario de verano
def cambioaverano(ano):
    dia = 31 - Zeller(ano, 3,31) # último domingo de marzo
    return "%02d/%02d/%02d 01:00:00"%(ano%100, 3,dia)
    
#----------------------------------
# devuelve la fecha/hora UTC de cambio a horario de invierno
def cambioainvierno(ano):
    dia = 31 - Zeller(ano, 10,31) # ultimo domingo de octubre
    return "%02d/%02d/%02d 01:00:00"%(ano%100,10,dia)
    
# ---------------------------------------------------
# retorna el dia siguiente de uno dado
def diasiguiente (d,m,a):
    d+=1
    if d<=28:
        return d,m,a
    if m in [1,3,5,7,8,10,12]:
        if d>31:
            d=1
            m+=1
            if m>12:
                m=1
                a+=1
    elif m in [4,6,9,11]:
        if d>30:
            d=1
            m+=1
    else:
        if a%4==0:
            if d>29:
                d=1
                m=3
        else:
            if d>28:
                d=1
                m=3
    return d,m,a

#------------------------------------------------
# devuelve la fecha/hora local, para una hora UTC
def Hz(a,m,dd,h,mm,s):
#    try:
        # añoç
        horautc="%02d/%02d/%02d %02d:%02d:%02d"%(a%100,m,dd,h,mm,s)
        verano=(horautc>=cambioaverano(a) and horautc<cambioainvierno(a)) # mirar si es verano o invierno
        # el formato de ["HORARIO"]["VERANO"]  es "+0100" (comillas incluidas), decalaje en horas y minutos respecto Greenwich
        if verano:
            dh=2
        else:
            dh=1
        h+=dh
        if h>=24:
            h=h%24
            dd,m,a=diasiguiente(dd,m,a)
        return a%100,m,dd,h,mm,s
#    except:
        return 0,0,0,0,0,0

