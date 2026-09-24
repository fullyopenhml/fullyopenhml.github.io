/* Fully Open Humanoid — procedural CAD-style viewer.
 *
 * Builds the robot from assets/data/robot.json: every part occurrence is a
 * group of simple solids (boxes, cylinders, tubes) placed in its link frame;
 * links hang from joints; joints rotate about their axis.  Nothing here is a
 * mesh export — the JSON is the model, so the page stays small.
 *
 * Usage (ES module):
 *   import { createRobotViewer } from "./robot-viewer.js";
 *   const v = await createRobotViewer(el, { dataUrl, mode: "full"|"hero" });
 *   v.select(occ) / v.fitTo(occ|null) / v.setJoint(id, deg) / v.setPose(name)
 *   v.explode(t) / v.xray(bool) / v.setVisible(occ, bool) / v.isolate(occ[]) / v.showAll()
 *   v.setView("iso"|"front"|"side"|"top") / v.on("select", fn) / v.on("hover", fn)
 */
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";

const SEL = 0xff6a1f;
const HOV = 0xffb347;

function hex(s) { return parseInt(s.replace("#", ""), 16); }

export async function createRobotViewer(container, opts = {}) {
  const mode = opts.mode || "full";
  const data = opts.data || await (await fetch(opts.dataUrl || "assets/data/robot.json")).json();

  // ---- renderer / scene -----------------------------------------------------
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  container.appendChild(renderer.domElement);
  renderer.domElement.style.touchAction = mode === "hero" ? "pan-y" : "none";

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(32, 1, 5, 30000);
  camera.up.set(0, 0, 1);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.09;
  controls.screenSpacePanning = true;
  controls.minDistance = 120;
  controls.maxDistance = 9000;
  controls.maxPolarAngle = Math.PI * 0.98;
  if (mode === "hero") {
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.9;
    controls.enableZoom = false;
    controls.enablePan = false;
  }

  // Lights
  const hemi = new THREE.HemisphereLight(0xffffff, 0x9aa5b5, 0.85);
  scene.add(hemi);
  const key = new THREE.DirectionalLight(0xffffff, 1.7);
  key.position.set(1600, -1300, 2400);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.bias = -0.0004;
  key.shadow.normalBias = 2;
  const sc = key.shadow.camera;
  sc.left = -900; sc.right = 900; sc.top = 900; sc.bottom = -900; sc.near = 200; sc.far = 6000;
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xffffff, 0.45);
  fill.position.set(-1400, 1600, 900);
  scene.add(fill);
  const rim = new THREE.DirectionalLight(0xffffff, 0.3);
  rim.position.set(-600, -1800, 400);
  scene.add(rim);

  // Ground: shadow catcher + grid in the XY plane (Z up)
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(6000, 6000), new THREE.ShadowMaterial({ opacity: 0.16 }));
  ground.receiveShadow = true;
  ground.position.z = -0.5;
  scene.add(ground);
  const gridColor = () => hex(getComputedStyle(container).getPropertyValue("--grid").trim() || "#b9bec6");
  let grid = makeGrid(gridColor());
  scene.add(grid);
  function makeGrid(color) {
    const g = new THREE.GridHelper(3000, 30, color, color);
    g.rotation.x = Math.PI / 2;
    g.material.transparent = true;
    g.material.opacity = 0.35;
    g.position.z = -1;
    return g;
  }
  document.addEventListener("foh-theme", () => { scene.remove(grid); grid = makeGrid(gridColor()); grid.visible = showGrid; scene.add(grid); });
  let showGrid = opts.showGrid !== false;
  grid.visible = showGrid;

  // ---- build the robot ------------------------------------------------------
  const mats = data.materials;
  const catalog = data.catalog;
  const linkById = {};
  const jointById = {};
  const parts = new Map();      // occ -> record
  const meshes = [];            // pickable meshes
  const robot = new THREE.Group();
  robot.name = "robot";
  scene.add(robot);

  const geoCache = new Map();
  function geometry(sh) {
    const k = JSON.stringify([sh.t, sh.s, sh.rd, sh.axis, sh.r, sh.ri, sh.l]);
    if (geoCache.has(k)) return geoCache.get(k);
    let g;
    if (sh.t === "box") {
      g = sh.rd ? new RoundedBoxGeometry(sh.s[0], sh.s[1], sh.s[2], 3, Math.min(sh.rd, Math.min(...sh.s) / 2.01))
                : new THREE.BoxGeometry(sh.s[0], sh.s[1], sh.s[2]);
    } else {
      const seg = sh.r > 40 ? 64 : sh.r > 20 ? 48 : 32;
      if (sh.ri) {
        const shape = new THREE.Shape();
        shape.absarc(0, 0, sh.r, 0, Math.PI * 2, false);
        const hole = new THREE.Path();
        hole.absarc(0, 0, sh.ri, 0, Math.PI * 2, true);
        shape.holes.push(hole);
        g = new THREE.ExtrudeGeometry(shape, { depth: sh.l, bevelEnabled: false, curveSegments: seg });
        g.translate(0, 0, -sh.l / 2);           // extrude along +Z, centre it
        if (sh.axis === "x") g.rotateY(Math.PI / 2);
        else if (sh.axis === "y") g.rotateX(Math.PI / 2);
      } else {
        g = new THREE.CylinderGeometry(sh.r, sh.r, sh.l, seg);   // along Y
        if (sh.axis === "x") g.rotateZ(Math.PI / 2);
        else if (sh.axis === "z") g.rotateX(Math.PI / 2);
      }
    }
    g.computeVertexNormals();
    geoCache.set(k, g);
    return g;
  }

  const edgeCache = new Map();
  function edges(sh, g) {
    const k = JSON.stringify([sh.t, sh.s, sh.rd, sh.axis, sh.r, sh.ri, sh.l]);
    if (edgeCache.has(k)) return edgeCache.get(k);
    const e = new THREE.EdgesGeometry(g, sh.t === "box" && sh.rd ? 40 : 28);
    edgeCache.set(k, e);
    return e;
  }
  const edgeMat = new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.22 });

  function material(mkey, category) {
    const m = mats[mkey] || mats.petg_cf;
    const col = hex(m.color);
    if (mkey === "actuator") return new THREE.MeshStandardMaterial({ color: col, roughness: 0.42, metalness: 0.55 });
    if (mkey === "flange" || mkey === "steel" || mkey === "al_ext") return new THREE.MeshStandardMaterial({ color: col, roughness: 0.3, metalness: 0.85 });
    if (mkey === "tpu") return new THREE.MeshStandardMaterial({ color: col, roughness: 0.9, metalness: 0.0 });
    if (category === "electronics") return new THREE.MeshStandardMaterial({ color: col, roughness: 0.6, metalness: 0.15 });
    return new THREE.MeshStandardMaterial({ color: col, roughness: 0.62, metalness: 0.05 });
  }

  // link groups
  for (const L of data.links) {
    const g = new THREE.Group();
    g.name = "link:" + L.id;
    L._group = g;
    linkById[L.id] = L;
    // centroid of the link's parts (local), used for explode
    const cs = L.parts.map(p => p.center);
    L._centroid = cs.length ? cs.reduce((a, c) => [a[0] + c[0], a[1] + c[1], a[2] + c[2]], [0, 0, 0]).map(v => v / cs.length) : [0, 0, 0];
    for (const P of L.parts) {
      const cat = catalog[P.part];
      const pg = new THREE.Group();
      pg.name = "part:" + P.occ;
      const mkey = cat.material;
      for (const sh of P.shapes) {
        const geo = geometry(sh);
        const mat = material(sh.m || mkey, cat.category);
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(sh.c[0], sh.c[1], sh.c[2]);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.userData.occ = P.occ;
        mesh.userData.baseColor = mat.color.getHex();
        pg.add(mesh);
        meshes.push(mesh);
        if (mode === "full") {
          const ln = new THREE.LineSegments(edges(sh, geo), edgeMat);
          ln.position.copy(mesh.position);
          ln.userData.isEdge = true;
          pg.add(ln);
        }
      }
      pg.userData = { occ: P.occ, part: P.part, link: L.id, center: P.center, optional: P.optional || null };
      const dir = new THREE.Vector3(P.center[0] - L._centroid[0], P.center[1] - L._centroid[1], P.center[2] - L._centroid[2]);
      if (dir.length() < 1) dir.set(0, 0, 1);
      dir.normalize();
      pg.userData.explodeDir = dir;
      g.add(pg);
      parts.set(P.occ, { occ: P.occ, part: P.part, cat, link: L, group: pg, meshes: pg.children.filter(c => c.isMesh), hidden: false, optional: P.optional || null });
    }
  }
  // joints
  for (const J of data.joints) {
    jointById[J.id] = J;
    const parent = linkById[J.parent];
    const child = linkById[J.child];
    const jg = new THREE.Group();
    jg.name = "joint:" + J.id;
    jg.position.set(J.origin[0] - parent.origin[0], J.origin[1] - parent.origin[1], J.origin[2] - parent.origin[2]);
    jg.add(child._group);
    parent._group.add(jg);
    J._group = jg;
    J._axis = new THREE.Vector3(...J.axis).normalize();
    J._angle = 0;
    // explode direction along the chain: child centroid (world) - parent centroid (world)
    const cw = child._centroid.map((v, i) => v + child.origin[i]);
    const pw = parent._centroid.map((v, i) => v + parent.origin[i]);
    const d = new THREE.Vector3(cw[0] - pw[0], cw[1] - pw[1], cw[2] - pw[2]);
    if (d.length() < 1) d.set(0, 0, 1);
    J._explodeDir = d.normalize();
    J._basePos = jg.position.clone();
  }
  const rootLink = data.links.find(L => !L.parent_joint);
  robot.add(rootLink._group);

  // ---- state ----------------------------------------------------------------
  const listeners = { select: [], hover: [], visibility: [] };
  function emit(ev, arg) { for (const f of listeners[ev]) f(arg); }
  let selected = null;
  let hovered = null;
  let xrayOn = false;
  let explodeT = 0;
  let showOptional = true;
  let showEdges = mode === "full";

  function applyMaterialState() {
    for (const rec of parts.values()) {
      const isSel = rec.occ === selected;
      const isHov = rec.occ === hovered && !isSel;
      for (const m of rec.meshes) {
        const mat = m.material;
        mat.emissive.setHex(isSel ? SEL : isHov ? HOV : 0x000000);
        mat.emissiveIntensity = isSel ? 0.55 : isHov ? 0.35 : 0;
        const ghost = xrayOn && !isSel;
        mat.transparent = ghost;
        mat.opacity = ghost ? 0.14 : 1;
        mat.depthWrite = !ghost;
        mat.needsUpdate = false;
      }
      for (const c of rec.group.children) if (c.userData.isEdge) c.visible = showEdges && !(xrayOn && !isSel);
    }
  }
  function applyVisibility() {
    for (const rec of parts.values()) {
      const vis = !rec.hidden && (showOptional || !rec.optional);
      rec.group.visible = vis;
    }
    emit("visibility", null);
  }

  // ---- picking --------------------------------------------------------------
  const ray = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  let downPos = null;
  function pick(ev) {
    const r = renderer.domElement.getBoundingClientRect();
    ndc.x = ((ev.clientX - r.left) / r.width) * 2 - 1;
    ndc.y = -((ev.clientY - r.top) / r.height) * 2 + 1;
    ray.setFromCamera(ndc, camera);
    const hits = ray.intersectObjects(meshes.filter(m => m.visible && m.parent.visible && (!xrayOn || m.material.opacity > 0.5 || true)), false);
    for (const h of hits) {
      const rec = parts.get(h.object.userData.occ);
      if (rec && rec.group.visible) return rec;
    }
    return null;
  }
  if (mode === "full") {
    let lastHover = 0;
    renderer.domElement.addEventListener("pointermove", ev => {
      const now = performance.now();
      if (now - lastHover < 40) return;
      lastHover = now;
      const rec = pick(ev);
      const occ = rec ? rec.occ : null;
      if (occ !== hovered) { hovered = occ; applyMaterialState(); emit("hover", rec); renderer.domElement.style.cursor = occ ? "pointer" : ""; }
    });
    renderer.domElement.addEventListener("pointerleave", () => { if (hovered) { hovered = null; applyMaterialState(); emit("hover", null); } });
    renderer.domElement.addEventListener("pointerdown", ev => { downPos = [ev.clientX, ev.clientY]; });
    renderer.domElement.addEventListener("pointerup", ev => {
      if (!downPos) return;
      const moved = Math.hypot(ev.clientX - downPos[0], ev.clientY - downPos[1]);
      downPos = null;
      if (moved > 5) return;
      const rec = pick(ev);
      select(rec ? rec.occ : null);
    });
    renderer.domElement.addEventListener("dblclick", ev => { const rec = pick(ev); if (rec) fitTo(rec.occ); });
  }

  // ---- API ------------------------------------------------------------------
  function select(occ) {
    if (occ && !parts.has(occ)) occ = null;
    selected = occ;
    applyMaterialState();
    emit("select", occ ? parts.get(occ) : null);
  }
  function setJoint(id, deg) {
    const J = jointById[id];
    if (!J) return;
    J._angle = deg;
    J._group.quaternion.setFromAxisAngle(J._axis, THREE.MathUtils.degToRad(deg));
  }
  function getJoint(id) { const J = jointById[id]; return J ? J._angle : 0; }
  function setPose(name) {
    const pose = data.poses[name];
    if (!pose) return;
    for (const J of data.joints) setJoint(J.id, pose.q[J.id] || 0);
  }
  function explode(t) {
    explodeT = t;
    for (const J of data.joints) {
      J._group.position.copy(J._basePos).addScaledVector(J._explodeDir, 130 * t);
    }
    for (const rec of parts.values()) {
      rec.group.position.copy(rec.group.userData.explodeDir).multiplyScalar(48 * t);
    }
  }
  function xray(on) { xrayOn = !!on; applyMaterialState(); }
  function setEdges(on) { showEdges = !!on; applyMaterialState(); }
  function setGrid(on) { showGrid = !!on; grid.visible = showGrid; ground.visible = showGrid; }
  function setOptional(on) { showOptional = !!on; applyVisibility(); }
  function setVisible(occ, on) { const rec = parts.get(occ); if (!rec) return; rec.hidden = !on; applyVisibility(); }
  function setVisibleMany(occs, on) { for (const o of occs) { const rec = parts.get(o); if (rec) rec.hidden = !on; } applyVisibility(); }
  function isolate(occs) {
    const keep = new Set(occs);
    for (const rec of parts.values()) rec.hidden = !keep.has(rec.occ);
    applyVisibility();
  }
  function showAll() { for (const rec of parts.values()) rec.hidden = false; applyVisibility(); }
  function isHidden(occ) { const rec = parts.get(occ); return rec ? rec.hidden : false; }

  const box = new THREE.Box3();
  const sphere = new THREE.Sphere();
  function boundsOf(target) {
    robot.updateMatrixWorld(true);
    box.makeEmpty();
    if (target) {
      const rec = parts.get(target);
      if (rec) box.setFromObject(rec.group);
    }
    if (box.isEmpty()) {
      for (const rec of parts.values()) if (rec.group.visible) box.expandByObject(rec.group);
    }
    if (box.isEmpty()) box.set(new THREE.Vector3(-300, -300, 0), new THREE.Vector3(300, 300, 1100));
    box.getBoundingSphere(sphere);
    return sphere;
  }
  function fitTo(target, animate = true) {
    const s = boundsOf(target);
    const dist = Math.max(s.radius, 60) / Math.sin(THREE.MathUtils.degToRad(camera.fov / 2)) * 1.15;
    const dir = new THREE.Vector3().subVectors(camera.position, controls.target).normalize();
    if (dir.length() < 0.01) dir.set(1, -1, 0.7).normalize();
    flyTo(s.center.clone(), s.center.clone().addScaledVector(dir, dist), animate);
  }
  const VIEWS = { iso: [1, -1, 0.72], front: [1, 0, 0.02], back: [-1, 0, 0.02], side: [0, -1, 0.02], top: [0.0001, 0, 1] };
  function setView(name, target = null, animate = true) {
    const s = boundsOf(target);
    const dir = new THREE.Vector3(...(VIEWS[name] || VIEWS.iso)).normalize();
    const dist = Math.max(s.radius, 60) / Math.sin(THREE.MathUtils.degToRad(camera.fov / 2)) * 1.15;
    flyTo(s.center.clone(), s.center.clone().addScaledVector(dir, dist), animate);
  }
  let fly = null;
  function flyTo(target, pos, animate) {
    if (!animate) { controls.target.copy(target); camera.position.copy(pos); controls.update(); return; }
    fly = { t0: performance.now(), dur: 420, fromT: controls.target.clone(), fromP: camera.position.clone(), toT: target, toP: pos };
  }

  // ---- resize / loop --------------------------------------------------------
  function resize() {
    const w = container.clientWidth || 300;
    const h = container.clientHeight || 300;
    renderer.setSize(w, h, false);
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  const ro = new ResizeObserver(resize);
  ro.observe(container);
  resize();

  let running = true;
  let visibleInViewport = true;
  const io = new IntersectionObserver(es => { visibleInViewport = es[0].isIntersecting; }, { threshold: 0.02 });
  io.observe(container);
  function loop() {
    if (!running) return;
    requestAnimationFrame(loop);
    if (!visibleInViewport) return;
    if (fly) {
      const k = Math.min(1, (performance.now() - fly.t0) / fly.dur);
      const e = 1 - Math.pow(1 - k, 3);
      controls.target.lerpVectors(fly.fromT, fly.toT, e);
      camera.position.lerpVectors(fly.fromP, fly.toP, e);
      if (k >= 1) fly = null;
    }
    controls.update();
    renderer.render(scene, camera);
  }

  // initial view
  applyVisibility();
  applyMaterialState();
  const s0 = boundsOf(null);
  const d0 = s0.radius / Math.sin(THREE.MathUtils.degToRad(camera.fov / 2)) * (mode === "hero" ? 0.92 : 1.12);
  const dir0 = new THREE.Vector3(...VIEWS.iso).normalize();
  controls.target.copy(s0.center);
  camera.position.copy(s0.center).addScaledVector(dir0, d0);
  controls.update();
  loop();

  return {
    scene, camera, controls, renderer, data, parts, linkById, jointById,
    select, getSelected: () => selected, fitTo, setView, setJoint, getJoint, setPose, explode, xray, setEdges, setGrid,
    setOptional, setVisible, setVisibleMany, isolate, showAll, isHidden, resize,
    on(ev, fn) { listeners[ev].push(fn); },
    setAutoRotate(on) { controls.autoRotate = !!on; },
    dispose() { running = false; ro.disconnect(); io.disconnect(); renderer.dispose(); },
  };
}
