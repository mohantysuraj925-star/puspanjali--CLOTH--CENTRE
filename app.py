import os,sqlite3,json,sys,uuid,re
from datetime import datetime,timedelta
from functools import wraps
from flask import *
from werkzeug.security import generate_password_hash as gh, check_password_hash as ch
B=os.path.dirname(os.path.abspath(__file__));U=os.path.join(B,'uploads');os.makedirs(U,exist_ok=True)
app=Flask(__name__);app.config['MAX_CONTENT_LENGTH']=300*1024*1024
SK=os.path.join(B,'.secret')
if not os.path.exists(SK):open(SK,'w').write(uuid.uuid4().hex)
app.secret_key=open(SK).read();app.jinja_env.filters['j']=json.loads
DB=os.path.join(B,'shop.db')
SCH="""create table if not exists settings(k text primary key,v text);
create table if not exists cats(id integer primary key,name text unique);
create table if not exists products(id integer primary key,name text,brand text,mrp real,disc real,price real,cid integer,descr text,fabric text,sizes text,stock integer,active integer default 1);
create table if not exists media(id integer primary key,pid integer,f text,kind text);
create table if not exists users(id integer primary key,uid text unique,name text,phone text,email text,pw text);
create table if not exists wish(uid integer,pid integer,primary key(uid,pid));
create table if not exists orders(id integer primary key,uid integer,name text,phone text,address text,items text,total real,pay text,paystat text,status text default 'New',at text default current_timestamp);"""
DEF={'shop_name':'Puspanjali Cloth Store','tagline':'Shop online. Reserve it. Collect in store.','phone':'9337988950','email':'mohantysuraj91@gmail.com','whatsapp':'919337988950','address':'Khatiguda, Navrangpur, Indravati, near Maa Santoshi Maa Mandir','hours':'9:00 AM - 9:00 PM','open_hour':'9','close_hour':'21','hold_days':'2','daily_max':'30','credit_pct':'10','about':'Puspanjali Cloth Store is our own clothing shop in Navrangpur. Sarees, lehengas, kurtis, menswear and kidswear, all under one roof.','story':'Big online platforms mostly sell other brands. At Puspanjali you buy straight from our own brand: shop-floor quality, fair prices with no middleman. Browse and save your favourites here, reserve with a part or full payment, and collect from our store.','delivery_note':'Not collected within the hold period? We can deliver to your home for an extra charge based on your location.'}
def init():
    c=sqlite3.connect(DB);c.executescript(SCH)
    for t,col in [('wish','price0 real'),('orders','code text'),('orders','hold_until text'),('orders','paid real'),('orders','balance real'),('orders','dfee real default 0'),('orders','mode text'),('orders','daddr text'),('users','credit real default 0'),('users','streak integer default 0'),('users','last_claim text'),('orders','credit_used real default 0')]:
        try:c.execute("alter table "+t+" add column "+col)
        except:pass
    for k,v in DEF.items():c.execute("insert or ignore into settings values(?,?)",(k,v))
    c.execute("insert or ignore into settings values('admin_user','ADMIN1234')")
    c.execute("insert or ignore into settings values('admin_hash',?)",(gh('ADMIN'),));c.commit();c.close()
def db():
    if 'd' not in g:g.d=sqlite3.connect(DB);g.d.row_factory=sqlite3.Row
    return g.d
@app.teardown_appcontext
def cl(e):
    d=g.pop('d',None)
    if d:d.close()
def q(s,a=(),one=False):
    r=db().execute(s,a).fetchall()
    return (r[0] if r else None) if one else r
def ex(s,a=()):
    c=db().execute(s,a);db().commit();return c.lastrowid
def st():return {r['k']:r['v'] for r in q("select * from settings")}
IMG="(select f from media where pid=p.id and kind='image' order by id limit 1)"
@app.context_processor
def ctx():
    s=st();s.pop('admin_hash',None)
    w=set(r['pid'] for r in q("select pid from wish where uid=?",(session['u'],))) if session.get('u') else set()
    me=q("select * from users where id=?",(session['u'],),True) if session.get('u') else None
    return dict(ME=me,TODAY=datetime.now().strftime('%Y-%m-%d'),YEST=(datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d'),NOW=datetime.now().strftime('%Y-%m-%d %H:%M'),S=s,CATS=q("select * from cats order by name"),UN=session.get('un'),W=w,mu=lambda f:f if f.startswith('http') else '/uploads/'+f)
def adm(f):
    @wraps(f)
    def w(*a,**k):
        if not session.get('a'):return redirect('/admin/login')
        return f(*a,**k)
    return w
def nx():
    n=request.args.get('next') or request.form.get('next') or '/account'
    return n if n.startswith('/') and not n.startswith('//') else '/account'
def fee(t):
    s=st();return 0 if t>=float(s['delivery_min']) else float(s['delivery_fee'])
@app.route('/manifest.json')
def man():return jsonify(name=st()['shop_name'],short_name='Puspanjali',start_url='/',display='standalone',background_color='#09090f',theme_color='#09090f',icons=[dict(src='/icon.svg',sizes='any',type='image/svg+xml')])
@app.route('/icon.svg')
def icon():return Response('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff7ab8"/><stop offset=".5" stop-color="#6fe3ff"/><stop offset="1" stop-color="#e9c46a"/></linearGradient></defs><rect width="48" height="48" rx="12" fill="#09090f"/><g fill="none" stroke="url(#g)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M24 15a3.2 3.2 0 1 0-3.2-3.2"/><path d="M24 15v3.5L10 29.5a2.6 2.6 0 0 0 1.6 4.7h24.8a2.6 2.6 0 0 0 1.6-4.7L24 18.5"/></g></svg>',mimetype='image/svg+xml')
@app.route('/uploads/<f>')
def up(f):return send_from_directory(U,f)
def pick():
    r=q("select p.*,"+IMG+" img from products p where active=1 and stock>0 order by id")
    return r[datetime.now().toordinal()%len(r)] if r else None
@app.route('/')
def home():
    s=request.args.get('q','');c=request.args.get('c','')
    sql="select p.*,"+IMG+" img from products p where active=1";a=[]
    if s:sql+=" and (name like ? or brand like ?)";a+=['%'+s+'%']*2
    if c:sql+=" and cid=?";a.append(c)
    occ=request.args.get('occ','').strip()
    if occ:
        ts=[x for x in occ.split(',') if x];sql+=" and ("+" or ".join(["descr like ? or name like ?"]*len(ts))+")";a+=sum([['%'+x+'%']*2 for x in ts],[])
    mx=request.args.get('max','').strip()
    if mx.isdigit():sql+=" and price<=?";a.append(int(mx))
    o={'low':' order by price','high':' order by price desc','off':' order by disc desc'}.get(request.args.get('s'),' order by id desc')
    return render_template('home.html',P=q(sql+o,a),N=q('select p.*,'+IMG+' img from products p where active=1 order by id desc limit 8'),PK=pick())
@app.route('/product/<int:i>')
def product(i):
    p=q("select * from products where id=? and active=1",(i,),True) or abort(404)
    R=q("select p.*,"+IMG+" img from products p where active=1 and cid=? and id!=? limit 4",(p['cid'],i))
    return render_template('product.html',p=p,R=R,M=q("select * from media where pid=? order by id",(i,)))
@app.route('/about')
def about():return render_template('page.html',pg='about')
@app.route('/contact')
def contact():return render_template('page.html',pg='contact')
@app.route('/cart')
def cart():return render_template('cart.html')
@app.route('/register',methods=['GET','POST'])
def register():
    e=''
    if request.method=='POST':
        f=request.form;u=re.sub(r'\s','',f['uid']).upper()
        if not re.fullmatch(r'[A-Z0-9_]{4,20}',u):e='User ID must be 4-20 characters: A-Z, 0-9 or _ (no spaces)'
        elif u==st()['admin_user'] or q("select 1 from users where uid=?",(u,)):e='This User ID is already taken'
        elif len(f['pw'])<6:e='Password must be at least 6 characters'
        elif not re.fullmatch(r'\d{10}',f['phone'].strip()):e='Enter a 10-digit phone number'
        elif '@' not in f['email']:e='Enter a valid email'
        else:
            i=ex("insert into users(uid,name,phone,email,pw) values(?,?,?,?,?)",(u,f['name'].strip(),f['phone'].strip(),f['email'].strip().lower(),gh(f['pw'])))
            session['u']=i;session['un']=f['name'].split()[0];return redirect(nx())
    return render_template('auth.html',reg=True,e=e)
@app.route('/login',methods=['GET','POST'])
def login():
    e=''
    if request.method=='POST':
        u=q("select * from users where uid=?",(re.sub(r'\s','',request.form['uid']).upper(),),True)
        if u and ch(u['pw'],request.form['pw']):session['u']=u['id'];session['un']=u['name'].split()[0];return redirect(nx())
        e='Incorrect User ID or password'
    return render_template('auth.html',reg=False,e=e)
def nxs(n):
    return n if n and n.startswith('/') and not n.startswith('//') else '/account'
@app.post('/api/login')
def apilogin():
    j=request.get_json(silent=True) or {};uid=re.sub(r'\s','',str(j.get('uid',''))).upper();pw=str(j.get('pw',''));s=st()
    if uid==s['admin_user'] and ch(s['admin_hash'],pw.strip()):
        session['a']=1;session.permanent=True;print('[login] admin OK');return jsonify(ok=True,to='/admin')
    u=q("select * from users where uid=?",(uid,),True)
    if u and ch(u['pw'],pw):
        session['u']=u['id'];session['un']=u['name'].split()[0];session.permanent=True;print('[login] customer OK',uid);return jsonify(ok=True,to=nxs(j.get('next')))
    print('[login] FAILED uid=',uid,'| reason:','no such user' if not u else 'wrong password');return jsonify(ok=False,msg='Incorrect User ID or password'),401
@app.route('/api/me')
def apime():return jsonify(admin=bool(session.get('a')),user=bool(session.get('u')))
@app.post('/api/claim')
def apiclaim():
    if not session.get('u'):return jsonify(ok=False,msg='Please log in first'),401
    u=q("select * from users where id=?",(session['u'],),True);today=datetime.now().strftime('%Y-%m-%d');yest=(datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d')
    if u['last_claim']==today:return jsonify(ok=False,msg='Already claimed today. Come back tomorrow!')
    sk=((u['streak'] or 0)+1) if u['last_claim']==yest else 1
    rw=min(float(st().get('daily_max') or 30),5*min(sk,6))
    ex("update users set credit=coalesce(credit,0)+?,streak=?,last_claim=? where id=?",(rw,sk,today,u['id']))
    return jsonify(ok=True,reward=rw,streak=sk,credit=(u['credit'] or 0)+rw)
@app.route('/logout')
def logout():session.pop('u',None);session.pop('un',None);return redirect('/')
@app.route('/account')
def account():
    if not session.get('u'):return redirect('/login')
    return render_template('account.html',u=q("select * from users where id=?",(session['u'],),True),O=q("select * from orders where uid=? order by id desc",(session['u'],)))
@app.route('/wishlist')
def wishlist():
    if not session.get('u'):return redirect('/login?next=/wishlist')
    return render_template('wish.html',P=q("select p.*,"+IMG+" img,w.price0 from products p join wish w on w.pid=p.id where w.uid=? and p.active=1",(session['u'],)))
@app.post('/api/wish/<int:i>')
def apiwish(i):
    u=session.get('u')
    if not u:return jsonify(ok=False),401
    if q("select 1 from wish where uid=? and pid=?",(u,i)):ex("delete from wish where uid=? and pid=?",(u,i));return jsonify(on=False)
    p=q("select price from products where id=?",(i,),True)
    ex("insert into wish(uid,pid,price0) values(?,?,?)",(u,i,p['price'] if p else 0));return jsonify(on=True)
@app.post('/order/<int:i>/delivery')
def reqdel(i):
    o=q("select * from orders where id=? and uid=?",(i,session.get('u')),True);ad=request.form.get('addr','').strip()
    if o and ad and o['status'] in('Reserved','Ready for pickup'):ex("update orders set mode='delivery',daddr=?,status='Delivery requested' where id=?",(ad,i))
    return redirect('/account')
@app.post('/api/cart')
def apicart():
    o=[]
    for k,n in (request.json or {}).items():
        i,_,s=k.partition('|')
        p=q("select p.id,name,mrp,price,stock,"+IMG+" img from products p where id=? and active=1",(i,),True)
        if p:d=dict(p);d.update(key=k,size=s,qty=max(1,int(n)));o.append(d)
    return jsonify(o)
@app.route('/checkout')
def checkout():
    if not session.get('u'):return redirect('/login?next=/checkout')
    return render_template('checkout.html',u=q("select * from users where id=?",(session['u'],),True))
@app.post('/api/checkout')
def apicheckout():
    if not session.get('u'):return jsonify(ok=False,msg='Please log in first'),401
    j=request.json;L=[];t=0;need={}
    for k,n in j['items'].items():
        i,_,s=k.partition('|');n=max(1,int(n))
        p=q("select * from products where id=? and active=1",(i,),True)
        if not p:continue
        need[p['id']]=need.get(p['id'],0)+n
        if p['stock']<need[p['id']]:return jsonify(ok=False,msg=p['name']+': not enough stock'),400
        L.append(dict(id=p['id'],name=p['name'],size=s,price=p['price'],qty=n));t+=p['price']*n
    if not L:return jsonify(ok=False,msg='Your bag is empty'),400
    if not (j.get('name') and j.get('phone')):return jsonify(ok=False,msg='Name and phone are required'),400
    cu=0
    if j.get('credit'):
        me=q("select credit from users where id=?",(session['u'],),True);cu=max(0,min(int(me['credit'] or 0),round(t*float(st().get('credit_pct') or 10)/100)));t-=cu
    pay=j.get('pay') if j.get('pay') in('half','full') else 'full';paid=round(t/2) if pay=='half' else t
    code=str(uuid.uuid4().int)[:6];hold=(datetime.now()+timedelta(days=int(st().get('hold_days') or 2))).strftime('%Y-%m-%d %H:%M')
    oid=ex("insert into orders(uid,name,phone,address,items,total,pay,paystat,status,code,hold_until,paid,balance,mode) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(session['u'],j['name'],j['phone'],'',json.dumps(L),t,pay.upper(),'Paid (Demo)','Reserved',code,hold,paid,t-paid,'pickup'))
    for i,n in need.items():ex("update products set stock=stock-? where id=?",(n,i))
    if cu:ex("update users set credit=credit-? where id=?",(cu,session['u']));ex("update orders set credit_used=? where id=?",(cu,oid))
    return jsonify(ok=True,id=oid)
@app.route('/order/<int:i>')
def success(i):
    o=q("select * from orders where id=? and uid=?",(i,session.get('u')),True)
    return render_template('success.html',o=o) if o else redirect('/account')
@app.route('/admin/login',methods=['GET','POST'])
def alogin():
    e=''
    if request.method=='POST':
        s=st()
        if re.sub(r'\s','',request.form['u']).upper()==s['admin_user'] and ch(s['admin_hash'],request.form['pw'].strip()):session['a']=1;return redirect('/admin')
        e='Incorrect User ID or password'
    return render_template('alogin.html',e=e)
@app.route('/admin/logout')
def alogout():session.pop('a',None);return redirect('/')
@app.route('/admin')
@adm
def dash():
    c=lambda s:q(s,one=True)[0]
    return render_template('admin.html',pg='dash',st=dict(p=c("select count(*) from products"),o=c("select count(*) from orders"),n=c("select count(*) from orders where status='Reserved'"),u=c("select count(*) from users"),r=c("select coalesce(sum(total),0) from orders where status!='Cancelled'")),O=q("select o.*,u.uid uu from orders o left join users u on u.id=o.uid order by o.id desc limit 5"))
@app.route('/admin/products')
@adm
def aprods():return render_template('admin.html',pg='prods',P=q("select p.*,"+IMG+" img from products p order by id desc"))
@app.route('/admin/product/<i>',methods=['GET','POST'])
@adm
def pform(i):
    p=None if i=='new' else q("select * from products where id=?",(i,),True)
    if request.method=='POST':
        f=request.form;mrp=float(f['mrp'] or 0);pr=float(f['price'] or 0)
        if pr<=0:pr=mrp
        d=round((mrp-pr)/mrp*100,1) if mrp>0 and mrp>pr else 0
        v=(f['name'],f.get('brand',''),mrp,d,pr,f.get('cid') or None,f['descr'],f.get('fabric',''),f.get('sizes',''),int(f['stock'] or 0),1 if f.get('active') else 0)
        if p:ex("update products set name=?,brand=?,mrp=?,disc=?,price=?,cid=?,descr=?,fabric=?,sizes=?,stock=?,active=? where id=?",v+(p['id'],));pid=p['id']
        else:pid=ex("insert into products(name,brand,mrp,disc,price,cid,descr,fabric,sizes,stock,active) values(?,?,?,?,?,?,?,?,?,?,?)",v)
        for fl in request.files.getlist('media'):
            if fl and fl.filename:
                e=fl.filename.rsplit('.',1)[-1].lower();n=uuid.uuid4().hex+'.'+e;fl.save(os.path.join(U,n))
                ex("insert into media(pid,f,kind) values(?,?,?)",(pid,n,'video' if e in('mp4','webm','mov','mkv') else 'image'))
        for l in f.get('urls','').splitlines():
            l=l.strip()
            if l.startswith('http'):ex("insert into media(pid,f,kind) values(?,?,?)",(pid,l,'video' if l.lower().split('?')[0].endswith(('.mp4','.webm')) else 'image'))
        return redirect('/admin/products')
    return render_template('admin.html',pg='pform',p=p,M=q("select * from media where pid=?",(p['id'],)) if p else [])
@app.route('/admin/media/<int:i>/del')
@adm
def mdel(i):
    m=q("select * from media where id=?",(i,),True)
    if m:
        if not m['f'].startswith('http'):
            try:os.remove(os.path.join(U,m['f']))
            except:pass
        ex("delete from media where id=?",(i,));return redirect('/admin/product/%d'%m['pid'])
    return redirect('/admin/products')
@app.route('/admin/product/<int:i>/del')
@adm
def pdel(i):
    for m in q("select * from media where pid=?",(i,)):
        if not m['f'].startswith('http'):
            try:os.remove(os.path.join(U,m['f']))
            except:pass
    ex("delete from media where pid=?",(i,));ex("delete from wish where pid=?",(i,));ex("delete from products where id=?",(i,));return redirect('/admin/products')
@app.route('/admin/cats',methods=['GET','POST'])
@adm
def acats():
    if request.method=='POST' and request.form.get('name','').strip():ex("insert or ignore into cats(name) values(?)",(request.form['name'].strip(),))
    return render_template('admin.html',pg='cats')
@app.route('/admin/cat/<int:i>/del')
@adm
def cdel(i):ex("delete from cats where id=?",(i,));ex("update products set cid=null where cid=?",(i,));return redirect('/admin/cats')
@app.route('/admin/orders',methods=['GET','POST'])
@adm
def aord():
    if request.method=='POST':
        f=request.form;o=q("select * from orders where id=?",(f['id'],),True)
        if o:
            if f['s']=='Cancelled' and o['status']!='Cancelled':
                for l in json.loads(o['items']):ex("update products set stock=stock+? where id=?",(l['qty'],l['id']))
                if o['credit_used']:ex("update users set credit=credit+? where id=?",(o['credit_used'],o['uid']))
            ex("update orders set status=?,dfee=? where id=?",(f['s'],float(f.get('dfee') or 0),f['id']))
    c=request.args.get('code','').strip()
    return render_template('admin.html',pg='orders',O=q("select o.*,u.uid uu from orders o left join users u on u.id=o.uid"+(" where o.code=?" if c else "")+" order by o.id desc",(c,) if c else ()))
@app.route('/admin/users')
@adm
def ausers():return render_template('admin.html',pg='users',US=q("select u.uid,(select count(*) from orders where uid=u.id) n from users u order by u.id desc"))
@app.route('/admin/settings',methods=['GET','POST'])
@adm
def aset():
    if request.method=='POST':
        for k in DEF:ex("insert or replace into settings values(?,?)",(k,request.form.get(k,'')))
        u=re.sub(r'\s','',request.form.get('admin_user','')).upper()
        if u:ex("insert or replace into settings values('admin_user',?)",(u,))
        if len(request.form.get('newpw',''))>=6:ex("insert or replace into settings values('admin_hash',?)",(gh(request.form['newpw']),))
        return redirect('/admin/settings')
    return render_template('admin.html',pg='set',KEYS=list(DEF))
def seed(wipe=False):
    init();c=sqlite3.connect(DB)
    if wipe:
        for t in('products','media','cats','wish'):c.execute("delete from "+t)
    if c.execute("select count(*) from products").fetchone()[0]:print('Products already exist');return
    for n in ['Sarees','Lehengas','Kurtis & Suits','Menswear','Kidswear','Shawls & Dupattas']:c.execute("insert or ignore into cats(name) values(?)",(n,))
    ids={r[1]:r[0] for r in c.execute("select * from cats")};X='S,M,L,XL';K='2-3Y,4-5Y,6-7Y,8-9Y'
    for n,m,d,cat,de,fa,sz,sk in [
    ('Banarasi Silk Saree',4999,20,'Sarees','Royal zari-border Banarasi saree for weddings and festivals.','Banarasi Silk','',15),
    ('Cotton Handloom Saree',1499,20,'Sarees','Light, breathable handloom saree for everyday elegance.','Pure Cotton','',30),
    ('Georgette Party Saree',2299,25,'Sarees','Flowy georgette saree with sequin work for parties.','Georgette','',12),
    ('Bridal Embroidered Lehenga',12999,20,'Lehengas','Heavy embroidered bridal lehenga set with dupatta.','Velvet & Net',X,6),
    ('Printed Lehenga Choli',4499,20,'Lehengas','Vibrant printed lehenga for haldi and sangeet.','Crepe',X,10),
    ('Anarkali Kurti Set',1999,20,'Kurtis & Suits','Flared anarkali kurti with pants and dupatta.','Rayon',X+',XXL',25),
    ('Straight Cotton Kurti',999,20,'Kurtis & Suits','Straight-fit cotton kurti for daily wear.','Cotton',X+',XXL',40),
    ('Punjabi Salwar Suit',2199,20,'Kurtis & Suits','Ready-to-wear salwar suit with matching dupatta.','Cotton Blend',X,18),
    ('Mens Cotton Kurta Pajama',1799,20,'Menswear','Soft cotton kurta pajama set for festive days.','Cotton','M,L,XL,XXL',20),
    ('Mens Formal Shirt',1199,20,'Menswear','Full-sleeve formal shirt for office and functions.','Cotton Blend','38,40,42,44',35),
    ('Slim Fit Jeans',1899,25,'Menswear','Stretchable slim-fit jeans for everyday comfort.','Denim','30,32,34,36',28),
    ('Nehru Jacket',2499,20,'Menswear','Stylish Nehru jacket to layer over a kurta.','Silk Blend','M,L,XL',14),
    ('Sherwani Set',7999,20,'Menswear','Royal sherwani with churidar for the big day.','Jacquard','M,L,XL',5),
    ('Girls Party Frock',1299,20,'Kidswear','Pretty net party frock for little girls.','Net & Cotton lining',K,20),
    ('Boys Ethnic Kurta Set',1099,20,'Kidswear','Festive kurta set for young boys.','Cotton',K,22),
    ('Pashmina Shawl',1999,20,'Shawls & Dupattas','Soft embroidered shawl for winter.','Pashmina Blend','',16),
    ('Embroidered Dupatta',699,20,'Shawls & Dupattas','A dupatta that matches any suit.','Chiffon','',45)]:
        c.execute("insert into products(name,brand,mrp,disc,price,cid,descr,fabric,sizes,stock,active) values(?,?,?,?,?,?,?,?,?,?,1)",(n,'Puspanjali',m,d,round(m*(100-d)/100),ids[cat],de,fa,sz,sk))
    c.commit();print('Sample products added')
if __name__=='__main__':
    init();x=sys.argv[1] if len(sys.argv)>1 else ''
    if x=='seed':seed()
    elif x=='reseed':seed(True)
    else:app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)),threaded=True)
