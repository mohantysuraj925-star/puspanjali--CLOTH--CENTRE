import sqlite3,os
G='#e2b84a';os.makedirs('uploads',exist_ok=True)
def hs(h,s,l):return 'hsl(%d,%d%%,%d%%)'%(h%360,s,l)
SP0={'jeans':(215,45,38),'shirt':(205,45,74),'sherwani':(38,45,64),'jacket':(190,42,30)}
SP1={'jeans':(225,22,20),'shirt':(345,45,76),'sherwani':(350,55,30),'jacket':(30,45,28)}
def kind(n):
    n=n.lower()
    for k,ws in [('sherwani',['sherwani']),('kidskurta',['boys']),('frock',['frock','girls']),('lehenga',['lehenga']),('saree',['saree']),('kurti',['kurti','anarkali','suit']),('shawl',['shawl']),('dupatta',['dupatta']),('jeans',['jeans']),('jacket',['jacket']),('kurta',['kurta']),('shirt',['shirt'])]:
        if any(w in n for w in ws):return k
    return 'shirt'
def pal(k,pid,v):
    t=(SP0 if v==0 else SP1).get(k);h,s,l=t if t else ((pid*47+v*58)%360,58,40)
    return hs(h,s,l),hs(h+38,62,58),hs(h,70,93),hs(h+28,60,82)
def B(d,c):return f'<path d="{d}" fill="{c}" stroke="rgba(0,0,0,.2)" stroke-width="2.5" stroke-linejoin="round"/><path d="{d}" fill="url(#p)"/>'
def dots(x,y0,gap,n,r,c):return ''.join(f'<circle cx="{x}" cy="{y0+i*gap}" r="{r}" fill="{c}"/>' for i in range(n))
def f_shirt(c1,c2):
    s=B("M200 170 L262 148 Q300 195 338 148 L400 170 L472 252 L432 302 L396 270 L396 650 L204 650 L204 270 L168 302 L128 252 Z",c1)
    s+=f'<path d="M262 148 L300 218 L252 205 Z M338 148 L300 218 L348 205 Z" fill="{c2}" stroke="rgba(0,0,0,.2)" stroke-width="2"/><path d="M300 218V650" stroke="rgba(0,0,0,.25)" stroke-width="3"/>'
    return s+dots(300,260,62,6,6,'#fff')+'<rect x="318" y="300" width="50" height="60" rx="4" fill="none" stroke="rgba(0,0,0,.22)" stroke-width="3"/>'
def f_jeans(c1,c2):
    s=B("M205 140 H395 L412 700 H314 L300 345 L286 700 H188 Z",c1)
    s+=f'<rect x="205" y="140" width="190" height="42" fill="{c2}" fill-opacity=".3"/><path d="M300 182V345" stroke="rgba(0,0,0,.3)" stroke-width="3"/><circle cx="300" cy="162" r="9" fill="{G}"/>'
    s+=f'<path d="M215 190Q250 260 285 200M385 190Q350 260 315 200" fill="none" stroke="{G}" stroke-width="3" stroke-dasharray="8 6"/>'
    return s+''.join(f'<rect x="{x}" y="132" width="14" height="38" rx="4" fill="{c1}" stroke="rgba(0,0,0,.25)"/>' for x in (222,262,324,364))
def f_kurti(c1,c2):
    s=B("M222 160 L268 138 Q300 180 332 138 L378 160 L418 228 L384 262 L372 238 L442 692 L158 692 L228 238 L216 262 L182 228 Z",c1)
    s+=f'<path d="M268 138 Q300 180 332 138" fill="none" stroke="{G}" stroke-width="7"/><path d="M300 178V330" stroke="{G}" stroke-width="5"/><path d="M163 672 L437 672" stroke="{G}" stroke-width="8"/><path d="M168 650 L432 650" stroke="{c2}" stroke-width="6" stroke-dasharray="3 12" stroke-linecap="round"/>'
    return s+dots(300,200,40,3,6,G)
def f_lehenga(c1,c2):
    s=B("M248 244 L352 244 L478 692 Q300 730 122 692 Z",c1)+B("M236 150 L270 134 Q300 164 330 134 L364 150 L386 216 L352 240 L248 240 L214 216 Z",c2)
    s+=f'<path d="M248 244H352" stroke="{G}" stroke-width="10"/><path d="M180 640 Q300 668 420 640 M160 600 Q300 632 440 600" fill="none" stroke="{G}" stroke-width="7"/>'
    P="M364 150 Q440 290 340 440 T 420 690"
    return s+f'<path d="{P}" fill="none" stroke="{c2}" stroke-width="30" stroke-linecap="round" opacity=".9"/><path d="{P}" fill="none" stroke="{G}" stroke-width="4" stroke-dasharray="10 8"/>'
def f_saree(c1,c2):
    s=B("M228 138 L270 128 Q300 152 330 128 L372 138 L398 222 L384 648 Q300 705 216 648 L202 222 Z",c1)
    s+=f'<path d="M234 146 H330 L398 300 V470 L260 300 Z" fill="{c2}" stroke="{G}" stroke-width="5" opacity=".92"/><path d="M216 640 Q300 700 384 640" fill="none" stroke="{G}" stroke-width="10"/><path d="M206 600 Q300 660 394 600" fill="none" stroke="{G}" stroke-width="3" stroke-dasharray="6 8"/><path d="M270 330 L250 640 M312 330 L322 650" stroke="rgba(0,0,0,.14)" stroke-width="4"/>'
    return s+B("M228 138 L270 128 Q300 152 330 128 L372 138 L398 222 L366 232 L234 232 L202 222 Z",c2)
def f_frock(c1,c2):
    s=B("M242 262 L358 262 L482 660 Q300 722 118 660 Z",c1)+'<path d="M150 600 Q225 640 300 600 T450 600" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="6"/>'
    s+=B("M258 150 L276 134 Q300 152 324 134 L342 150 L356 262 L244 262 Z",c2)+f'<path d="M258 150 L252 106 M342 150 L348 106" stroke="{c2}" stroke-width="8" stroke-linecap="round"/>'
    return s+f'<path d="M300 262 L262 240 L262 284 Z M300 262 L338 240 L338 284 Z" fill="{G}"/><circle cx="300" cy="262" r="11" fill="{G}"/>'
def f_jacket(c1,c2):
    s=B("M208 152 L262 132 Q300 168 338 132 L392 152 L414 252 L398 652 L202 652 L186 252 Z",c1)
    s+=f'<path d="M262 132 Q300 168 338 132 L338 108 Q300 138 262 108 Z" fill="{c2}" stroke="rgba(0,0,0,.2)" stroke-width="2"/><path d="M300 165V652" stroke="{G}" stroke-width="5"/><path d="M222 470H272M328 470H378" stroke="rgba(0,0,0,.3)" stroke-width="5"/>'
    return s+dots(300,240,70,5,8,G)
def f_sherwani(c1,c2):
    s=B("M212 152 L264 132 Q300 168 336 132 L388 152 L458 262 L422 314 L398 288 L408 712 L192 712 L202 288 L178 314 L142 262 Z",c1)
    s+=f'<path d="M264 132 Q300 168 336 132 L336 108 Q300 138 264 108 Z" fill="{G}"/><path d="M300 168V712" stroke="{G}" stroke-width="12"/><path d="M194 690H406M196 660H404" stroke="{G}" stroke-width="7"/>'
    return s+''.join(f'<circle cx="300" cy="{215+i*62}" r="8" fill="{c2}" stroke="{G}" stroke-width="3"/>' for i in range(8))
def f_kurta(c1,c2):
    s=B("M212 156 L264 134 Q300 172 336 134 L388 156 L452 262 L418 312 L398 284 L406 712 L194 712 L202 284 L182 312 L148 262 Z",c1)
    s+=f'<path d="M264 134 Q300 172 336 134" fill="none" stroke="{G}" stroke-width="8"/><path d="M300 172V380" stroke="{G}" stroke-width="10"/><path d="M196 690H404" stroke="{G}" stroke-width="7"/>'
    return s+dots(300,205,42,4,6,c2)
def f_shawl(c1,c2):
    s=B("M100 190 Q300 120 500 190 L524 620 Q300 690 76 620 Z",c1)+f'<path d="M92 560 Q300 626 508 560 M90 590 Q300 656 510 590" fill="none" stroke="{G}" stroke-width="8"/>'
    s+=''.join('<path d="M%d %d l-2 34" stroke="%s" stroke-width="4" stroke-linecap="round"/>'%(76+448*i/32,620+140*(i/32)*(1-i/32),c2) for i in range(33))
    return s+''.join(f'<path d="M{150+i*75} 300 q18 -34 36 0 q-18 34 -36 0" fill="{c2}" fill-opacity=".55"/>' for i in range(5))
def f_dupatta(c1,c2):
    P="M170 140 C440 230 160 420 420 560 C470 600 400 690 330 710"
    return f'<path d="{P}" fill="none" stroke="{G}" stroke-width="150" stroke-linecap="round"/><path d="{P}" fill="none" stroke="{c1}" stroke-width="132" stroke-linecap="round"/><path d="{P}" fill="none" stroke="url(#p)" stroke-width="132" stroke-linecap="round"/><path d="{P}" fill="none" stroke="{c2}" stroke-width="100" stroke-linecap="round" stroke-dasharray="2 26" opacity=".85"/>'
FN={'shirt':f_shirt,'jeans':f_jeans,'kurti':f_kurti,'lehenga':f_lehenga,'saree':f_saree,'frock':f_frock,'jacket':f_jacket,'sherwani':f_sherwani,'kurta':f_kurta,'kidskurta':f_kurta,'shawl':f_shawl,'dupatta':f_dupatta}
PT=['<path d="M0 7h14" stroke="#fff" stroke-opacity=".16" stroke-width="3"/>','<circle cx="8" cy="8" r="2.2" fill="#fff" fill-opacity=".3"/>','<path d="M12 2L22 12 12 22 2 12Z" fill="none" stroke="#f3d27a" stroke-opacity=".6" stroke-width="1.5"/>','<path d="M0 0H18M0 0V18" stroke="#fff" stroke-opacity=".14" stroke-width="3"/>']
SZ=[14,16,24,18]
def svg(name,pid,v):
    k=kind(name);c1,c2,b1,b2=pal(k,pid,v);st=(pid+v)%4;g=FN[k](c1,c2)
    if k=='kidskurta':g='<g transform="translate(300 140) scale(.82) translate(-300 -140)">'+g+'</g>'
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 800"><defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient><pattern id="p" width="%d" height="%d" patternUnits="userSpaceOnUse">%s</pattern><filter id="tx" x="0" y="0" width="100%%" height="100%%" color-interpolation-filters="sRGB"><feTurbulence type="fractalNoise" baseFrequency=".85 .6" numOctaves="3" seed="4" result="n1"/><feDiffuseLighting in="n1" surfaceScale="1.4" lighting-color="#fff" result="l1"><feDistantLight azimuth="225" elevation="60"/></feDiffuseLighting><feTurbulence type="fractalNoise" baseFrequency=".007 .035" numOctaves="2" seed="9" result="n2"/><feDiffuseLighting in="n2" surfaceScale="11" lighting-color="#fff" result="l2"><feDistantLight azimuth="200" elevation="52"/></feDiffuseLighting><feComposite in="l1" in2="l2" operator="arithmetic" k1="1.25" k2="0" k3="0" k4="0" result="lm"/><feComposite in="SourceGraphic" in2="lm" operator="arithmetic" k1="1.15" k2="0" k3="0" k4="0" result="m"/><feComposite in="m" in2="SourceAlpha" operator="in"/></filter><filter id="sh" x="-20%%" y="-20%%" width="140%%" height="150%%"><feDropShadow dx="0" dy="14" stdDeviation="14" flood-color="#000" flood-opacity=".28"/></filter></defs><rect width="600" height="800" fill="url(#bg)"/><circle cx="470" cy="150" r="190" fill="#fff" fill-opacity=".35"/><circle cx="90" cy="700" r="150" fill="#fff" fill-opacity=".25"/><path d="M300 112V94a14 14 0 1 0-14-14M300 112L168 176M300 112L432 176" fill="none" stroke="#8a7a70" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/><g filter="url(#sh)"><g filter="url(#tx)">%s</g></g><text x="584" y="782" text-anchor="end" font-family="sans-serif" font-size="15" fill="#000" fill-opacity=".35" letter-spacing="2">DEMO IMAGE</text></svg>')%(b1,b2,SZ[st],SZ[st],PT[st],g)
db=sqlite3.connect('shop.db')
for pid,name in db.execute("select id,name from products").fetchall():
    if db.execute("select count(*) from media where pid=? and f not like 'demo_%'",(pid,)).fetchone()[0]:print('skip (asli photo hai):',name);continue
    db.execute("delete from media where pid=? and f like 'demo_%'",(pid,))
    for v in (0,1):
        f='demo_%d_%d.svg'%(pid,v);open('uploads/'+f,'w',encoding='utf-8').write(svg(name,pid,v))
        db.execute("insert into media(pid,f,kind) values(?,?,'image')",(pid,f))
    print('OK  ',name)
db.commit()
