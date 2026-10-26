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
document.querySelectorAll('.copy-button').forEach((b) => b.addEventListener('click', async (event) => {
  const button = event.currentTarget;
  try {
    await navigator.clipboard.writeText(document.getElementById(button.dataset.target).textContent.trim());
    button.textContent = 'Copied';
    setTimeout(() => { button.textContent = 'Copy'; }, 2000);
  } catch {
    button.textContent = 'Select the commands to copy';
  }
}));
