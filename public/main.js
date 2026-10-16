// UI for the codex: titles, language, recruiter mode, music, boot. The WebGL
// layer lives in gl.js and is loaded after, so the page works without it.
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
let lang = 'en';

/* figure placement: data attributes -> CSS vars shared with gl.js */
$$('.issue').forEach((s) => {
  const img = $('.still', s);
  img.style.setProperty('--fh', s.dataset.fh);
  img.style.setProperty('--fb', s.dataset.fb);
  img.style.setProperty('--fx', s.dataset.fx);
});

/* titles: split into letters, fit to their box */
function renderTitle(el) {
  const text = el.textContent.trim();
  el.textContent = '';
  [...text].forEach((c, i) => {
    const s = document.createElement('span');
    s.className = 'ch'; s.style.setProperty('--i', i); s.textContent = c;
    el.appendChild(s);
  });
  fit(el);
}
function fit(el) {
  const box = el.parentElement;
  el.style.fontSize = '100px';
  const r = el.getBoundingClientRect();
  if (!r.width) return;
  const h = box.clientHeight - parseFloat(getComputedStyle(box).paddingBottom);
  el.style.fontSize = (100 * Math.min(box.clientWidth / r.width, h / r.height) * 0.995) + 'px';
}
const titles = $$('.title-text');
titles.forEach(renderTitle);
const fitAll = () => titles.forEach(fit);
new ResizeObserver(fitAll).observe(document.body);
document.fonts && document.fonts.ready.then(fitAll);

/* sections: reveal titles, play background loops only while visible */
const io = new IntersectionObserver((entries) => entries.forEach((e) => {
  const v = $('.bg video', e.target);
  if (e.isIntersecting) {
    e.target.classList.add('in');
    if (v && !reduce) {
      if (!v.src && v.dataset.src) v.src = v.dataset.src;
      v.play().then(() => v.classList.add('on')).catch(() => {});
    }
  } else if (v) v.pause();
}), { threshold: 0.2 });
$$('.issue').forEach((s) => io.observe(s));
$$('.bg video').forEach((v) => v.addEventListener('error', () => v.remove()));

/* EN <-> LATINA */
function setLang(next) {
  lang = next;
  document.documentElement.lang = lang;
  $$('[data-la]').forEach((el) => {
    if (el.dataset.en === undefined) el.dataset.en = el.classList.contains('title-text') ? el.textContent : el.innerHTML;
    el.innerHTML = lang === 'la' ? el.dataset.la : el.dataset.en;
    if (el.classList.contains('title-text')) renderTitle(el);
  });
  $$('.seg button').forEach((b) => b.setAttribute('aria-pressed', b.dataset.lang === lang));
}
$$('.seg button').forEach((b) => b.addEventListener('click', () => setLang(b.dataset.lang)));
window.codexSetLang = setLang; // scroll.js re-applies it to text it loads later

/* recruiter mode */
$('#toRecruiter')?.addEventListener('click', () => { document.body.classList.add('recruiter'); scrollTo(0, 0); });
$('#toPoster')?.addEventListener('click', () => { document.body.classList.remove('recruiter'); requestAnimationFrame(fitAll); });

/* barcode */
$$('.bars').forEach((bc) => {
  let seed = 26, x = 0;
  const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  while (x < 178) {
    const w = 1 + Math.floor(rnd() * 3.4);
    const r = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    r.setAttribute('x', x); r.setAttribute('width', w); r.setAttribute('height', 60);
    bc.appendChild(r);
    x += w + 1 + Math.floor(rnd() * 2.6);
  }
});

/* choir-ish synth placeholder (real recordings later) */
let ctx, master, voices = [], timer, started = 0;
const chords = [[196, 233.08, 293.66, 392], [155.56, 233.08, 311.13, 392], [130.81, 261.63, 311.13, 392], [146.83, 220, 293.66, 369.99]];
const music = $('#music'), playBtn = $('#play'), icon = $('#playIcon');
function startSynth() {
  ctx = new (window.AudioContext || window.webkitAudioContext)();
  master = ctx.createGain(); master.gain.value = 0; master.connect(ctx.destination);
  master.gain.linearRampToValueAtTime(.06, ctx.currentTime + 2.5);
  const formant = ctx.createBiquadFilter(); formant.type = 'bandpass'; formant.frequency.value = 850; formant.Q.value = .9;
  const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 2400;
  formant.connect(lp); lp.connect(master);
  chords[0].forEach((f) => [-7, 7].forEach((cents) => {
    const o = ctx.createOscillator(); o.type = 'sawtooth'; o.frequency.value = f; o.detune.value = cents;
    const lfo = ctx.createOscillator(), lg = ctx.createGain(); lfo.frequency.value = 4.6 + Math.random(); lg.gain.value = 1.6;
    lfo.connect(lg); lg.connect(o.frequency); o.connect(formant); o.start(); lfo.start();
    voices.push({ o, step: voices.length >> 1 });
  }));
  let c = 0;
  timer = setInterval(() => {
    c = (c + 1) % chords.length;
    voices.forEach((v) => v.o.frequency.setTargetAtTime(chords[c][v.step], ctx.currentTime, .8));
  }, 6000);
  started = performance.now(); tick();
}
function stopSynth() {
  clearInterval(timer);
  const c = ctx; master.gain.setTargetAtTime(0, c.currentTime, .4);
  setTimeout(() => c.close(), 1500);
  ctx = null; voices = [];
}
function tick() {
  if (!ctx) return;
  const s = ((performance.now() - started) / 1000) % 252;
  $('#t').textContent = `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  $('#prog').style.width = (s / 252 * 100) + '%';
  requestAnimationFrame(tick);
}
playBtn?.addEventListener('click', () => {
  const on = !ctx;
  on ? startSynth() : stopSynth();
  music.classList.toggle('playing', on);
  playBtn.setAttribute('aria-label', on ? 'Pause' : 'Play');
  icon.innerHTML = on ? '<path d="M3 1.5h3v11H3zM8 1.5h3v11H8z"/>' : '<path d="M3 1.5 L12 7 L3 12.5 Z"/>';
});

/* boot: gl.js wakes the pyramid; without it, a short text-only intro */
const boot = $('#boot');
let booted = false;
function finishBoot() {
  if (booted) return; booted = true;
  boot?.classList.add('gone');
  setTimeout(() => boot?.remove(), 1000);
  window.dispatchEvent(new Event('codex:booted'));
}
boot?.addEventListener('click', finishBoot);
if (reduce || !boot) finishBoot();

const lowPower = (navigator.hardwareConcurrency || 8) <= 4 || navigator.connection?.saveData;
if (!reduce && !lowPower) {
  import('./gl.js')
    .then((m) => m.start({ boot: booted ? null : boot, onBootDone: finishBoot }))
    .catch((err) => { console.warn('WebGL layer unavailable, using stills', err); boot?.classList.add('lit'); setTimeout(finishBoot, 1600); });
} else if (!booted) {
  boot?.classList.add('lit'); setTimeout(finishBoot, 1600);
}
setTimeout(finishBoot, 6000); // never trap anyone behind the intro
