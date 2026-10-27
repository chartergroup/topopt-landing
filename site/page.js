// The favicon follows the light or dark mode of the browser. A browser draws an SVG favicon once, so a media query inside the file
// does not follow a later switch; the page swaps the file instead (favicon-light.svg: dark icon, favicon-dark.svg: light icon).
(() => {
  const scheme = window.matchMedia('(prefers-color-scheme: dark)');
  const setIcon = () => {
    const old = document.querySelector('link[rel="icon"][type="image/svg+xml"]');
    if (!old) return;
    const href = old.getAttribute('href').replace(/favicon(-light|-dark)?\.svg$/, scheme.matches ? 'favicon-dark.svg' : 'favicon-light.svg');
    if (href === old.getAttribute('href')) return;
    const icon = old.cloneNode();
    icon.setAttribute('href', href);
    old.replaceWith(icon);
  };
  scheme.addEventListener('change', setIcon);
  setIcon();
})();

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
