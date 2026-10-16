// Scrolls opened by their cord: drag the tassel down to unroll, up to roll it
// back, and it stays wherever you let go. A tap opens or closes it fully.
// The open sheet is capped (data-cap × viewport height) and scrolls inside;
// once its text runs out, the wheel carries on down the page as usual.
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const PDF = 'assets/Sam_Amin_Resume.pdf';

// The main page borrows the scroll's text from curriculum.html, so the
// résumé is written once.
async function fill(scroll) {
  const src = scroll.dataset.from;
  if (!src) return;
  const doc = new DOMParser().parseFromString(await (await fetch(src)).text(), 'text/html');
  scroll.querySelector('.sheet-inner').innerHTML = doc.querySelector('#scroll .sheet-inner').innerHTML;
  window.codexSetLang?.(document.documentElement.lang || 'en');
}

function cord(scroll) {
  const sheet = scroll.querySelector('.sheet');
  const inner = sheet.querySelector('.sheet-inner');
  const tassel = scroll.querySelector('.tassel');
  const cap = () => Math.min(inner.scrollHeight, innerHeight * (+scroll.dataset.cap || .7));
  let h = 0;

  function set(v, glide = false) {
    h = Math.max(0, Math.min(cap(), v));
    sheet.classList.toggle('glide', glide && !reduce);
    sheet.style.height = h + 'px';
    scroll.classList.toggle('open', h > 4);
    tassel.setAttribute('aria-valuenow', Math.round((h / (cap() || 1)) * 100));
  }
  set(0);

  let y0 = null, h0 = 0, moved = false;
  tassel.addEventListener('pointerdown', (e) => {
    tassel.setPointerCapture(e.pointerId);
    y0 = e.clientY; h0 = h; moved = false;
    scroll.classList.add('pulling');
    e.preventDefault();
  });
  tassel.addEventListener('pointermove', (e) => {
    if (y0 === null) return;
    const want = h0 + e.clientY - y0;
    if (Math.abs(e.clientY - y0) > 4) moved = true;
    set(want);
    // Pulling past fully open stretches the cord a little.
    scroll.style.setProperty('--stretch', Math.min(36, Math.max(0, want - h) * .4) + 'px');
  });
  const release = () => {
    if (y0 === null) return;
    y0 = null;
    scroll.classList.remove('pulling');
    scroll.style.setProperty('--stretch', '0px');
    if (!moved) set(h > 4 ? 0 : cap(), true);
  };
  tassel.addEventListener('pointerup', release);
  tassel.addEventListener('pointercancel', release);
  tassel.addEventListener('keydown', (e) => {
    const step = { ArrowDown: 80, ArrowUp: -80, PageDown: 300, PageUp: -300 }[e.key];
    if (step) set(h + step, true);
    else if (e.key === 'Home') set(0, true);
    else if (e.key === 'End') set(cap(), true);
    else if (e.key === 'Enter' || e.key === ' ') set(h > 4 ? 0 : cap(), true);
    else return;
    e.preventDefault();
  });
  addEventListener('resize', () => { if (h > cap()) set(cap()); });
}

document.querySelectorAll('.scroll').forEach(async (s) => {
  await fill(s).catch((err) => console.warn('scroll text failed to load', err));
  cord(s);
});

// Print / save gives the standard résumé PDF, not a print of this page.
addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && (e.key === 'p' || e.key === 's')) {
    e.preventDefault();
    open(PDF, '_blank', 'noopener');
  }
});
