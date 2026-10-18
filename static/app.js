(function(){
var w=document.createElement('div');w.className='shw';w.innerHTML='<div class=shd></div>';document.body.appendChild(w);var d=w.firstChild;
function close(){w.classList.remove('on')}
w.addEventListener('click',function(e){if(e.target===w)close()});
function open(h,wire){d.innerHTML=h;wire(d);w.classList.add('on')}
function enh(s){if(s.dataset.enh)return;s.dataset.enh=1;s.style.display='none';var b=document.createElement('button');b.type='button';b.className='sel';
var t=function(){var o=s.options[s.selectedIndex];b.textContent=o?o.textContent:'Select'};t();s.parentNode.insertBefore(b,s.nextSibling);
b.onclick=function(){var p=s.previousElementSibling,lab=s.getAttribute('aria-label')||(p&&p.tagName=='LABEL'?p.textContent:'Choose');var h='<h4>'+lab+'</h4>';
for(var i=0;i<s.options.length;i++)h+='<button type=button class="op'+(i==s.selectedIndex?' on':'')+'" data-i="'+i+'">'+s.options[i].textContent+'</button>';
open(h,function(x){x.querySelectorAll('.op').forEach(function(o){o.onclick=function(){s.selectedIndex=+o.dataset.i;t();close();s.dispatchEvent(new Event('change',{bubbles:true}))}})})}}
document.addEventListener('click',function(e){var a=e.target.closest('[data-confirm]');if(!a)return;e.preventDefault();var href=a.getAttribute('href');
open('<h4>'+a.dataset.confirm+'</h4><div class=acts2><button type=button class="btn ghost" data-c>Cancel</button><button type=button data-y>Yes, continue</button></div>',function(x){x.querySelector('[data-c]').onclick=close;x.querySelector('[data-y]').onclick=function(){location=href}})});
document.querySelectorAll('select').forEach(enh)})();
window.pcLogin=function(f,next){f.addEventListener('submit',function(e){e.preventDefault();var b=f.querySelector('.go'),er=document.getElementById('er');
function bad(m){er.textContent=m;er.hidden=false;b.disabled=false;b.textContent='Log in';f.classList.remove('shk');void f.offsetWidth;f.classList.add('shk')}
b.disabled=true;b.textContent='Signing in...';er.hidden=true;
fetch('/api/login',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({uid:f.uid.value,pw:f.pw.value,next:next})}).then(function(r){return r.json()}).then(function(j){
if(!j.ok){bad(j.msg||'Login failed');return}
fetch('/api/me',{credentials:'same-origin'}).then(function(r){return r.json()}).then(function(m){
if(!(m.admin||m.user)){bad('Login worked, but your browser is not saving cookies. Please open this site in Chrome (not inside another app) and allow cookies.');return}
b.textContent='Welcome!';location=j.to})}).catch(function(){bad('Cannot reach the server. Is the app running in Termux?')})})};
