/* Shared behaviour: theme toggle, mobile nav, active link, in-page TOC, data helpers. */
(function () {
  const root = document.documentElement;
  const stored = (() => { try { return localStorage.getItem("foh-theme"); } catch (e) { return null; } })();
  if (stored === "dark" || stored === "light") root.setAttribute("data-theme", stored);
  const qt = new URLSearchParams(location.search).get("theme");
  if (qt === "dark" || qt === "light") root.setAttribute("data-theme", qt);

  function currentTheme() {
    const t = root.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  window.fohTheme = currentTheme;

  document.addEventListener("DOMContentLoaded", () => {
    // Active nav link
    const here = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".nav a[href]").forEach(a => {
      const target = a.getAttribute("href").split("#")[0];
      if (target === here || (here === "" && target === "index.html")) a.classList.add("active");
    });
    // Mobile nav
    const tog = document.querySelector(".nav-toggle");
    const nav = document.querySelector(".nav");
    if (tog && nav) tog.addEventListener("click", () => nav.classList.toggle("open"));
    // Theme toggle
    document.querySelectorAll(".theme-toggle").forEach(b => {
      b.addEventListener("click", () => {
        const next = currentTheme() === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        try { localStorage.setItem("foh-theme", next); } catch (e) { /* private mode */ }
        document.dispatchEvent(new CustomEvent("foh-theme", { detail: next }));
      });
    });
    // In-page TOC from h2s
    const toc = document.querySelector("[data-toc]");
    if (toc) {
      const hs = [...document.querySelectorAll("main h2[id]")];
      if (hs.length > 1) {
        const ol = document.createElement("ol");
        hs.forEach(h => { const li = document.createElement("li"); const a = document.createElement("a"); a.href = "#" + h.id; a.textContent = h.textContent; li.appendChild(a); ol.appendChild(li); });
        const b = document.createElement("b"); b.textContent = "On this page";
        toc.appendChild(b); toc.appendChild(ol);
      } else toc.remove();
    }
    // Cost figures from bom.json: <span data-cost="core|optional|tools|core+optional" data-fmt="k|full">
    const costEls = document.querySelectorAll("[data-cost]");
    if (costEls.length) window.foh.json("assets/data/bom.json").then(bom => {
      costEls.forEach(el => {
        const v = el.dataset.cost.split("+").reduce((a, k) => a + (bom.tiers[k] || 0), 0);
        el.textContent = el.dataset.fmt === "full" ? window.foh.money(v) : "$" + (v / 1000).toFixed(1) + "k";
      });
    }).catch(() => {});
    // Auto ids for headings without one
    document.querySelectorAll("main h2:not([id]), main h3:not([id])").forEach(h => {
      h.id = h.textContent.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
    });
  });

  // Helpers used by data-driven pages
  window.foh = {
    money(v, digits) { return "$" + Number(v).toLocaleString("en-US", { minimumFractionDigits: digits ?? 0, maximumFractionDigits: digits ?? 0 }); },
    kg(g) { return (g / 1000).toFixed(1) + " kg"; },
    async json(url) { const r = await fetch(url); if (!r.ok) throw new Error(url + " " + r.status); return r.json(); },
    esc(s) { return String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); },
    partHref(id) { return "viewer.html#part=" + encodeURIComponent(id); },
  };
})();
