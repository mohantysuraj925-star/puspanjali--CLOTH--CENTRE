import sqlite3,json,urllib.request,urllib.parse,uuid,os,sys
KEY=sys.argv[1] if len(sys.argv)>1 else ''
if not KEY:sys.exit('Use: python photos.py YOUR_PEXELS_KEY')
Q={'saree':'indian woman saree','lehenga':'indian bridal lehenga','kurti':'indian woman kurti','suit':'indian salwar suit','kurta':'indian man kurta','shirt':'man formal shirt','jeans':'man jeans fashion','jacket':'man nehru jacket','sherwani':'groom sherwani','frock':'little girl party dress','kids':'indian kids ethnic wear','shawl':'woman shawl','dupatta':'indian dupatta'}
def qy(n):
    n=n.lower()
    for k,v in Q.items():
        if k in n:return v
    return n
def get(u,h={}):
    return urllib.request.urlopen(urllib.request.Request(u,headers=dict({'User-Agent':'Mozilla/5.0'},**h)),timeout=40).read()
db=sqlite3.connect('shop.db');os.makedirs('uploads',exist_ok=True);used={}
for pid,name in db.execute("select id,name from products where id not in (select pid from media)").fetchall():
    try:
        q=qy(name);i=used.get(q,0);used[q]=i+1
        j=json.loads(get('https://api.pexels.com/v1/search?'+urllib.parse.urlencode({'query':q,'per_page':40,'orientation':'portrait'}),{'Authorization':KEY}))
        ph=j['photos'][i*2:i*2+2] or j['photos'][:2]
        for p in ph:
            f=uuid.uuid4().hex+'.jpg';open('uploads/'+f,'wb').write(get(p['src']['portrait']))
            db.execute("insert into media(pid,f,kind) values(?,?,'image')",(pid,f))
        db.commit();print('OK  ',name,len(ph),'photos')
    except Exception as e:print('FAIL',name,e)
