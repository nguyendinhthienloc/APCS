// Reusable multiple-choice quiz with instant feedback.
// Quiz.mount(el, [{q, options:[...], answer:index, why}])
(function(){
  let uid=0;
  function mount(el,qs){
    el.classList.add('quiz');
    qs.forEach((q,qi)=>{
      const d=document.createElement('div'), name='q'+(uid++); d.className='q';
      d.innerHTML='<p><b>'+(qi+1)+'.</b> '+q.q+'</p>'
        +q.options.map((o,i)=>'<label><input type="radio" name="'+name+'" value="'+i+'"> '+o+'</label>').join('')
        +'<div class="why" hidden></div>';
      d.addEventListener('change',e=>{
        const pick=+e.target.value;
        d.querySelectorAll('label').forEach((l,i)=>{ l.className = i===q.answer?'ok':(i===pick?'bad':''); });
        const w=d.querySelector('.why'); w.hidden=false; w.textContent=(pick===q.answer?'✓ ':'✗ ')+q.why;
      });
      el.appendChild(d);
    });
  }
  window.Quiz={mount};
})();
