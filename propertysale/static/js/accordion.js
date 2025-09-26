(function () {
  const faq = document.querySelector('.faq');
  if (!faq) return;

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  faq.querySelectorAll('.faq-item').forEach((item) => {
    const q = item.querySelector('.faq-q');
    const a = item.querySelector('.faq-a');
    if (!q || !a) return;

    // Ensure there is an icon span we can rotate (use the trailing span if present)
    let icon = q.querySelector('.faq-icon');
    if (!icon) {
      const lastSpan = q.querySelector('span:last-child');
      if (lastSpan) lastSpan.classList.add('faq-icon');
    }

    // Start collapsed
    a.style.maxHeight = '0px';
    a.style.opacity = '0';

    function open() {
      item.classList.add('is-open');
      a.style.opacity = '1';
      a.style.maxHeight = a.scrollHeight + 'px';
      if (prefersReduced) {
        a.style.maxHeight = 'none';
      } else {
        const done = () => {
          if (item.classList.contains('is-open')) a.style.maxHeight = 'none';
          a.removeEventListener('transitionend', done);
        };
        a.addEventListener('transitionend', done);
      }
    }

    function close() {
      item.classList.remove('is-open');
      if (a.style.maxHeight === 'none') {
        a.style.maxHeight = a.scrollHeight + 'px';
        void a.offsetHeight; // force reflow
      }
      a.style.opacity = '0';
      a.style.maxHeight = '0px';
    }

    q.addEventListener('click', () => {
      const isOpen = item.classList.contains('is-open');
      if (isOpen) close();
      else {
        if (a.style.maxHeight === 'none') {
          a.style.maxHeight = '0px';
          void a.offsetHeight;
        }
        open();
      }
    });
  });
})();
