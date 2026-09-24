// Numbers every red gap mark on the page (B1, B2, ... by page letter and document order) so a
// reviewer can point at one. tools/list_gaps.py prints the same numbering from the built site.
(function () {
  var LETTER = { "": "H", "bom": "B", "fabrication": "F", "assembly": "A", "electrical": "E",
                 "bringup": "U", "software": "S", "reference": "R" };
  function pageLetter() {
    var m = location.pathname.replace(/\/+$/, "").split("/");
    var seg = m[m.length - 1] || "";
    if (/Duke_Humanoid_V2_OpenSource$/i.test(seg) || seg === "" || seg === "index.html") return "H";
    return LETTER[seg] || seg.charAt(0).toUpperCase();
  }
  var marks = document.querySelectorAll(
    ".md-typeset .dh-missing, .md-typeset .dh-unverified, .md-typeset .pending-figure, " +
    ".md-typeset .admonition.missing > .admonition-title, .md-typeset .admonition.unverified > .admonition-title");
  var letter = pageLetter();
  marks.forEach(function (el, i) {
    var id = letter + (i + 1);
    var b = document.createElement("span");
    b.className = "dh-gap-no";
    b.textContent = id;
    b.title = "Gap " + id;
    el.id = el.id || ("gap-" + id);
    el.insertBefore(b, el.firstChild);
  });
})();
