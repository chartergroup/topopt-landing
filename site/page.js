const clip = document.querySelector('#hero-clip');
const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
const applyMotion = () => {
  if (motion.matches) { clip.pause(); clip.removeAttribute('autoplay'); }
  else { clip.setAttribute('autoplay', ''); clip.play().catch(() => {}); }
};
motion.addEventListener('change', applyMotion);
applyMotion();
document.querySelector('.copy-button').addEventListener('click', async (event) => {
  const button = event.currentTarget;
  try {
    await navigator.clipboard.writeText(document.querySelector('#install-command').textContent.trim());
    button.textContent = 'Copied';
    setTimeout(() => { button.textContent = 'Copy'; }, 2000);
  } catch {
    button.textContent = 'Select the commands to copy';
  }
});
