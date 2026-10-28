(() => {
  const dateElement = document.querySelector('#today-date');
  if (dateElement) {
    dateElement.textContent = new Intl.DateTimeFormat('en-IN', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date());
  }
  document.querySelectorAll('[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });
  document.querySelectorAll('.notice-close').forEach((button) => {
    button.addEventListener('click', () => button.closest('.notice')?.remove());
  });
})();
