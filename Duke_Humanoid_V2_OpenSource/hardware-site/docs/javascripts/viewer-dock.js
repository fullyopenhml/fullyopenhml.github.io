/* Keeps the part viewer in sight while the file tables are read.
 *
 * Once the reader scrolls past the viewer, the viewer and its info bar move into a
 * card fixed at the bottom-right corner of the window; a placeholder keeps the page
 * from jumping. Scrolling back up puts it back in the page. The card can be hidden
 * (a small pill brings it back) or expanded (scrolls back to the full-size viewer).
 * On screens narrower than Material's desktop breakpoint nothing docks.
 *
 * Works on the same elements as viewer.js and does not touch its logic.
 */
(function () {
  "use strict";

  const DESKTOP = "(min-width: 76.25em)";   // Material: sidebars visible from here
  const ICON_EXPAND = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M5 5h6v2H7v4H5V5m14 0v6h-2V7h-4V5h6M5 19v-6h2v4h4v2H5m14 0h-6v-2h4v-4h2v6Z"/></svg>';
  const ICON_CLOSE = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M18.3 5.7 12 12l6.3 6.3-1.4 1.4L10.6 13.4 12 12 5.7 5.7l1.4-1.4L12 10.6l6.3-6.3 1.4 1.4Z"/></svg>';
  const ICON_ROBOT = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 2a2 2 0 0 1 2 2c0 .7-.4 1.4-1 1.7V7h3a3 3 0 0 1 3 3v7a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3v-7a3 3 0 0 1 3-3h3V5.7c-.6-.3-1-1-1-1.7a2 2 0 0 1 2-2m-3 9a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3m6 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3M2 11h1v5H2v-5m19 0h1v5h-1v-5Z"/></svg>';

  function init() {
    const mv = document.getElementById("dh-viewer");
    if (!mv || mv.dataset.dock) return;
    mv.dataset.dock = "1";
    // The bar follows the viewer inside .dh-viewer-block; fall back to a lookup if the
    // Markdown wrapped the viewer in a <p> of its own.
    const bar = mv.nextElementSibling && mv.nextElementSibling.classList.contains("dh-viewer-bar")
      ? mv.nextElementSibling : document.querySelector(".dh-viewer-bar");

    // Wrap viewer + bar so one element can be moved; a placeholder holds the space.
    const wrap = document.createElement("div");
    wrap.className = "dh-viewer-wrap";
    const anchor = document.createElement("div");
    anchor.className = "dh-viewer-anchor";
    mv.parentNode.insertBefore(anchor, mv);
    mv.parentNode.insertBefore(wrap, mv);
    wrap.appendChild(mv);
    if (bar) wrap.appendChild(bar);

    // Card controls (shown only while docked).
    const tools = document.createElement("div");
    tools.className = "dh-dock-tools";
    const expand = document.createElement("button");
    expand.type = "button";
    expand.className = "dh-dock-btn";
    expand.title = "Back to the full-size viewer";
    expand.setAttribute("aria-label", "Back to the full-size viewer");
    expand.innerHTML = ICON_EXPAND;
    const close = document.createElement("button");
    close.type = "button";
    close.className = "dh-dock-btn";
    close.title = "Hide the viewer";
    close.setAttribute("aria-label", "Hide the viewer");
    close.innerHTML = ICON_CLOSE;
    tools.append(expand, close);
    wrap.appendChild(tools);

    // Drag handle: a strip along the top of the card. The card body is the model (drag =
    // orbit), so moving the card needs its own grip. Position persists per browser.
    const handle = document.createElement("div");
    handle.className = "dh-dock-handle";
    handle.title = "Drag to move; double-click to send back to the corner";
    handle.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path fill="currentColor" d="M9 4h2v2H9V4m4 0h2v2h-2V4M9 8h2v2H9V8m4 0h2v2h-2V8m-4 4h2v2H9v-2m4 0h2v2h-2v-2m-4 4h2v2H9v-2m4 0h2v2h-2v-2"/></svg><span>Drag</span>';
    wrap.appendChild(handle);
    const POS_KEY = "dh-dock-pos";
    let pos = null;
    try { pos = JSON.parse(localStorage.getItem(POS_KEY) || "null"); } catch (err) { pos = null; }
    function clampPos(p) {
      const w = wrap.offsetWidth, h = wrap.offsetHeight;
      return { left: Math.min(Math.max(0, p.left), Math.max(0, innerWidth - w)),
               top: Math.min(Math.max(0, p.top), Math.max(0, innerHeight - h)) };
    }
    function applyPos() {
      if (!docked) return;
      if (!pos) { wrap.style.left = wrap.style.top = wrap.style.right = wrap.style.bottom = ""; return; }
      const p = clampPos(pos);
      wrap.style.left = p.left + "px"; wrap.style.top = p.top + "px";
      wrap.style.right = "auto"; wrap.style.bottom = "auto";
    }
    function savePos() { try { if (pos) localStorage.setItem(POS_KEY, JSON.stringify(pos)); else localStorage.removeItem(POS_KEY); } catch (err) { /* private mode */ } }
    let drag = null;
    handle.addEventListener("pointerdown", (e) => {
      if (!docked || e.button !== 0) return;
      const r = wrap.getBoundingClientRect();
      drag = { dx: e.clientX - r.left, dy: e.clientY - r.top };
      wrap.classList.add("dh-dragging");
      handle.setPointerCapture(e.pointerId);
      e.preventDefault();
    });
    handle.addEventListener("pointermove", (e) => {
      if (!drag) return;
      pos = clampPos({ left: e.clientX - drag.dx, top: e.clientY - drag.dy });
      applyPos();
    });
    function endDrag(e) {
      if (!drag) return;
      drag = null;
      wrap.classList.remove("dh-dragging");
      try { handle.releasePointerCapture(e.pointerId); } catch (err) { /* already released */ }
      savePos();
    }
    handle.addEventListener("pointerup", endDrag);
    handle.addEventListener("pointercancel", endDrag);
    handle.addEventListener("dblclick", () => { pos = null; savePos(); applyPos(); });
    // A position remembered from a wider window is pulled back inside the current one.
    window.addEventListener("resize", () => { if (docked && pos) applyPos(); });

    const pill = document.createElement("button");
    pill.type = "button";
    pill.className = "dh-dock-pill md-button";
    pill.innerHTML = ICON_ROBOT + "<span>Show the robot</span>";
    pill.hidden = true;
    document.body.appendChild(pill);

    const desktop = window.matchMedia(DESKTOP);
    let docked = false, collapsed = false, ticking = false;

    function headerBottom() {
      const h = document.querySelector(".md-header");
      return h ? h.getBoundingClientRect().bottom : 0;
    }
    // The placeholder always holds the viewer's in-page height, measured while the viewer
    // is in the page. If it grew only on docking, the threshold below would move by the
    // viewer's height at the moment of docking and the card would flicker in and out at the
    // boundary.
    let anchorHeight = 0;
    function measure() {
      if (!docked && wrap.offsetHeight) anchorHeight = wrap.offsetHeight;
    }
    // The placeholder is empty while the viewer is in the page and takes the viewer's height
    // while it is docked, so the test uses the remembered height, not the placeholder's own.
    // Hysteresis: dock a little below the boundary, undock a little above it.
    function scrolledPast() {
      const bottom = anchor.getBoundingClientRect().top + anchorHeight, limit = headerBottom() + 8;
      return docked ? bottom < limit + 40 : bottom < limit;
    }
    function dock() {
      if (docked) return;
      measure();
      anchor.style.height = anchorHeight + "px";
      wrap.classList.add("dh-docked");
      docked = true;
      applyPos();
    }
    function undock() {
      if (!docked) return;
      wrap.classList.remove("dh-docked");
      wrap.style.left = wrap.style.top = wrap.style.right = wrap.style.bottom = "";
      anchor.style.height = "";
      docked = false;
    }
    function update() {
      ticking = false;
      const past = desktop.matches && scrolledPast();
      if (!past) { undock(); pill.hidden = true; collapsed = false; return; }
      if (collapsed) { undock(); wrap.classList.add("dh-collapsed"); pill.hidden = false; return; }
      wrap.classList.remove("dh-collapsed");
      pill.hidden = true;
      dock();
    }
    function onScroll() {
      if (ticking) return;
      ticking = true;
      setTimeout(update, 40);   // a short throttle; unlike rAF it also runs in a background tab
    }

    close.addEventListener("click", () => { collapsed = true; update(); });
    pill.addEventListener("click", () => { collapsed = false; update(); });
    expand.addEventListener("click", () => {
      collapsed = false;
      undock();
      anchor.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", () => { measure(); applyPos(); onScroll(); });
    desktop.addEventListener("change", onScroll);
    mv.addEventListener("load", measure);
    measure();
    update();
  }

  if (typeof document$ !== "undefined") document$.subscribe(() => { init(); });
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => { init(); });
  else init();
})();
