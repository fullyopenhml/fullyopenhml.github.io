// Exploded-view clips only (assets/exploded/*.mp4): click to pause on a frame, click
// again to resume. The demo clips elsewhere keep looping untouched. While paused a scrub bar appears under the frame so any moment can be found.
// Native <video controls> are deliberately not used: browsers also toggle playback on a
// click when controls are shown, which would cancel our own toggle.
(function () {
  function setup(video) {
    if (video.dataset.clipReady) return;
    video.dataset.clipReady = "1";
    video.tabIndex = 0;
    video.title = "Click to pause / play";
    video.removeAttribute("controls");

    var wrap = document.createElement("span");
    wrap.className = "dh-clip-wrap";
    video.parentNode.insertBefore(wrap, video);
    wrap.appendChild(video);

    var badge = document.createElement("span");
    badge.className = "dh-clip-badge";
    badge.textContent = "Paused — click the picture to play";
    wrap.appendChild(badge);

    var scrub = document.createElement("input");
    scrub.type = "range"; scrub.min = "0"; scrub.step = "0.01"; scrub.value = "0";
    scrub.className = "dh-clip-scrub";
    scrub.setAttribute("aria-label", "Scrub through the clip");
    wrap.appendChild(scrub);

    function setMax() { if (isFinite(video.duration)) scrub.max = String(video.duration); }
    function sync() { if (!scrub.matches(":active")) scrub.value = String(video.currentTime); }
    function refresh() { wrap.classList.toggle("is-paused", video.paused); }
    function toggle() { if (video.paused) video.play(); else video.pause(); }

    video.addEventListener("loadedmetadata", setMax); setMax();
    video.addEventListener("timeupdate", sync);
    video.addEventListener("play", refresh);
    video.addEventListener("pause", refresh);
    video.addEventListener("click", toggle);
    video.addEventListener("keydown", function (e) {
      if (e.key === " " || e.key === "Enter") { e.preventDefault(); toggle(); }
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
        e.preventDefault(); video.pause();
        video.currentTime = Math.max(0, video.currentTime + (e.key === "ArrowRight" ? 1 : -1) / 24);
      }
    });
    scrub.addEventListener("input", function () { video.pause(); video.currentTime = parseFloat(scrub.value); });
    refresh();
  }
  document.querySelectorAll("video.dh-clip").forEach(function (v) {
    var src = v.querySelector("source");
    if (src && /\/assets\/exploded\//.test(src.getAttribute("src") || "")) setup(v);
  });
})();
