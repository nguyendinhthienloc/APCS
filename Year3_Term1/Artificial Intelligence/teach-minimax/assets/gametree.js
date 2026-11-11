// Reusable game-tree component.
// Tree spec: a number (leaf) or {t:'max'|'min', label?, c:[...children]}.
//
// GameTree.mount(el, spec, {mode:'practice'|'show'})
//   practice: every non-leaf gets an input; Check / Reveal / Reset buttons.
//   show: values filled in, chosen edges highlighted.
// GameTree.alphabeta(el, spec, {mode:'step'|'practice'})
//   step: Next / Back / Reset walk through alpha-beta (left to right), showing α, β, v.
//         countLeaves:true also shows how many leaves have been examined so far.
//   practice: click nodes to mark them pruned (✂); Check / Reveal / Reset.
(function(){
  const W=64, SVG='http://www.w3.org/2000/svg';
  const fmt=x=>x===Infinity?'+∞':x===-Infinity?'−∞':String(x);
  function build(s,depth,acc,parent){
    acc.maxD=Math.max(acc.maxD,depth);
    const id=acc.id++;
    if(typeof s==='number'){ const n={id,leaf:s,v:s,depth,x:acc.i++,parent}; acc.all.push(n); return n; }
    const n={id,t:s.t,label:s.label,depth,parent}; acc.all.push(n);
    n.kids=s.c.map(k=>build(k,depth+1,acc,n)); const vs=n.kids.map(k=>k.v);
    n.v=s.t==='max'?Math.max(...vs):Math.min(...vs); n.x=(n.kids[0].x+n.kids[n.kids.length-1].x)/2;
    return n;
  }
  function walk(n,f){ f(n); (n.kids||[]).forEach(k=>walk(k,f)); }

  // Draws the tree; nodeBody(n) returns inner HTML / element for each node.
  function draw(el,spec,nodeBody,H=86){
    const acc={i:0,maxD:0,id:0,all:[]}, root=build(spec,0,acc), w=acc.i*W, h=(acc.maxD+1)*H;
    el.classList.add('gt'); el.innerHTML='';
    const inner=document.createElement('div'); inner.className='gt-inner'; inner.style.width=w+'px'; inner.style.height=h+'px'; el.appendChild(inner);
    const svg=document.createElementNS(SVG,'svg'); svg.setAttribute('width',w); svg.setAttribute('height',h); inner.appendChild(svg);
    const px=n=>n.x*W+W/2, py=n=>n.depth*H+H/2;
    walk(root,n=>{
      (n.kids||[]).forEach(k=>{ const l=document.createElementNS(SVG,'line');
        l.setAttribute('x1',px(n)); l.setAttribute('y1',py(n)+10); l.setAttribute('x2',px(k)); l.setAttribute('y2',py(k)-14);
        l.setAttribute('stroke','currentColor'); l.setAttribute('stroke-opacity','.35'); l.setAttribute('stroke-width','1.5');
        k.edge=l; svg.appendChild(l); });
      const d=document.createElement('div'); d.className='gt-node '+(n.t||''); d.style.left=px(n)+'px'; d.style.top=py(n)+'px';
      if(n.leaf!==undefined) d.innerHTML='<span class="leaf">'+n.leaf+'</span>';
      else d.innerHTML='<span class="tri">'+(n.t==='max'?'▲':'▼')+'</span>';
      nodeBody(n,d); if(n.label) d.insertAdjacentHTML('beforeend','<span class="lbl">'+n.label+'</span>');
      n.el=d; inner.appendChild(d);
    });
    return {root,all:acc.all};
  }
  function toolbar(el,buttons){
    const bar=document.createElement('div'); bar.className='no-print';
    bar.innerHTML=buttons.map(b=>'<button data-a="'+b.toLowerCase()+'">'+b+'</button>').join('')+'<div class="gt-status"></div>';
    el.after(bar); return {bar,st:bar.querySelector('.gt-status')};
  }

  function mount(el,spec,opt={}){
    const show=opt.mode==='show', inputs=[];
    const {root}=draw(el,spec,(n,d)=>{ if(n.leaf!==undefined) return;
      if(show) d.insertAdjacentHTML('beforeend','<span class="val ok">'+n.v+'</span>');
      else { const inp=document.createElement('input'); inp.inputMode='numeric'; inp.setAttribute('aria-label',(n.label||n.t)+' value'); inp._v=n.v; d.appendChild(inp); inputs.push(inp); } });
    if(show){ (function mark(n){ if(!n.kids) return; n.kids.find(k=>k.v===n.v).edge.setAttribute('class','gt-edge-best'); n.kids.forEach(mark); })(root); return; }
    const {bar,st}=toolbar(el,['Check','Reveal','Reset']);
    bar.addEventListener('click',e=>{ const a=e.target.dataset.a; if(!a) return;
      if(a==='reset'){ inputs.forEach(i=>{i.value='';i.className='';}); st.textContent=''; return; }
      let ok=0, empty=0;
      inputs.forEach(i=>{ if(a==='reveal') i.value=i._v;
        if(i.value.trim()===''){ i.className=''; empty++; return; }
        const good=Number(i.value)===i._v; i.className=good?'ok':'bad'; if(good) ok++; });
      st.textContent = a==='reveal' ? 'Answers shown. Hit Reset and redo it from memory.'
        : ok===inputs.length ? '✓ All '+ok+' correct.'
        : ok+' / '+inputs.length+' correct'+(empty?' ('+empty+' empty)':'')+'. For red boxes: is that node ▲ (take max) or ▼ (take min)?';
    });
  }

  // Alpha-beta trace (AIMA 4e Fig. 5.7, children left to right).
  // Returns steps: snapshots of per-node {a,b,v,state} plus a message, and the set of cut nodes.
  function trace(root,all){
    let leaves=0;
    const S={}, steps=[], cut=new Set(), name=n=>n.label||(n.leaf!==undefined?'leaf '+n.leaf:(n.t==='max'?'▲':'▼'));
    const snap=(cur,msg)=>steps.push({cur:cur.id,msg,leaves,S:JSON.parse(JSON.stringify(S,(k,v)=>v===Infinity?'+∞':v===-Infinity?'−∞':v))});
    function rec(n,a,b){
      if(n.leaf!==undefined){ leaves++; S[n.id]={state:'done'}; snap(n,'Reach '+name(n)+' → return '+n.v+'.'); return n.v; }
      let v=n.t==='max'?-Infinity:Infinity; S[n.id]={a,b,v,state:'active'};
      snap(n,'Enter '+name(n)+' ('+(n.t==='max'?'MAX':'MIN')+') with α='+fmt(a)+', β='+fmt(b)+'.');
      for(let i=0;i<n.kids.length;i++){
        const r=rec(n.kids[i],a,b);
        if(n.t==='max'){ v=Math.max(v,r); a=Math.max(a,v); } else { v=Math.min(v,r); b=Math.min(b,v); }
        Object.assign(S[n.id],{a,b,v,state:'active'});
        const prune = n.t==='max' ? v>=b : v<=a, rest=n.kids.slice(i+1);
        if(prune && rest.length){
          rest.forEach(k=>{ cut.add(k.id); walk(k,d=>S[d.id]={state:'cut'}); });
          snap(n,'Back at '+name(n)+': v='+fmt(v)+(n.t==='max'?' ≥ β='+fmt(b)+'. MIN above will never let play reach here':' ≤ α='+fmt(a)+'. MAX above already has something at least as good')+' → prune the remaining '+rest.length+' child'+(rest.length>1?'ren':'')+'.');
          break;
        }
        snap(n,'Back at '+name(n)+': got '+r+' → v='+fmt(v)+', '+(n.t==='max'?'α='+fmt(a):'β='+fmt(b))+'.'+(rest.length?' No prune ('+(n.t==='max'?'v < β':'v > α')+').':''));
      }
      S[n.id].state='done'; snap(n,name(n)+' returns '+fmt(v)+'.'); return v;
    }
    rec(root,-Infinity,Infinity); return {steps,cut};
  }

  function alphabeta(el,spec,opt={}){
    const tags={};
    const {root,all}=draw(el,spec,(n,d)=>{ const t=document.createElement('span'); t.className='ab'; d.appendChild(t); tags[n.id]=t; },110);
    const {steps,cut}=trace(root,all);
    const paint=(n,cls)=>{ n.el.classList.remove('ab-active','ab-done','ab-cut','ab-mark','ab-ok','ab-bad'); if(cls) n.el.classList.add(...cls.split(' ')); };
    if(opt.mode==='practice'){
      // A node counts if it is the top of a cut; clicks below a cut are ignored.
      const marked=new Set();
      all.forEach(n=>{ if(!n.parent) return; n.el.classList.add('ab-click'); n.el.title='Click to mark as pruned';
        n.el.addEventListener('click',()=>{ marked.has(n.id)?marked.delete(n.id):marked.add(n.id); paint(n,marked.has(n.id)?'ab-mark':''); }); });
      const {bar,st}=toolbar(el,['Check','Reveal','Reset']);
      const under=n=>{ for(let p=n.parent;p;p=p.parent) if(cut.has(p.id)) return true; return false; };
      bar.addEventListener('click',e=>{ const a=e.target.dataset.a; if(!a) return;
        if(a==='reset'){ marked.clear(); all.forEach(n=>paint(n,'')); st.textContent=''; return; }
        if(a==='reveal'){ all.forEach(n=>paint(n,cut.has(n.id)?'ab-cut':under(n)?'ab-cut':'')); st.textContent='Pruned subtrees shown faded. Root value = '+root.v+'. Reset and redo it from memory.'; return; }
        let hit=0, wrong=0;
        all.forEach(n=>{ if(!n.parent||under(n)) return;
          if(cut.has(n.id)&&marked.has(n.id)){ hit++; paint(n,'ab-mark ab-ok'); }
          else if(marked.has(n.id)){ wrong++; paint(n,'ab-mark ab-bad'); }
          else if(cut.has(n.id)) paint(n,''); });
        st.textContent = hit===cut.size&&!wrong ? '✓ Exactly right: '+cut.size+' cut'+(cut.size>1?'s':'')+'.'
          : hit+' / '+cut.size+' cuts found'+(wrong?', '+wrong+' marked that should be explored (red)':'')+'. Trace it left to right, writing α and β beside each node.';
      });
      return;
    }
    // step mode
    let i=-1; const {bar,st}=toolbar(el,['Back','Next','Reset']);
    function render(){
      const s=steps[i]||{S:{},msg:'Press Next to start at the root with α=−∞, β=+∞.',cur:-1};
      all.forEach(n=>{ const x=s.S[n.id]; tags[n.id].textContent='';
        if(!x){ paint(n,''); return; }
        paint(n,n.id===s.cur?'ab-active':x.state==='active'?'ab-path':'ab-'+x.state);
        if(x.v!==undefined) tags[n.id].innerHTML='v='+x.v+'<br>α='+x.a+' β='+x.b; });
      st.textContent=(i>=0?'Step '+(i+1)+'/'+steps.length+': ':'')+s.msg+(opt.countLeaves&&i>=0?'  [leaves examined: '+s.leaves+' of '+all.filter(n=>n.leaf!==undefined).length+']':'');
    }
    bar.addEventListener('click',e=>{ const a=e.target.dataset.a; if(!a) return;
      if(a==='next') i=Math.min(i+1,steps.length-1); if(a==='back') i=Math.max(i-1,-1); if(a==='reset') i=-1; render(); });
    render();
  }
  window.GameTree={mount,alphabeta};
})();
