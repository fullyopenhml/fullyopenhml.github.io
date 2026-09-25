/* Live 3D view of the builder's combination: one GLB per module, composed by matching anchors. */
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

THREE.Object3D.DEFAULT_UP.set(0, 0, 1);

const PALETTE = { foh: 0xe8642c, duke2: 0x3b7dd8, bhl: 0x3aa86b, lerobot: 0xd9a400, duck: 0x1fa3a3, mevita: 0x8b5cf6, "amazing-hand": 0xd946a0, hopejr: 0x8a8f98, bolt: 0xa0522d,
  "so-arm101": 0xc2410c, openarm: 0x0e7490, leap: 0x7c3aed, ruka: 0xbe185d, lekiwi: 0x65a30d, tidybot2: 0x4b5563, solo12: 0xb45309, xlerobot: 0x2563eb };
const SLOT_ORDER = ["lower", "torso", "arms", "hands", "head"];
const V = (a) => new THREE.Vector3(a[0], a[1], a[2]);

const container = document.getElementById("mix-viewer");
const legendEl = document.getElementById("mix-legend");
const statusEl = document.getElementById("mix-status");
if (container) init();

async function init() {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 0.01, 50);
  camera.position.set(2.2, -2.4, 1.3);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true; controls.target.set(0, 0, 0.55);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8a8a, 0.9));
  const key = new THREE.DirectionalLight(0xffffff, 1.4); key.position.set(2, -3, 4); scene.add(key);
  const fill = new THREE.DirectionalLight(0xffffff, 0.5); fill.position.set(-3, 2, 2); scene.add(fill);
  const grid = new THREE.GridHelper(4, 40, 0x9aa0a8, 0xcfd3d8); grid.rotation.x = Math.PI / 2; scene.add(grid);
  const root = new THREE.Group(); scene.add(root);

  const isDark = () => document.documentElement.dataset.theme === "dark" || (!document.documentElement.dataset.theme && matchMedia("(prefers-color-scheme: dark)").matches);
  function resize() {
    const w = container.clientWidth, h = container.clientHeight || 520;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(container); resize();
  (function loop() { requestAnimationFrame(loop); controls.update(); grid.material.opacity = isDark() ? 0.35 : 0.6; grid.material.transparent = true; renderer.render(scene, camera); })();

  const geomData = await fetch("assets/data/module_geom.json").then(r => r.json());
  const loader = new GLTFLoader();
  const cache = {};
  const loadGlb = (file) => cache[file] || (cache[file] = new Promise((res, rej) => loader.load(file, g => {
    g.scene.traverse(o => { if (o.isMesh && !o.geometry.attributes.normal) o.geometry.computeVertexNormals(); });
    res(g.scene);
  }, undefined, rej)));

  let explode = false, current = null, token = 0;
  document.getElementById("mix-fit")?.addEventListener("click", () => fit());
  document.getElementById("mix-explode")?.addEventListener("click", e => { explode = !explode; e.target.textContent = explode ? "Assemble" : "Explode"; if (current) show(current); });

  function fit() {
    const box = new THREE.Box3().setFromObject(root);
    if (box.isEmpty()) return;
    const size = box.getSize(new THREE.Vector3()), c = box.getCenter(new THREE.Vector3());
    const r = Math.max(size.x, size.y, size.z) * 0.6 / Math.tan(camera.fov * Math.PI / 360);
    controls.target.copy(c); camera.position.set(c.x + r * 0.75, c.y - r * 0.85, c.z + r * 0.45); controls.update();
  }

  function material(robot, placeholder) {
    return new THREE.MeshStandardMaterial({ color: PALETTE[robot] || 0x999999, roughness: 0.55, metalness: 0.08, transparent: placeholder, opacity: placeholder ? 0.35 : 1, wireframe: false });
  }

  function placeholder(slot, mod) {
    // an honest box for a module without public geometry, sized from its robot's height
    const h = (mod.scale_mm || 1000) / 1000;
    const dims = { lower: [0.25, 0.3, 0.5 * h], torso: [0.2, 0.3, 0.3 * h], arms: [0.09, 0.09, 0.45 * h], hands: [0.06, 0.1, 0.12], head: [0.14, 0.16, 0.15] }[slot];
    const mk = () => { const g = new THREE.Mesh(new THREE.BoxGeometry(...dims), material(mod.robot, true)); g.add(new THREE.LineSegments(new THREE.EdgesGeometry(g.geometry), new THREE.LineBasicMaterial({ color: PALETTE[mod.robot] || 0x999999 }))); return g; };
    const parts = {}; const anchors = {}; const y = 0.16;
    if (slot === "lower") { const g = mk(); g.position.z = dims[2] / 2; parts.C = g; anchors.top = [0, 0, dims[2]]; }
    if (slot === "torso") { const g = mk(); g.position.z = dims[2] / 2; parts.C = g; anchors.bottom = [0, 0, 0]; anchors.shoulder_L = [0, y, dims[2] * 0.9]; anchors.shoulder_R = [0, -y, dims[2] * 0.9]; anchors.top = [0, 0, dims[2]]; }
    if (slot === "arms") { for (const [s, sy] of [["L", y], ["R", -y]]) { const g = mk(); g.position.set(0, sy, -dims[2] / 2); parts[s] = g; anchors["shoulder_" + s] = [0, sy, 0]; anchors["wrist_" + s] = [0, sy, -dims[2]]; } }
    if (slot === "hands") { for (const [s, sy] of [["L", y], ["R", -y]]) { const g = mk(); g.position.set(0, sy, -dims[2] / 2); parts[s] = g; anchors["wrist_" + s] = [0, sy, 0]; } }
    if (slot === "head") { const g = mk(); g.position.z = dims[2] / 2; parts.C = g; anchors.bottom = [0, 0, 0]; }
    return { parts, anchors, ground_z: 0, placeholder: true };
  }

  async function build(slot, mod) {
    const g = geomData.modules[mod.id];
    if (!g) return placeholder(slot, mod);
    const parts = {};
    for (const [side, file] of Object.entries(g.parts)) {
      const src = await loadGlb(file); const obj = src.clone();
      obj.traverse(o => { if (o.isMesh) o.material = material(mod.robot, false); });
      parts[side] = obj;
    }
    return { parts, anchors: g.anchors || {}, ground_z: g.ground_z || 0, credit: g.credit };
  }

  async function show(sel) {
    current = sel; const my = ++token;
    statusEl && (statusEl.textContent = "loading…");
    const built = {};
    for (const slot of SLOT_ORDER) if (sel[slot]) built[slot] = await build(slot, sel[slot]);
    if (my !== token) return;
    root.clear();
    const place = (obj, offset) => { obj.position.copy(offset); root.add(obj); };
    const off = {};
    const A = (b, k) => (b && b.anchors && b.anchors[k]) ? V(b.anchors[k]) : null;
    const ex = (i) => explode ? new THREE.Vector3(0, 0, i * 0.18) : new THREE.Vector3();
    // lower body on the ground
    if (built.lower) { off.lower = new THREE.Vector3(0, 0, -built.lower.ground_z); place(built.lower.parts.C, off.lower.clone().add(ex(0))); }
    const lowerTop = built.lower ? (A(built.lower, "top") || V([0, 0, 0.5])).add(off.lower) : new THREE.Vector3(0, 0, 0);
    // torso: bottom anchor on the lower body's top anchor; with no lower body it stands on the ground
    if (built.torso) {
      off.torso = built.lower ? lowerTop.clone().sub(A(built.torso, "bottom") || new THREE.Vector3()) : new THREE.Vector3(0, 0, -built.torso.ground_z);
      place(built.torso.parts.C, off.torso.clone().add(ex(1)));
    }
    const shoulder = (s) => built.torso && A(built.torso, "shoulder_" + s) ? A(built.torso, "shoulder_" + s).add(off.torso) : lowerTop.clone().add(new THREE.Vector3(0, s === "L" ? 0.16 : -0.16, 0.3));
    const wrist = {};
    if (built.arms) for (const s of ["L", "R"]) if (built.arms.parts[s]) {
      const o = shoulder(s).sub(A(built.arms, "shoulder_" + s) || new THREE.Vector3()); place(built.arms.parts[s], o.clone().add(ex(2)));
      wrist[s] = (A(built.arms, "wrist_" + s) || new THREE.Vector3(0, 0, -0.45)).add(o);
    }
    if (built.hands) for (const s of ["L", "R"]) if (built.hands.parts[s]) {
      const w = wrist[s] || shoulder(s).add(new THREE.Vector3(0, 0, -0.45));
      place(built.hands.parts[s], w.sub(A(built.hands, "wrist_" + s) || new THREE.Vector3()).add(ex(3)));
    }
    if (built.head) {
      const top = built.torso && A(built.torso, "top") ? A(built.torso, "top").add(off.torso) : lowerTop.clone().add(new THREE.Vector3(0, 0, 0.4));
      place(built.head.parts.C, top.sub(A(built.head, "bottom") || new THREE.Vector3()).add(ex(4)));
    }
    if (legendEl) legendEl.innerHTML = SLOT_ORDER.filter(s => sel[s]).map(s => `<li><i style="background:#${(PALETTE[sel[s].robot] || 0x999999).toString(16).padStart(6, "0")}"></i>${sel[s].name}${built[s].placeholder ? ' <span class="pill warn">no public geometry, box stands in</span>' : ""}</li>`).join("");
    statusEl && (statusEl.textContent = Object.values(built).some(b => b.placeholder) ? "Boxes stand in for modules whose projects publish no assembled geometry." : "");
    fit();
  }

  const selectionOf = (d) => { const s = {}; for (const k of SLOT_ORDER) s[k] = d && d[k] ? d[k] : null; return s; };
  document.addEventListener("foh:selection", e => show(selectionOf(e.detail)));
  if (window._mixSelection) show(selectionOf(window._mixSelection));
}
