/* Live 3D view of the builder's combination.
   Modules (one GLB per module and side) are placed by matching joint anchors, then:
   - donor parts are scaled to the reference robot's height (the legs' robot, else the torso's), shown in the legend, switchable;
   - parts from different robots are pushed into contact, so nothing floats or sits inside another part;
   - each joint gets a dot coloured by its checklist status. */
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

THREE.Object3D.DEFAULT_UP.set(0, 0, 1);

const PALETTE = { foh: 0xe8642c, duke2: 0x3b7dd8, bhl: 0x3aa86b, lerobot: 0xd9a400, duck: 0x1fa3a3, mevita: 0x8b5cf6, "amazing-hand": 0xd946a0, hopejr: 0x8a8f98, bolt: 0xa0522d,
  "so-arm101": 0xc2410c, openarm: 0x0e7490, leap: 0x7c3aed, ruka: 0xbe185d, lekiwi: 0x65a30d, tidybot2: 0x4b5563, solo12: 0xb45309, xlerobot: 0x2563eb };
const STATUS_COLOR = { verified: 0x22c55e, design: 0x60a5fa, match: 0xf59e0b, unverified: 0xf59e0b, adapter: 0xef4444, bad: 0xef4444, unknown: 0x9ca3af };
const SLOT_ORDER = ["lower", "torso", "arms", "hands", "head"];
const V = (a) => new THREE.Vector3(a[0], a[1], a[2]);
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));

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
  const markers = new THREE.Group(); scene.add(markers);

  const isDark = () => document.documentElement.dataset.theme === "dark" || (!document.documentElement.dataset.theme && matchMedia("(prefers-color-scheme: dark)").matches);
  function resize() {
    const w = container.clientWidth, h = container.clientHeight || 520;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(container); resize();
  (function loop() { requestAnimationFrame(loop); controls.update(); grid.material.opacity = isDark() ? 0.35 : 0.6; grid.material.transparent = true; renderer.render(scene, camera); })();

  const [geomData, catalog] = await Promise.all([fetch("assets/data/module_geom.json").then(r => r.json()), fetch("assets/data/catalog.json").then(r => r.json())]);
  const robots = Object.fromEntries(catalog.robots.map(r => [r.id, r]));
  const loader = new GLTFLoader();
  const cache = {};
  const loadGlb = (file) => cache[file] || (cache[file] = new Promise((res, rej) => loader.load(file, g => {
    g.scene.traverse(o => { if (o.isMesh && !o.geometry.attributes.normal) o.geometry.computeVertexNormals(); });
    res(g.scene);
  }, undefined, rej)));

  let explode = false, fitScale = true, current = null, token = 0;
  document.getElementById("mix-fit")?.addEventListener("click", () => fit());
  document.getElementById("mix-explode")?.addEventListener("click", e => { explode = !explode; e.target.textContent = explode ? "Assemble" : "Explode"; if (current) show(current); });
  document.getElementById("mix-scale")?.addEventListener("click", e => { fitScale = !fitScale; e.target.textContent = fitScale ? "Scale to fit: on" : "Scale to fit: off"; if (current) show(current); });

  function fit() {
    const box = new THREE.Box3().setFromObject(root);
    if (box.isEmpty()) return;
    const size = box.getSize(new THREE.Vector3()), c = box.getCenter(new THREE.Vector3());
    const r = Math.max(size.x, size.y, size.z) * 0.6 / Math.tan(camera.fov * Math.PI / 360);
    controls.target.copy(c); camera.position.set(c.x + r * 0.75, c.y - r * 0.85, c.z + r * 0.45); controls.update();
  }

  function material(robot, placeholder) {
    return new THREE.MeshStandardMaterial({ color: PALETTE[robot] || 0x999999, roughness: 0.55, metalness: 0.08, transparent: placeholder, opacity: placeholder ? 0.35 : 1 });
  }

  function placeholder(slot, mod) {
    // an honest box for a module without public geometry, sized from its robot's height
    const h = (mod.scale_mm || 1000) / 1000;
    const dims = { lower: [0.25, 0.3, 0.5 * h], torso: [0.2, 0.3, 0.3 * h], arms: [0.09, 0.09, 0.45 * h], hands: [0.06, 0.1, 0.12], head: [0.14, 0.16, 0.15] }[slot];
    const mk = () => { const g = new THREE.Mesh(new THREE.BoxGeometry(...dims), material(mod.robot, true)); g.add(new THREE.LineSegments(new THREE.EdgesGeometry(g.geometry), new THREE.LineBasicMaterial({ color: PALETTE[mod.robot] || 0x999999 }))); return g; };
    const parts = {}, anchors = {}, y = 0.16;
    if (slot === "lower") { const g = mk(); g.position.z = dims[2] / 2; parts.C = g; anchors.top = [0, 0, dims[2]]; }
    if (slot === "torso") { const g = mk(); g.position.z = dims[2] / 2; parts.C = g; anchors.bottom = [0, 0, 0]; anchors.shoulder_L = [0, y, dims[2] * 0.9]; anchors.shoulder_R = [0, -y, dims[2] * 0.9]; anchors.top = [0, 0, dims[2]]; }
    if (slot === "arms") { for (const s of ["L", "R"]) { const g = mk(); g.position.set(0, 0, -dims[2] / 2); parts[s] = g; anchors["shoulder_" + s] = [0, 0, 0]; anchors["wrist_" + s] = [0, 0, -dims[2]]; } }
    if (slot === "hands") { for (const s of ["L", "R"]) { const g = mk(); g.position.set(0, 0, -dims[2] / 2); parts[s] = g; anchors["wrist_" + s] = [0, 0, 0]; } }
    if (slot === "head") { const g = mk(); g.position.z = dims[2] / 2; parts.C = g; anchors.bottom = [0, 0, 0]; }
    return { parts, anchors, ground_z: 0, placeholder: true };
  }

  async function build(slot, mod) {
    const g = geomData.modules[mod.id];
    let b;
    if (!g) b = placeholder(slot, mod);
    else {
      const parts = {};
      for (const [side, file] of Object.entries(g.parts)) {
        const src = await loadGlb(file); const obj = src.clone();
        obj.traverse(o => { if (o.isMesh) o.material = material(mod.robot, false); });
        parts[side] = obj;
      }
      b = { parts, anchors: g.anchors || {}, ground_z: g.ground_z || 0, credit: g.credit };
    }
    b.mod = mod; b.robot = mod.robot; b.s = 1;
    // wrap every part in a group so the module can be scaled about its own origin
    for (const side of Object.keys(b.parts)) { const grp = new THREE.Group(); grp.add(b.parts[side]); b.parts[side] = grp; }
    return b;
  }

  const box = (obj) => new THREE.Box3().setFromObject(obj);

  async function show(sel) {
    current = sel; const my = ++token;
    statusEl && (statusEl.textContent = "loading…");
    const built = {};
    for (const slot of SLOT_ORDER) if (sel[slot]) built[slot] = await build(slot, sel[slot]);
    if (my !== token) return;
    root.clear(); markers.clear();
    const links = sel._links || {};

    // 1. scale donors to the reference robot (the legs' robot, else the torso's)
    const ref = built.lower || built.torso;
    // reference height: the legs' robot height from the catalog; for legs without one, the leg height over a typical 0.53 waist-to-height ratio
    let refH = ref ? (robots[ref.robot] || {}).height_mm : null;
    if (!refH && built.lower && built.lower.anchors.top) refH = Math.round((built.lower.anchors.top[2] - built.lower.ground_z) / 0.53 * 1000);
    const scaled = [];
    for (const b of Object.values(built)) {
      const donorH = (robots[b.robot] || {}).height_mm;
      b.s = (fitScale && refH && donorH && b.robot !== ref.robot) ? clamp(refH / donorH, 0.5, 2.0) : 1;
      for (const grp of Object.values(b.parts)) grp.scale.setScalar(b.s);
      if (Math.abs(b.s - 1) > 0.02) scaled.push(b);
    }
    const A = (b, k) => (b && b.anchors && b.anchors[k]) ? V(b.anchors[k]).multiplyScalar(b.s) : null;
    const cross = (a, b) => a && b && a.robot !== b.robot;
    const ex = (i) => new THREE.Vector3(0, 0, i * 0.18);
    const place = (grp, pos) => { grp.position.copy(pos); root.add(grp); };

    // 2. lower body on the ground
    if (built.lower) place(built.lower.parts.C, new THREE.Vector3(0, 0, -built.lower.ground_z * built.lower.s));
    const lowerObj = built.lower && built.lower.parts.C;
    const lowerTop = built.lower ? (A(built.lower, "top") || V([0, 0, 0.5])).add(lowerObj.position) : new THREE.Vector3(0, 0, 0);

    // 3. torso: bottom anchor on the legs' top anchor, then into contact and centred
    let torsoObj = null;
    if (built.torso) {
      torsoObj = built.torso.parts.C;
      const pos = built.lower ? lowerTop.clone().sub(A(built.torso, "bottom") || new THREE.Vector3()) : new THREE.Vector3(0, 0, -built.torso.ground_z * built.torso.s);
      place(torsoObj, pos);
      if (cross(built.torso, built.lower)) {
        const bt = box(torsoObj), bl = box(lowerObj);
        const overlap = bl.max.z - bt.min.z;            // > 0: torso bottom is inside the legs' top
        if (overlap > 0.02) torsoObj.position.z += overlap - 0.01;
        else if (overlap < -0.02) torsoObj.position.z += overlap + 0.01;   // floating: bring it down to a 1 cm gap
        const c = bl.getCenter(new THREE.Vector3()), ct = box(torsoObj).getCenter(new THREE.Vector3());
        torsoObj.position.x += c.x - ct.x; torsoObj.position.y += c.y - ct.y;
      }
    }
    const torsoBox = torsoObj ? box(torsoObj) : null;
    const shoulderPt = (s) => {
      if (torsoObj && A(built.torso, "shoulder_" + s)) return A(built.torso, "shoulder_" + s).add(torsoObj.position);
      const base = torsoBox ? new THREE.Vector3(torsoBox.getCenter(new THREE.Vector3()).x, 0, torsoBox.max.z - 0.05) : lowerTop.clone().add(new THREE.Vector3(0, 0, 0.3));
      return base.add(new THREE.Vector3(0, (torsoBox ? torsoBox.max.y : 0.16) * (s === "L" ? 1 : -1), 0));
    };

    // 4. arms at the shoulders, pushed out of the torso if they intersect it, pulled in if they float
    const wristPt = {}, armObj = {}, shoulderUsed = {};
    if (built.arms) for (const s of ["L", "R"]) if (built.arms.parts[s]) {
      const grp = built.arms.parts[s]; armObj[s] = grp;
      const sh = shoulderPt(s); shoulderUsed[s] = sh;
      place(grp, sh.clone().sub(A(built.arms, "shoulder_" + s) || new THREE.Vector3()));
      if (torsoBox && cross(built.arms, built.torso)) {
        const sign = s === "L" ? 1 : -1;
        const ba = box(grp);
        const inner = sign > 0 ? ba.min.y : -ba.max.y, wall = sign > 0 ? torsoBox.max.y : -torsoBox.min.y;   // distances along the outward direction
        const gap = inner - wall;
        if (gap < 0.005) grp.position.y += sign * (0.005 - gap);
        else if (gap > 0.04) grp.position.y -= sign * (gap - 0.01);
        // keep the shoulder near the torso's top: an arm hanging from the middle of the chest looks wrong
        const top = box(grp).max.z, want = torsoBox.max.z - 0.03;
        if (top < want - 0.05) grp.position.z += want - top;
        shoulderUsed[s] = sh.clone().add(grp.position).sub(sh.clone().sub(A(built.arms, "shoulder_" + s) || new THREE.Vector3()));
      }
      wristPt[s] = (A(built.arms, "wrist_" + s) || new THREE.Vector3(0, 0, -0.45)).add(grp.position);
    }

    // 5. hands at the wrists, dropped below the arm if they run into it
    if (built.hands) for (const s of ["L", "R"]) if (built.hands.parts[s]) {
      const grp = built.hands.parts[s];
      const w = wristPt[s] || shoulderPt(s).add(new THREE.Vector3(0, 0, -0.45));
      place(grp, w.clone().sub(A(built.hands, "wrist_" + s) || new THREE.Vector3()));
      if (armObj[s] && cross(built.hands, built.arms)) {
        const bh = box(grp), ba = box(armObj[s]);
        const overlap = bh.max.z - ba.min.z;
        if (overlap > 0.01) grp.position.z -= overlap - 0.005;
        else if (overlap < -0.03) grp.position.z -= overlap + 0.01;
      }
      wristPt[s] = w;
    }

    // 6. head on the torso top, centred, in contact
    let headPt = null;
    if (built.head) {
      const grp = built.head.parts.C;
      const top = torsoObj && A(built.torso, "top") ? A(built.torso, "top").add(torsoObj.position) : (torsoBox ? new THREE.Vector3(torsoBox.getCenter(new THREE.Vector3()).x, 0, torsoBox.max.z) : lowerTop.clone().add(new THREE.Vector3(0, 0, 0.4)));
      place(grp, top.clone().sub(A(built.head, "bottom") || new THREE.Vector3()));
      if (torsoBox && cross(built.head, built.torso)) {
        const bh = box(grp);
        const overlap = torsoBox.max.z - bh.min.z;
        if (overlap > 0.01) grp.position.z += overlap - 0.005;
        else if (overlap < -0.03) grp.position.z += overlap + 0.01;
        const ch = box(grp).getCenter(new THREE.Vector3()), ct = torsoBox.getCenter(new THREE.Vector3());
        grp.position.x += ct.x - ch.x; grp.position.y += ct.y - ch.y;
        headPt = new THREE.Vector3(ct.x, ct.y, torsoBox.max.z);
      } else headPt = top;
    }

    // 7. explode offsets, or joint markers coloured by the checklist
    if (explode) { const idx = { lower: 0, torso: 1, arms: 2, hands: 3, head: 4 }; for (const [slot, b] of Object.entries(built)) for (const grp of Object.values(b.parts)) grp.position.add(ex(idx[slot])); }
    else {
      const dot = (p, st) => { if (!p) return; const col = STATUS_COLOR[st] || STATUS_COLOR.unknown; const m = new THREE.Mesh(new THREE.SphereGeometry(0.018, 16, 12), new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: 0.35 })); m.position.copy(p); markers.add(m); };
      if (built.lower && built.torso) dot(lowerTop, links.waist);
      if (built.torso && built.arms) for (const s of ["L", "R"]) dot(shoulderUsed[s], links.shoulders);
      if (built.arms && built.hands) for (const s of ["L", "R"]) dot(wristPt[s], links.wrists);
      if (built.torso && built.head) dot(headPt, links.head);
    }

    if (legendEl) legendEl.innerHTML = SLOT_ORDER.filter(s => sel[s]).map(s => `<li><i style="background:#${(PALETTE[sel[s].robot] || 0x999999).toString(16).padStart(6, "0")}"></i>${sel[s].name}${Math.abs(built[s].s - 1) > 0.02 ? ` <small>×${built[s].s.toFixed(2)}</small>` : ""}${built[s].placeholder ? ' <span class="pill warn">no public geometry, box stands in</span>' : ""}</li>`).join("");
    const notes = [];
    if (scaled.length) notes.push(`Drawn at ${scaled.map(b => b.mod.name + " ×" + b.s.toFixed(2)).join(", ")} to match ${robots[ref.robot].name}${(robots[ref.robot] || {}).height_mm ? "'s height" : "'s leg height (" + (refH / 1000).toFixed(2) + " m body implied)"}; the real parts are not scaled.`);
    if (Object.values(built).some(b => b.placeholder)) notes.push("Boxes stand in for modules whose projects publish no assembled geometry.");
    if (!explode && Object.keys(links).length) notes.push("Joint dots: green verified, blue same design unbuilt, amber unverified, red adapter needed.");
    statusEl && (statusEl.textContent = notes.join(" "));
    fit();
  }

  const selectionOf = (d) => { const s = {}; for (const k of SLOT_ORDER) s[k] = d && d[k] ? d[k] : null; s._links = (d && d._links) || {}; return s; };
  document.addEventListener("foh:selection", e => show(selectionOf(e.detail)));
  if (window._mixSelection) show(selectionOf(window._mixSelection));
}
