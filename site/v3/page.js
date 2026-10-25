/* Two small controls. The page works without this file. */
(function () {
  var clip = document.getElementById("hero-clip");
  var clipBtn = document.getElementById("clip-btn");
  var copyBtn = document.getElementById("copy-btn");
  var cmd = document.getElementById("cmd-text");

  if (clip && clipBtn && window.matchMedia) {
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    var label = function () {
      var word = clip.paused ? "Play" : "Pause";
      clipBtn.textContent = word;
      clipBtn.setAttribute("aria-label", word + " the clip");
    };
    clip.controls = false;
    clipBtn.hidden = false;
    clipBtn.addEventListener("click", function () {
      if (clip.paused) { clip.play(); } else { clip.pause(); }
    });
    clip.addEventListener("play", label);
    clip.addEventListener("pause", label);
    if (!reduced.matches) {
      var started = clip.play();
      if (started && started.catch) { started.catch(label); }
    }
    label();
  }

  if (copyBtn && cmd) {
    var lines = function () {
      return Array.prototype.map.call(cmd.querySelectorAll(".cmd"), function (el) {
        return el.textContent;
      }).join("\n");
    };
    var done = function () {
      copyBtn.textContent = "Copied";
      window.setTimeout(function () { copyBtn.textContent = "Copy"; }, 1600);
    };
    var fallback = function (text) {
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.top = "0";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      try { if (document.execCommand("copy")) { done(); } } catch (e) { /* nothing to do */ }
      document.body.removeChild(area);
    };
    copyBtn.hidden = false;
    copyBtn.setAttribute("aria-live", "polite");
    copyBtn.addEventListener("click", function () {
      var text = lines();
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { fallback(text); });
      } else {
        fallback(text);
      }
    });
  }
})();
