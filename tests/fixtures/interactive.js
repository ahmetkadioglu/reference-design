// A Unicode marker exercises UTF-16 source offsets: 🌿
function toggleMenu() {
  const trigger = document.querySelector('#menu-toggle');
  const panel = document.querySelector('#menu');
  const open = trigger.getAttribute('aria-expanded') !== 'true';
  trigger.setAttribute('aria-expanded', String(open));
  panel.hidden = !open;
  localStorage.setItem('menu-open', String(open));
}
document.querySelector('#menu-toggle').addEventListener('click', toggleMenu);
function selectAvailability() {
  document.querySelector('#tab-one').setAttribute('aria-selected', 'false');
  document.querySelector('#tab-two').setAttribute('aria-selected', 'true');
  document.querySelector('#panel-one').hidden = true;
  document.querySelector('#panel-two').hidden = false;
}
document.querySelector('#tab-two').addEventListener('click', selectAvailability);
document.querySelector('#open-dialog').addEventListener('click', function openGuide() {
  document.querySelector('#dialog').showModal();
});
document.querySelector('#close-dialog').addEventListener('click', function closeGuide() {
  document.querySelector('#dialog').close();
});
window.addEventListener('scroll', function updateHeader() {
  document.querySelector('#header').setAttribute('data-scrolled', String(window.scrollY > 150));
}, {passive: true});
if (localStorage.getItem('menu-open') === 'true') toggleMenu();
