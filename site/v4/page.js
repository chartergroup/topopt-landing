const clip = document.querySelector('#hero-clip');
const toggle = document.querySelector('#clip-toggle');
const toggleLabel = toggle.querySelector('.clip-label');
const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
// The button shows the real state of the clip, so it stays right when the browser blocks autoplay.
const showState = () => {
  const playing = !clip.paused;
  toggle.dataset.state = playing ? 'playing' : 'paused';
  toggle.setAttribute('aria-label', playing ? 'Pause the clip' : 'Play the clip');
  toggleLabel.textContent = playing ? 'Pause' : 'Play';
};
const applyMotion = () => {
  if (motion.matches) { clip.pause(); clip.removeAttribute('autoplay'); }
  else { clip.setAttribute('autoplay', ''); clip.play().catch(() => {}); }
  showState();
};
clip.addEventListener('play', showState);
clip.addEventListener('pause', showState);
toggle.addEventListener('click', () => {
  if (clip.paused) clip.play().catch(() => {});
  else clip.pause();
});
motion.addEventListener('change', applyMotion);
applyMotion();
document.querySelectorAll('[data-copy]').forEach(button => {
  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(document.getElementById(button.dataset.copy).textContent.trim());
      button.textContent = 'Copied';
      setTimeout(() => { button.textContent = 'Copy'; }, 2000);
    } catch {
      button.textContent = 'Select the commands to copy';
    }
  });
});

// The Examples button ends at the right edge of the intro text: the button row is as wide as the longest intro line.
(function () {
  var intro = document.querySelector(".hero .intro");
  var actions = document.querySelector(".hero .actions");
  if (!intro || !actions) return;
  function fit() {
    actions.style.maxWidth = "";
    var range = document.createRange();
    range.selectNodeContents(intro);
    var left = intro.getBoundingClientRect().left;
    var right = 0;
    var rects = range.getClientRects();
    for (var i = 0; i < rects.length; i++) right = Math.max(right, rects[i].right);
    if (right > left) actions.style.maxWidth = Math.ceil(right - left) + "px";
  }
  fit();
  window.addEventListener("resize", fit);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
})();
