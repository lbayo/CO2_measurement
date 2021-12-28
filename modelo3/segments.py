 # display 7 segments

def digit (x0,y0,n,l,oled,cf,cb):
    
    # segmento horizontal en x0 y0 de longitud l en el display dsp color k
    def segmentH(x0,y0,l,dsp,k):
        w=5 if l>6 else 3  # ancho del segmento
        o=0 if l>6 else 1  # offet para compensar anchura
        dsp.fill_rect(x0+5, y0+o, l, w, k)
        dsp.pixel (x0+4,y0+1,k); dsp.pixel (x0+4,y0+2,k); dsp.pixel (x0+4,y0+3,k)
        dsp.pixel (x0+3,y0+2,k)
        dsp.pixel (x0+l+5,y0+1,k); dsp.pixel (x0+l+5,y0+2,k); dsp.pixel (x0+l+5,y0+3,k)
        dsp.pixel (x0+l+6,y0+2,k)

    def segmentV(x0,y0,l,dsp,k):
        w=5 if l>4 else 3
        o=0 if l>4 else 1
        dsp.fill_rect(x0+o, y0+2, w, l, k)
        dsp.pixel (x0+1,y0+1,k); dsp.pixel (x0+2,y0+1,k); dsp.pixel (x0+3,y0+1,k)
        dsp.pixel (x0+2,y0  ,k)
        dsp.pixel (x0+1,y0+l+2,k); dsp.pixel (x0+2,y0+l+2,k); dsp.pixel (x0+3,y0+l+2,k)
        dsp.pixel (x0+2,y0+l+3,k)

    def point(x0,y0,l,dsp,k):
        dsp.pixel(x0+l+7,y0+4,k)
        dsp.pixel(x0+l+8,y0+4,k)
        dsp.pixel(x0+l+7,y0+5,k)
        dsp.pixel(x0+l+8,y0+5,k)
    '''
          ---e---
          |      |
          a      c
          |      |
          ---f---
          |      |
          b      d
          |      |
          ---g---
    '''
    def a(k):
        segmentV( 0+x0, 3+y0,l+l//2,oled,k)
    def b(k):
        segmentV( 0+x0,8+l+l//2+y0,l+l//2,oled,k)
    def c(k):
        segmentV(5+l+x0, 3+y0,l+l//2,oled,k)
    def d(k):
        segmentV(5+l+x0,8+l+l//2+y0,l+l//2,oled,k)
    def e(k):
        segmentH( 0+x0, 0+y0,l,oled,k)
    def f(k):
        segmentH( 0+x0,10+3*l+y0,l,oled,k)
    def g(k):
        segmentH( 0+x0,5+l+l//2+y0,l,oled,k)
        
    if n=='0':
        a(cf); b(cf); c(cf); d(cf); e(cf); f(cf); g(cb)
    elif n=='1':
        a(cb); b(cb); c(cf); d(cf); e(cb); f(cb); g(cb)
    elif n=='2':
        a(cb); b(cf); c(cf); d(cb); e(cf); f(cf); g(cf)
    elif n=='3':
        a(cb); b(cb); c(cf); d(cf); e(cf); f(cf); g(cf)
    elif n=='4':
        a(cf); b(cb); c(cf); d(cf); e(cb); f(cb); g(cf)
    elif n in ['5',"s","S"]:
        a(cf); b(cb); c(cb); d(cf); e(cf); f(cf); g(cf)
    elif n=='6':
        a(cf); b(cf); c(cb); d(cf); e(cf); f(cf); g(cf)
    elif n=='7':
        a(cb); b(cb); c(cf); d(cf); e(cf); f(cb); g(cb)
    elif n=='8':
        a(cf); b(cf); c(cf); d(cf); e(cf); f(cf); g(cf)
    elif n=='9':
        a(cf); b(cb); c(cf); d(cf); e(cf); f(cb); g(cf)
    elif n=='9':
        a(cf); b(cb); c(cf); d(cf); e(cf); f(cb); g(cf)
    elif n==' ':
        a(cb); b(cb); c(cb); d(cb); e(cb); f(cb); g(cb)
    elif n in ['a','A']:
        a(cf); b(cf); c(cf); d(cf); e(cf); f(cb); g(cf)
    elif n in ['b','B']:
        a(cf); b(cf); c(cb); d(cf); e(cb); f(cf); g(cf)
    elif n in ['c','C']:
        a(cf); b(cf); c(cb); d(cb); e(cf); f(cf); g(cb)
    elif n in ['d','D']:
        a(cb); b(cf); c(cf); d(cf); e(cb); f(cf); g(cf)
    elif n in ['e','E']:
        a(cf); b(cf); c(cb); d(cb); e(cf); f(cf); g(cf)
    elif n in ['f','F']:
        a(cf); b(cf); c(cb); d(cb); e(cf); f(cb); g(cf)
    elif n in ['h','H']:
        a(cf); b(cf); c(cb); d(cf); e(cb); f(cb); g(cf)
    elif n in ['i','I']:
        a(cb); b(cb); c(cb); d(cf); e(cb); f(cb); g(cb)
    elif n in ['j','J']:
        a(cb); b(cf); c(cf); d(cf); e(cb); f(cf); g(cb)
    elif n in ['l','L']:
        a(cf); b(cf); c(cb); d(cb); e(cb); f(cf); g(cb)
    elif n in ['n','N']:
        a(cb); b(cf); c(cb); d(cf); e(cb); f(cb); g(cf)
    elif n in ['ñ','Ñ']:
        a(cb); b(cf); c(cb); d(cf); e(cf); f(cb); g(cf)
    elif n in ['o','O']:
        a(cb); b(cf); c(cb); d(cf); e(cb); f(cf); g(cf)
    elif n in ['r','R']:
        a(cb); b(cf); c(cb); d(cb); e(cb); f(cb); g(cf)
    elif n in ['t','T']:
        a(cf); b(cf); c(cb); d(cb); e(cb); f(cf); g(cf)
    elif n in ['u','U']:
        a(cb); b(cf); c(cb); d(cf); e(cb); f(cf); g(cb)
    elif n in ['x','X']:
        a(cf); b(cf); c(cf); d(cf); e(cb); f(cb); g(cf)
    elif n in ['y','Y']:
        a(cf); b(cf); c(cf); d(cb); e(cb); f(cb); g(cf)
    elif n in ["z","Z"]:
        a(cb); b(cf); c(cf); d(cb); e(cf); f(cf); g(cf)
    elif n =="-":
        a(cb); b(cb); c(cb); d(cb); e(cb); f(cf); g(cb)
    else:
        a(cb); b(cb); c(cb); d(cb); e(cf); f(cf); g(cf)
        
def number(n,oled, x0=0,y0=0,size=10,cifras=4,cf=1,cb=0,TipoOled=False):
    n=n%(10**cifras)
    s=("%"+str(cifras)+"d")%n
    for i in range(cifras):
        digit (x0,y0,s[i],size,oled,cf,cb)
        x0+=(size+size//2)+9
    if TipoOled:
        oled.show()
            
def texto (s,oled,x0=0,y0=0,size=10,cf=1,cb=0,TipoOled=False):
    for i in range(len(s)):
        digit (x0,y0,s[i],size,oled,cf,cb)
        x0+=(size+size//2)+9
    if TipoOled:
        oled.show()


