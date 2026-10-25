/* topopt landing page v2: the clip control and the copy buttons. Plain JavaScript. The page works without it. */
(function () {
  "use strict";

  /* The clip: plays by itself, unless the reader asks for less motion. */
  var clip = document.getElementById("hero-clip");
  var toggle = document.getElementById("clip-toggle");
  if (clip && toggle) {
    var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)");
    var label = function () { toggle.textContent = clip.paused ? "Play clip" : "Pause clip"; };
    clip.controls = false;
    toggle.hidden = false;
    toggle.addEventListener("click", function () {
      if (clip.paused) { clip.play(); } else { clip.pause(); }
    });
    clip.addEventListener("play", label);
    clip.addEventListener("pause", label);
    if (!(reduced && reduced.matches)) {
      var started = clip.play();
      if (started && started.catch) { started.catch(label); }
    }
    label();
  }

  /* A copy button on each command. */
  if (!navigator.clipboard || !navigator.clipboard.writeText) { return; }
  var boxes = document.querySelectorAll(".cmd");
  Array.prototype.forEach.call(boxes, function (box) {
    var code = box.querySelector("code");
    if (!code) { return; }
    var button = document.createElement("button");
    button.type = "button";
    button.className = "copy";
    button.textContent = "Copy";
    button.setAttribute("aria-label", "Copy the command");
    button.addEventListener("click", function () {
      navigator.clipboard.writeText(code.textContent).then(function () {
        button.textContent = "Copied";
        window.setTimeout(function () { button.textContent = "Copy"; }, 1600);
      });
    });
    box.appendChild(button);
  });
})();
