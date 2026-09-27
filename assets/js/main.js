document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('menu-toggle');
  const closeBtn = document.getElementById('menu-close');
  const overlay = document.getElementById('nav-overlay');
  const panel = document.getElementById('nav-panel');

  function openMenu() {
    overlay.hidden = false;
    panel.hidden = false;
  }

  function closeMenu() {
    overlay.hidden = true;
    panel.hidden = true;
  }

  toggleBtn?.addEventListener('click', openMenu);
  closeBtn?.addEventListener('click', closeMenu);
  overlay?.addEventListener('click', closeMenu);
});
