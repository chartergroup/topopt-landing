const clip = document.querySelector('#hero-clip');
const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
const applyMotion = () => {
  if (motion.matches) { clip.pause(); clip.removeAttribute('autoplay'); }
  else { clip.setAttribute('autoplay', ''); clip.play().catch(() => {}); }
};
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
