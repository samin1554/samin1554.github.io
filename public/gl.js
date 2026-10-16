// WebGL layer: "living paintings" (figure cutouts displaced by their depth
// maps) and the eye-pyramid, used in the boot intro and in Issue V.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

THREE.Cache.enabled = true;
const pointer = { x: 0, y: 0 };
addEventListener('pointermove', (e) => {
  pointer.x = (e.clientX / innerWidth) * 2 - 1;
  pointer.y = -((e.clientY / innerHeight) * 2 - 1);
}, { passive: true });

const clamp01 = (v) => Math.min(1, Math.max(0, v));
const easeOut = (p) => 1 - Math.pow(1 - clamp01(p), 3);
const smooth = (a, b, v) => { const x = clamp01((v - a) / (b - a)); return x * x * (3 - 2 * x); };

/* ---------- living painting ---------- */
const VERT = /* glsl */`
  uniform sampler2D uDepth; uniform float uAmp; uniform float uTime;
  varying vec2 vUv; varying float vD;
  void main() {
    vUv = uv;
    float d = texture2D(uDepth, uv).r;
    vD = d;
    vec3 p = position;
    p.z += (d - .5) * uAmp;
    p.z += sin(uTime * .7 + uv.y * 8. + uv.x * 3.) * .02 * uAmp * d;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.);
  }`;
const FRAG = /* glsl */`
  uniform sampler2D uMap; uniform float uExp; uniform float uTime; uniform vec3 uTint; uniform vec3 uLight;
  varying vec2 vUv; varying float vD;
  void main() {
    vec4 c = texture2D(uMap, vUv);
    if (c.a < .02) discard;
    vec3 col = c.rgb;
    float l = dot(col, vec3(.299, .587, .114));
    col = mix(col, vec3(l), .18) * uExp;
    col = mix(uTint + col * .45, col, smoothstep(.0, .5, l));
    vec2 lp = vec2(.35 + sin(uTime * .21) * .2, .25 + cos(uTime * .17) * .1);
    float beam = smoothstep(.7, .0, distance(vUv, lp));
    col += uLight * beam * (.1 + vD * .28) * l;
    col *= .96 + .04 * sin(uTime * 6.3) * sin(uTime * 2.9);
    gl_FragColor = vec4(col, c.a);
  }`;

class Painting {
  constructor(section) {
    this.section = section;
    this.still = section.querySelector('.still');
    this.canvas = section.querySelector('canvas.gl');
    const d = section.dataset;
    this.cfg = { n: d.fig, amp: +d.amp || .1, exp: +d.exp || .8, tint: new THREE.Color(d.tint || '#000'), light: new THREE.Color(d.light || '#fff') };
    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, alpha: true, antialias: true });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
    this.renderer.setClearColor(0x000000, 0);
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(20, 1, .1, 100);
    this.camera.position.z = 10;
    this.pivot = new THREE.Group();
    this.scene.add(this.pivot);
    this.m = { x: 0, y: 0 };
    this.visible = false;
    new ResizeObserver(() => this.layout()).observe(this.canvas);
  }

  async load() {
    const tl = new THREE.TextureLoader(), n = this.cfg.n;
    const [map, depth] = await Promise.all([tl.loadAsync(`assets/web/${n}.webp`), tl.loadAsync(`assets/web/${n}-depth.png`)]);
    map.anisotropy = 4;
    this.aspect = map.image.width / map.image.height;
    this.uniforms = {
      uMap: { value: map }, uDepth: { value: depth }, uAmp: { value: 0 }, uTime: { value: 0 },
      uExp: { value: this.cfg.exp }, uTint: { value: this.cfg.tint }, uLight: { value: this.cfg.light },
    };
    const seg = innerWidth < 760 ? 140 : 240;
    this.mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(1, 1, seg, seg),
      new THREE.ShaderMaterial({ vertexShader: VERT, fragmentShader: FRAG, uniforms: this.uniforms, transparent: true }),
    );
    this.pivot.add(this.mesh);
    await this.extras?.();
    this.layout();
    this.render(0);
    this.section.classList.add('gl-on');
  }

  // Same placement rules as the .still image in styles.css.
  layout() {
    if (!this.mesh) return;
    const w = this.canvas.clientWidth, h = this.canvas.clientHeight;
    if (!w || !h) return;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    const cs = getComputedStyle(this.still);
    const fh = parseFloat(cs.getPropertyValue('--fh')) || .9;
    const fb = parseFloat(cs.getPropertyValue('--fb')) || 0;
    const fx = parseFloat(cs.getPropertyValue('--fx')) || 0;
    const viewH = 2 * Math.tan(THREE.MathUtils.degToRad(this.camera.fov / 2)) * this.camera.position.z;
    const viewW = viewH * this.camera.aspect;
    let ph = viewH * fh, pw = ph * this.aspect;
    if (pw > viewW * 1.08) { pw = viewW * 1.08; ph = pw / this.aspect; }
    this.mesh.scale.set(pw, ph, 1);
    this.pivot.position.set(fx * viewW, -viewH / 2 + fb * viewH + ph / 2, 0);
    this.size = { pw, ph };
    this.uniforms.uAmp.value = ph * this.cfg.amp;
    this.place?.();
  }

  render(t) {
    if (!this.mesh) return;
    this.m.x += (pointer.x - this.m.x) * .05;
    this.m.y += (pointer.y - this.m.y) * .05;
    this.pivot.rotation.y = this.m.x * .12 + Math.sin(t * .23) * .04;
    this.pivot.rotation.x = -this.m.y * .07 + Math.cos(t * .19) * .025;
    this.uniforms.uTime.value = t;
    this.tick?.(t);
    this.renderer.render(this.scene, this.camera);
  }
}

/* ---------- eye-pyramid ---------- */
// A black room with two thin light strips: obsidian stays black and only the
// strips glint along its faces.
function envFor(renderer) {
  const room = new THREE.Scene();
  room.add(new THREE.Mesh(new THREE.SphereGeometry(20, 32, 16), new THREE.MeshBasicMaterial({ color: 0x020203, side: THREE.BackSide })));
  const strip = (x, y, z, w, h, color) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color, side: THREE.DoubleSide }));
    m.position.set(x, y, z); m.lookAt(0, 0, 0); room.add(m);
  };
  strip(-6, 3, 6, .5, 14, 0xfff0d0);
  strip(7, -1, 3, .35, 10, 0x9cc4ff);
  strip(0, 9, -4, 12, .4, 0xffd9a0);
  const pm = new THREE.PMREMGenerator(renderer);
  const tex = pm.fromScene(room, .02).texture;
  pm.dispose();
  return tex;
}
function lights(scene, rim) {
  scene.add(new THREE.AmbientLight(0xffffff, .15));
  const key = new THREE.DirectionalLight(0xfff1d6, .9); key.position.set(-6, 1.5, 2); scene.add(key);
  const back = new THREE.DirectionalLight(rim, 3); back.position.set(3, 2, -4); scene.add(back);
}
function canvasTex(size, draw) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  draw(c.getContext('2d'), size);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
const glowTex = () => canvasTex(256, (g, s) => {
  const r = g.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  r.addColorStop(0, 'rgba(255,244,214,1)'); r.addColorStop(.25, 'rgba(255,214,140,.55)'); r.addColorStop(1, 'rgba(192,147,70,0)');
  g.fillStyle = r; g.fillRect(0, 0, s, s);
});

// Shared controls, whichever way the pyramid was built.
function controls(group, { iris, lid, halo, glow, mixer, clip }) {
  const irisBase = iris ? iris.position.clone() : null;
  let awake = 0;
  return {
    group,
    setAwake(p) {
      awake = p;
      if (mixer) { mixer.setTime(p * clip.duration); return; }
      lid.scale.y = .03 + .97 * smooth(.35, .85, p);
      const h = easeOut((p - .1) / .9);
      halo.scale.setScalar(.2 + .8 * h);
      halo.children.forEach((r) => { r.material.opacity = .32 * h; });
      glow.material.opacity = .36 * h;
    },
    look(x, y) {
      if (!iris) return;
      iris.position.x = irisBase.x + Math.max(-1, Math.min(1, x)) * .07;
      iris.position.y = irisBase.y + Math.max(-1, Math.min(1, y)) * .035;
    },
    tick(t) {
      if (halo) halo.rotation.z = t * .03;
      if (glow) glow.material.opacity = (mixer ? .36 : .36 * awake) * (.9 + .1 * Math.sin(t * 1.7));
      if (lid && awake >= 1) lid.scale.y = (t % 5.5) < .14 ? .08 : 1;
    },
  };
}

function proceduralPyramid() {
  const group = new THREE.Group();
  const a = .92, H = 1;
  const top = [0, H, 0], bot = [0, -H, 0];
  const base = [[a, 0, a], [-a, 0, a], [-a, 0, -a], [a, 0, -a]];
  const pos = [];
  for (let i = 0; i < 4; i++) {
    const p = base[i], q = base[(i + 1) % 4];
    pos.push(...top, ...p, ...q);
    pos.push(...bot, ...q, ...p);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.computeVertexNormals();
  const body = new THREE.Mesh(geo, new THREE.MeshPhysicalMaterial({
    color: 0x060608, metalness: .2, roughness: .07, clearcoat: .8, clearcoatRoughness: .04, flatShading: true, envMapIntensity: 1.2,
  }));
  group.add(body);
  group.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: 0xb8913f, transparent: true, opacity: .45 })));

  // eye on the front ridge
  const eye = new THREE.Group(); eye.position.set(0, 0, a + .012); group.add(eye);
  const lid = new THREE.Group(); eye.add(lid);
  const s = new THREE.Shape(); const w = .27, h = .26;
  s.moveTo(-w, 0); s.quadraticCurveTo(0, h, w, 0); s.quadraticCurveTo(0, -h, -w, 0);
  lid.add(new THREE.Mesh(new THREE.ShapeGeometry(s, 24), new THREE.MeshBasicMaterial({ color: 0xf4efe0, toneMapped: false })));
  const irisTex = canvasTex(256, (g, S) => {
    const c = S / 2;
    const r = g.createRadialGradient(c, c, 0, c, c, c);
    r.addColorStop(0, '#0a1424'); r.addColorStop(.55, '#1d3d66'); r.addColorStop(.8, '#0b0f18'); r.addColorStop(.86, '#c09346'); r.addColorStop(.93, '#5a3c14'); r.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = r; g.beginPath(); g.arc(c, c, c, 0, Math.PI * 2); g.fill();
    g.fillStyle = '#020203'; g.beginPath(); g.arc(c, c, S * .17, 0, Math.PI * 2); g.fill();
    g.fillStyle = 'rgba(255,255,255,.9)'; g.beginPath(); g.arc(c + S * .12, c - S * .12, S * .06, 0, Math.PI * 2); g.fill();
  });
  const iris = new THREE.Mesh(new THREE.CircleGeometry(.095, 48), new THREE.MeshBasicMaterial({ map: irisTex, transparent: true, toneMapped: false }));
  iris.position.z = .003; lid.add(iris);

  // halo: alternating rays and a soft glow behind the diamond
  const halo = new THREE.Group(); halo.position.z = -.6; group.add(halo);
  for (let i = 0; i < 56; i++) {
    const long = i % 2 === 0, len = long ? 1.25 : .7, ang = (i / 56) * Math.PI * 2;
    const ray = new THREE.Mesh(new THREE.PlaneGeometry(long ? .016 : .01, len), new THREE.MeshBasicMaterial({ color: 0xffe3a8, transparent: true, opacity: 0, depthWrite: false, toneMapped: false }));
    const r0 = 1.18 + len / 2;
    ray.position.set(Math.cos(ang) * r0, Math.sin(ang) * r0, 0);
    ray.rotation.z = ang - Math.PI / 2;
    halo.add(ray);
  }
  const glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex(), transparent: true, opacity: 0, depthWrite: false, toneMapped: false }));
  glow.scale.setScalar(4.6); glow.position.z = -.7; group.add(glow);
  return controls(group, { iris, lid, halo, glow });
}

// Prefer the Blender model; fall back to the one built above.
async function loadPyramid() {
  try {
    const gltf = await new GLTFLoader().loadAsync('assets/models/pyramid.glb');
    const root = gltf.scene;
    const halo = root.getObjectByName('Halo');
    const box = new THREE.Box3();
    root.traverse((o) => { if (o.isMesh && !(halo && isInside(o, halo))) box.expandByObject(o); });
    const size = box.getSize(new THREE.Vector3()), center = box.getCenter(new THREE.Vector3());
    const group = new THREE.Group();
    root.position.sub(center);
    group.add(root);
    group.scale.setScalar(2 / (size.y || 2));
    const glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex(), transparent: true, opacity: .6, depthWrite: false, toneMapped: false }));
    glow.scale.setScalar(4.6 * (size.y || 2) / 2); glow.position.z = -.7 * (size.y || 2) / 2; root.add(glow);
    let clip = gltf.animations.find((c) => c.name === 'Awaken') || gltf.animations[0];
    let mixer = null;
    if (clip) {
      mixer = new THREE.AnimationMixer(root);
      const action = mixer.clipAction(clip);
      action.setLoop(THREE.LoopOnce, 1);
      action.clampWhenFinished = true;
      action.play();
      clip = { duration: clip.duration * 0.999 }; // setTime(duration) would wrap to 0
    }
    root.traverse((o) => {
      if (o.material?.name === 'Obsidian') Object.assign(o.material, { envMapIntensity: 1.2, roughness: .07, clearcoatRoughness: .04 });
      if (o.material?.emissive?.getHex()) o.material.toneMapped = false;
    });
    return controls(group, { iris: root.getObjectByName('Iris'), halo, glow, mixer, clip });
  } catch {
    return proceduralPyramid();
  }
}
function isInside(o, parent) { for (let p = o; p; p = p.parent) if (p === parent) return true; return false; }

/* ---------- Issue V: painting + live pyramid over the painted diamond ---------- */
class EyePainting extends Painting {
  constructor(section) {
    super(section);
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.scene.environment = envFor(this.renderer);
    lights(this.scene, 0x9cc4ff);
    const [u, v, h] = section.dataset.pyramid.split(',').map(Number);
    this.spot = { u, v, h };
    this.wake = null;
  }
  async extras() {
    this.pyr = await loadPyramid();
    this.pivot.add(this.pyr.group);
  }
  place() {
    if (!this.pyr) return;
    const { pw, ph } = this.size, { u, v, h } = this.spot;
    const s = (h * ph / 2) * 1.12;
    this.pyr.group.scale.setScalar(s * (this.pyr.group.userData.k ??= this.pyr.group.scale.x));
    this.pyr.group.position.set((u - .5) * pw, (.5 - v) * ph, this.uniforms.uAmp.value * .5 + s * .2);
  }
  tick(t) {
    if (!this.pyr) return;
    this.wake ??= t;
    this.pyr.setAwake(easeOut((t - this.wake) / 2.6));
    this.pyr.look(pointer.x, pointer.y);
    this.pyr.tick(t);
  }
}

/* ---------- boot ---------- */
async function runBoot(boot, done) {
  const canvas = boot.querySelector('.boot-gl');
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  renderer.setClearColor(0x020203, 1);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  const scene = new THREE.Scene();
  scene.environment = envFor(renderer);
  lights(scene, 0x9cc4ff);
  const cam = new THREE.PerspectiveCamera(30, 1, .1, 100);
  cam.position.z = 9;
  const size = () => { renderer.setSize(innerWidth, innerHeight, false); cam.aspect = innerWidth / innerHeight; cam.updateProjectionMatrix(); };
  size(); addEventListener('resize', size);
  const pyr = await loadPyramid();
  pyr.group.scale.multiplyScalar(Math.min(1, cam.aspect) * .8);
  scene.add(pyr.group);
  let stopped = false;
  addEventListener('codex:booted', () => { stopped = true; setTimeout(() => renderer.dispose(), 1200); }, { once: true });
  const t0 = performance.now();
  (function loop() {
    if (stopped) return;
    const t = (performance.now() - t0) / 1000;
    const p = easeOut(t / 2.6);
    pyr.setAwake(p);
    pyr.look(pointer.x, pointer.y);
    pyr.tick(t);
    pyr.group.rotation.y = (1 - p) * -1.1 + Math.sin(t * .5) * .05;
    renderer.render(scene, cam);
    if (t > 1.2) boot.classList.add('lit');
    if (t > 4.6) done();
    requestAnimationFrame(loop);
  })();
}

/* ---------- entry ---------- */
export function start({ boot, onBootDone }) {
  if (boot) runBoot(boot, onBootDone).catch((e) => { console.warn(e); onBootDone(); });
  const paintings = [...document.querySelectorAll('.issue')].map((s) => (s.dataset.pyramid ? new EyePainting(s) : new Painting(s)));
  const io = new IntersectionObserver((entries) => entries.forEach((e) => {
    const p = paintings.find((x) => x.section === e.target);
    p.visible = e.isIntersecting;
    if (p.visible && !p.loading) p.loading = p.load().catch((err) => console.warn('painting failed', err));
  }), { rootMargin: '300px 0px' });
  paintings.forEach((p) => io.observe(p.section));
  const clock = new THREE.Clock();
  (function loop() {
    const t = clock.getElapsedTime();
    for (const p of paintings) if (p.visible) p.render(t);
    requestAnimationFrame(loop);
  })();
}
