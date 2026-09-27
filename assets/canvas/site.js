function toggleMenu() {
  document.body.classList.toggle('menu-open');
}

function toggleAcc(head) {
  var item = head.closest('.acc-item');
  var icon = head.querySelector('.acc-icon');
  var opening = !item.classList.contains('open');
  item.classList.toggle('open', opening);
  icon.textContent = opening ? '−' : '+';
}

document.addEventListener('DOMContentLoaded', function () {
  var overlay = document.getElementById('menu-overlay');
  if (overlay) overlay.addEventListener('click', toggleMenu);
});
