/* topopt v4. Plain JavaScript, no library. The page works without it.
   1. The clip plays by itself, unless the reader asks for less motion. A button plays and pauses it.
   2. Each command block gets a copy button. */
(function () {
  "use strict";

  var figure = document.getElementById("clip");
  var clip = document.getElementById("hero-clip");
  var toggle = document.getElementById("clip-toggle");

  if (figure && clip && toggle) {
    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    var sync = function () {
      toggle.textContent = clip.paused ? "Play clip" : "Pause clip";
      figure.classList.toggle("is-paused", clip.paused);
    };
    var flip = function () {
      if (clip.paused) {
        var started = clip.play();
        if (started && started.catch) { started.catch(sync); }
      } else {
        clip.pause();
      }
    };

    clip.controls = false;
    toggle.hidden = false;
    toggle.addEventListener("click", flip);
    clip.addEventListener("click", flip);
    clip.addEventListener("play", sync);
    clip.addEventListener("pause", sync);
    if (!reduced) { flip(); }
    sync();
  }

  var blocks = document.querySelectorAll(".cmd");
  Array.prototype.forEach.call(blocks, function (block) {
    var code = block.querySelector("code");
    if (!code) { return; }
    var button = document.createElement("button");
    button.type = "button";
    button.className = "copy";
    button.textContent = "Copy";
    button.setAttribute("aria-label", "Copy the code to the clipboard");

    var done = function (ok) {
      button.textContent = ok ? "Copied" : "Press Ctrl+C";
      window.setTimeout(function () { button.textContent = "Copy"; }, 1800);
    };
    var fallback = function () {
      var range = document.createRange();
      range.selectNodeContents(code);
      var selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (error) { ok = false; }
      done(ok);
    };

    button.addEventListener("click", function () {
      var text = code.textContent.replace(/\s+$/, "");
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, fallback);
      } else {
        fallback();
      }
    });
    block.appendChild(button);
  });
})();
