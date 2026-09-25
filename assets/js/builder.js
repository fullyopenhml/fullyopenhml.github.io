/* Mix-and-match builder: modules from assets/data/catalog.json, compatibility checks, merged BOM, sourcing. */
foh.json("assets/data/catalog.json").then(cat => {
  const esc = foh.esc, money = foh.money;
  const robots = Object.fromEntries(cat.robots.map(r => [r.id, r]));
  const modules = Object.fromEntries(cat.modules.map(m => [m.id, m]));
  const slots = cat.slots;
  const BUILT = new Set(["walking", "commercial", "prototype"]);
  const MARK = { itemised: "", estimate: " ≈", "published-total": " †", "third-party": " ‡", unknown: "" };

  const PRESETS = [
    ["Fully Open Humanoid", { lower: "foh-lower", torso: "foh-torso", arms: "foh-arms", hands: "foh-hands", head: "foh-head" }],
    ["Duke Humanoid V2", { lower: "duke2-lower", torso: "duke2-torso", arms: "duke2-arms", hands: "duke2-hands", head: "duke2-head" }],
    ["Duke legs, FOH upper body", { lower: "duke2-lower", torso: "foh-torso", arms: "foh-arms", hands: "foh-hands", head: "foh-head" }],
    ["LeRobot legs, FOH upper body", { lower: "lerobot-lower", torso: "foh-torso", arms: "foh-arms", hands: "amazing-hands", head: "foh-head" }],
    ["Cheapest printed", { lower: "lerobot-lower", torso: "bhl-torso", arms: "bhl-arms", hands: "amazing-hands", head: null }],
  ];

  const state = Object.fromEntries(slots.map(s => [s.id, null]));
  function readHash() {
    const h = new URLSearchParams(location.hash.slice(1));
    if (h.get("robot")) {
      const rid = h.get("robot");
      for (const s of slots) state[s.id] = (cat.modules.find(m => m.robot === rid && m.slot === s.id) || {}).id || state[s.id];
      return;
    }
    let any = false;
    for (const s of slots) if (h.has(s.id)) { any = true; const v = h.get(s.id); state[s.id] = v && modules[v] ? v : null; }
    if (!any) Object.assign(state, PRESETS[0][1]);
  }
  function writeHash() {
    const p = new URLSearchParams();
    for (const s of slots) p.set(s.id, state[s.id] || "");
    history.replaceState(null, "", "#" + p.toString());
    document.getElementById("permalink").href = location.href;
  }

  // --- pickers
  const slotsEl = document.getElementById("slots");
  for (const s of slots) {
    const div = document.createElement("div"); div.className = "slot";
    const opts = cat.modules.filter(m => m.slot === s.id);
    const byRobot = {};
    for (const m of opts) (byRobot[m.robot] = byRobot[m.robot] || []).push(m);
    div.innerHTML = `<h3>${esc(s.name)}</h3><p class="d">${esc(s.desc)}</p><select data-slot="${s.id}">` +
      (s.id === "hands" || s.id === "head" ? `<option value="">none</option>` : "") +
      Object.entries(byRobot).map(([rid, ms]) => `<optgroup label="${esc(robots[rid].name)}">` + ms.map(m => `<option value="${m.id}">${esc(m.name)}${m.price_usd != null ? " · " + money(m.price_usd) + MARK[m.price_basis] : " · price n/a"}</option>`).join("") + `</optgroup>`).join("") +
      `</select><p class="m"></p>`;
    slotsEl.appendChild(div);
    div.querySelector("select").addEventListener("change", e => { state[s.id] = e.target.value || null; update(); });
  }
  const presetsEl = document.getElementById("presets");
  for (const [name, cfg] of PRESETS) {
    const b = document.createElement("button"); b.className = "btn small"; b.textContent = name;
    b.addEventListener("click", () => { for (const s of slots) state[s.id] = cfg[s.id] || null; update(); });
    presetsEl.appendChild(b);
  }

  // --- checks
  function pairCheck(a, b, ifA, ifB, label) {
    const ma = a && modules[a], mb = b && modules[b];
    if (!ma || !mb) return null;
    const ra = robots[ma.robot], rb = robots[mb.robot];
    const ia = ma[ifA], ib = mb[ifB];
    if (ma.robot === mb.robot) {
      if (ra.status === "design") return { st: "design", tag: "same design, unbuilt", text: `${label}: ${ra.name}'s own joint.`, sub: ia ? (ia.desc || ia.mount) : "" };
      if (BUILT.has(ra.status)) return { st: "verified", tag: "verified", text: `${label}: ${ra.name}'s own joint, on a built robot.`, sub: ia ? (ia.desc || ia.mount) : "" };
      return { st: "unverified", tag: "same design", text: `${label}: ${ra.name}'s own joint; the robot has not been shown built.`, sub: ia ? (ia.desc || ia.mount) : "" };
    }
    if (!ia || !ib) return { st: "unknown", tag: "unknown", text: `${label}: interface not documented for ${!ia ? ma.name : mb.name}.`, sub: "" };
    const da = ia.desc || ia.mount, db = ib.desc || ib.mount;
    if (ia.mount === ib.mount) return { st: "match", tag: "unverified", text: `${label}: both sides use the same actuator output pattern (${ia.mount}); the coupler and plate still have to be drawn and printed for this pairing.`, sub: `${ra.name}: ${da}. ${rb.name}: ${db}.` };
    return { st: "adapter", tag: "adapter needed", text: `${label}: ${ra.name} ends in "${ia.mount}", ${rb.name} expects "${ib.mount}". An adapter bracket is needed; nobody has built one.`, sub: `${ra.name}: ${da}. ${rb.name}: ${db}.` };
  }

  function checks() {
    const out = [];
    const sel = slots.map(s => state[s.id] && modules[state[s.id]]).filter(Boolean);
    const push = c => c && out.push(c);
    push(pairCheck(state.lower, state.torso, "top", "bottom", "Waist"));
    push(pairCheck(state.torso, state.arms, "side", "top", "Shoulders"));
    push(pairCheck(state.arms, state.hands, "bottom", "top", "Wrists"));
    push(pairCheck(state.torso, state.head, "top", "bottom", "Head mount"));
    // electrical
    const fams = [...new Set(sel.filter(m => (m.dof || 0) > 0 && m.family && m.family !== "none").map(m => m.family))];
    const known = fams.filter(f => cat.families[f]);
    if (fams.includes("unknown") || fams.some(f => !cat.families[f])) out.push({ st: "unknown", tag: "unknown", text: "Electrical: at least one module's actuator family is not documented.", sub: "" });
    else if (known.length === 1) {
      const f = cat.families[known[0]];
      const sameRobot = new Set(sel.map(m => m.robot)).size === 1;
      out.push({ st: sameRobot && BUILT.has(robots[sel[0].robot].status) ? "verified" : sameRobot ? "design" : "match", tag: sameRobot ? (BUILT.has(robots[sel[0].robot].status) ? "verified" : "same design") : "unverified", text: `Electrical: one actuator family, ${f.name}: one bus (${f.bus}), one protocol, ${f.voltage_v ? f.voltage_v + " V" : "voltage not stated"}.`, sub: sameRobot ? "" : "The same driver talks to every joint, but CAN IDs, bus loading and the harness are new for this combination." });
    } else if (known.length > 1) {
      const volts = [...new Set(known.map(f => cat.families[f].voltage_v).filter(v => v))];
      out.push({ st: "adapter", tag: "extra work", text: `Electrical: ${known.length} actuator families (${known.map(f => cat.families[f].name).join(", ")}). Each needs its own driver and bus adapter${volts.length > 1 ? ", and a DC-DC converter between " + volts.join(" V and ") + " V" : ""}.`, sub: "Two control loops with different rates and protocols must be merged in the low-level code." });
    }
    // payload
    const lower = state.lower && modules[state.lower];
    if (lower) {
      const upper = sel.filter(m => m.slot !== "lower");
      const unknownMass = upper.filter(m => m.mass_kg == null);
      const mass = upper.reduce((a, m) => a + (m.mass_kg || 0), 0);
      if (lower.payload_kg == null) out.push({ st: "unknown", tag: "unknown", text: `Payload: ${lower.name} has no published design payload; the upper body here is ${mass.toFixed(1)} kg${unknownMass.length ? " plus unknown masses" : ""}.`, sub: "" });
      else if (unknownMass.length) out.push({ st: "unknown", tag: "unknown", text: `Payload: the legs carry ${lower.payload_kg} kg in their own robot; ${unknownMass.map(m => m.name).join(", ")} ${unknownMass.length > 1 ? "have" : "has"} no published mass.`, sub: `Known upper-body mass ${mass.toFixed(1)} kg.` });
      else {
        const ratio = mass / lower.payload_kg;
        out.push({ st: ratio <= 1.0 ? (new Set(sel.map(m => m.robot)).size === 1 ? (BUILT.has(robots[lower.robot].status) ? "verified" : "design") : "match") : ratio <= 1.15 ? "unverified" : "adapter", tag: ratio <= 1 ? "within design" : ratio <= 1.15 ? "marginal" : "over design load", text: `Payload: ${mass.toFixed(1)} kg above the hips against ${lower.payload_kg} kg in the legs' own robot (${Math.round(ratio * 100)} %).`, sub: ratio > 1 ? "Torque margins at the knees and hips shrink in proportion; check the leg actuators' peak torque against the new mass before printing." : "" });
      }
    }
    // scale
    const scales = sel.filter(m => m.scale_mm);
    if (lower && lower.scale_mm) {
      const off = scales.filter(m => m.slot !== "lower" && (m.scale_mm / lower.scale_mm > 1.33 || m.scale_mm / lower.scale_mm < 0.75));
      if (off.length) out.push({ st: "adapter", tag: "size mismatch", text: `Scale: ${off.map(m => `${m.name} (${(m.scale_mm / 1000).toFixed(2)} m robot)`).join(", ")} against ${(lower.scale_mm / 1000).toFixed(2)} m legs.`, sub: "Hip spacing, shoulder width and reach were designed for a different body size." });
    }
    // software
    const rs = new Set(sel.map(m => m.robot));
    if (rs.size === 1) {
      const r = robots[[...rs][0]];
      out.push({ st: r.open.policy === "yes" ? "verified" : r.status === "design" ? "design" : "unverified", tag: r.open.policy === "yes" ? "released" : r.open.policy === "partial" ? "partial" : "none", text: `Software: ${r.name}'s own description and controller${r.open.policy === "yes" ? " are released." : r.open.policy === "partial" ? " are partly released." : " do not exist yet."}`, sub: (r.open_notes || {}).policy || "" });
    } else if (sel.length) {
      out.push({ st: "adapter", tag: "new work", text: "Software: a mixed body needs a new robot description (URDF/MJCF) with the combined masses, and a controller retrained or retuned on it. No existing stack covers this combination.", sub: "" });
    }
    // reported cross-project builds
    for (const vc of cat.verified_combos) {
      if (vc.modules.every(id => Object.values(state).includes(id))) out.push({ st: "verified", tag: "reported build", text: `${vc.by}: ${vc.evidence}`, sub: vc.url || "" });
    }
    // unbuilt design note
    const unbuilt = [...rs].filter(id => robots[id].status === "design");
    if (unbuilt.length) out.push({ st: "design", tag: "unbuilt", text: `${unbuilt.map(id => robots[id].name).join(", ")} is a design that has not been built; its numbers are estimates.`, sub: "" });
    return out;
  }

  function update() {
    // pickers
    for (const sel of slotsEl.querySelectorAll("select")) {
      const id = sel.dataset.slot; sel.value = state[id] || "";
      const m = state[id] && modules[state[id]];
      sel.parentElement.querySelector(".m").innerHTML = m ? `${esc(robots[m.robot].name)} · ${m.dof ?? "?"} DOF · ${m.mass_kg != null ? m.mass_kg + " kg" : "mass n/a"} · ${m.price_usd != null ? money(m.price_usd) + MARK[m.price_basis] : "price n/a"}${m.price_optional_usd ? ` (+${money(m.price_optional_usd)} optional)` : ""}<br><small>${esc(m.notes || "")}</small>` : "<small>nothing selected</small>";
    }
    const sel = slots.map(s => state[s.id] && modules[state[s.id]]).filter(Boolean);
    // checklist
    const cs = checks();
    const ul = document.getElementById("checklist"); ul.innerHTML = "";
    const ICON = { verified: "✓", design: "◐", match: "?", unverified: "?", adapter: "!", unknown: "·", ok: "✓", bad: "!" };
    for (const c of cs) { const li = document.createElement("li"); li.innerHTML = `<span class="ic ${c.st}">${ICON[c.st]}</span><span class="t">${esc(c.text)}${c.sub ? `<small>${esc(c.sub)}</small>` : ""}</span><span class="tag">${esc(c.tag)}</span>`; ul.appendChild(li); }
    const n = { verified: 0, design: 0, unverified: 0, adapter: 0, unknown: 0 };
    for (const c of cs) n[c.st === "match" ? "unverified" : c.st in n ? c.st : "unknown"]++;
    const v = document.getElementById("verdict");
    const rs = new Set(sel.map(m => m.robot));
    if (!sel.length) { v.className = "verdict"; v.innerHTML = "<b>Nothing selected.</b>"; }
    else if (rs.size === 1 && BUILT.has(robots[[...rs][0]].status)) { v.className = "verdict ok"; v.innerHTML = `<b>Verified: this is ${esc(robots[[...rs][0]].name)} as built.</b> ${n.unverified + n.adapter ? "Some checks still flag missing data." : "Every check is covered by the project's own build."}`; }
    else if (rs.size === 1) { v.className = "verdict design"; v.innerHTML = `<b>Design only: ${esc(robots[[...rs][0]].name)} has not been built.</b> The combination is self-consistent on paper; nothing has been verified in hardware.`; }
    else { v.className = "verdict warn"; v.innerHTML = `<b>Unverified combination.</b> ${n.verified} verified, ${n.unverified} unverified, ${n.adapter} needing adapters or extra work, ${n.unknown} unknown. Nobody has reported building this.`; }
    // totals
    const priced = sel.filter(m => m.price_usd != null);
    const item = priced.filter(m => m.price_basis === "itemised").reduce((a, m) => a + m.price_usd, 0);
    const est = priced.filter(m => m.price_basis !== "itemised").reduce((a, m) => a + m.price_usd, 0);
    const opt = sel.reduce((a, m) => a + (m.price_optional_usd || 0), 0);
    const unpriced = sel.filter(m => m.price_usd == null);
    const mass = sel.reduce((a, m) => a + (m.mass_kg || 0), 0), massUnknown = sel.filter(m => m.mass_kg == null).length;
    const dof = sel.reduce((a, m) => a + (m.dof || 0), 0);
    const fams = [...new Set(sel.filter(m => (m.dof || 0) > 0).map(m => m.family))];
    document.getElementById("totals").innerHTML = [
      ["Price", money(item + est), `${money(item)} itemised${est ? " + " + money(est) + " estimated" : ""}${opt ? " · " + money(opt) + " optional" : ""}${unpriced.length ? " · " + unpriced.length + " module" + (unpriced.length > 1 ? "s" : "") + " unpriced" : ""}`],
      ["Mass", mass.toFixed(1) + " kg", massUnknown ? `${massUnknown} module${massUnknown > 1 ? "s" : ""} with unknown mass` : "from the projects' figures"],
      ["Joints", String(dof), sel.map(m => `${m.dof ?? "?"} ${m.slot}`).join(" · ")],
      ["Actuator families", String(fams.length), fams.map(f => (cat.families[f] || { name: f }).name).join(", ")],
      ["Designs mixed", String(rs.size), [...rs].map(id => robots[id].name).join(", ")],
    ].map(([k, val, s]) => `<div class="tot"><div class="k">${esc(k)}</div><div class="v">${esc(val)}</div><div class="s">${esc(s)}</div></div>`).join("");
    // BOM
    const tb = document.querySelector("#bom-table tbody"); tb.innerHTML = "";
    const rows = [];
    for (const m of sel) for (const b of m.bom) rows.push(Object.assign({ module: m.name, robot: robots[m.robot].name, basis: m.price_basis }, b));
    for (const b of rows) {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td class="mod">${esc(b.module)}</td><td>${esc(b.item)}${b.note ? ` <small class="tiny">${esc(b.note)}</small>` : ""}${b.tier && b.tier !== "core" ? ' <span class="pill">optional</span>' : ""}</td><td class="num">${b.qty ?? ""}</td><td class="num">${b.unit != null ? money(b.unit, 2) : "—"}</td><td class="num">${b.total != null ? money(b.total, 2) : "—"}</td><td>${b.url ? `<a href="${esc(b.url)}">${esc(b.vendor || "link")}</a>` : esc(b.vendor || "")}</td>`;
      tb.appendChild(tr);
    }
    // sourcing
    const vendors = {};
    for (const b of rows) (vendors[b.vendor || "unspecified"] = vendors[b.vendor || "unspecified"] || { lines: 0, total: 0, url: b.url, items: [] }).lines++, vendors[b.vendor || "unspecified"].total += b.total || 0, vendors[b.vendor || "unspecified"].items.push(b.item);
    document.getElementById("vendors").innerHTML = Object.entries(vendors).sort((a, b) => b[1].total - a[1].total).map(([v, d]) => `<li><b>${d.url ? `<a href="${esc(d.url)}">${esc(v)}</a>` : esc(v)}</b> · ${d.lines} line${d.lines > 1 ? "s" : ""} · ${money(d.total)}<br><small class="tiny">${esc(d.items.slice(0, 4).join("; "))}${d.items.length > 4 ? "; …" : ""}</small></li>`).join("");
    const first = rows.filter(b => /actuator|robstride|dynamixel|cubemars|servo/i.test(b.item) || b.section === "actuators" || b.section === "cnc-parts");
    document.getElementById("order-first").innerHTML = `<span class="t">Order first:</span> ${first.length ? first.map(b => `${esc(b.item)} × ${b.qty}`).slice(0, 12).join("; ") + (first.length > 12 ? "; …" : "") : "no long-lead items in this combination"}.`;
    // report link
    const title = encodeURIComponent("Verified build: " + sel.map(m => m.name).join(" + "));
    const body = encodeURIComponent(`Combination: ${location.origin}${location.pathname}#${new URLSearchParams(Object.fromEntries(slots.map(s => [s.id, state[s.id] || ""]))).toString()}\n\nWhat I built:\n\nWhat needed changing:\n\nPhotos / links:\n`);
    document.getElementById("report").href = `https://github.com/fullyopenhml/fullyopenhml.github.io/issues/new?title=${title}&body=${body}`;
    writeHash();
    window._bomRows = rows;
  }

  document.getElementById("csv").addEventListener("click", () => {
    const rows = window._bomRows || [];
    const q = s => `"${String(s ?? "").replace(/"/g, '""')}"`;
    const csv = ["module,robot,item,qty,unit_usd,total_usd,price_basis,vendor,url,note"].concat(rows.map(b => [b.module, b.robot, b.item, b.qty, b.unit, b.total, b.basis, b.vendor, b.url, b.note].map(q).join(","))).join("\n");
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" })); a.download = "humanoid-mix-bom.csv"; a.click();
  });
  document.getElementById("permalink").addEventListener("click", e => { e.preventDefault(); navigator.clipboard && navigator.clipboard.writeText(location.href); e.target.textContent = "Link copied"; setTimeout(() => e.target.textContent = "Copy link to this combination", 1500); });
  window.addEventListener("hashchange", () => { readHash(); update(); });
  readHash(); update();
});
