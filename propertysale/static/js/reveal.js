(function () {
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* -------- Page enter -------- */
  document.addEventListener('DOMContentLoaded', () => {
    const root = document.querySelector('.page-enter');
    if (root) requestAnimationFrame(() => root.classList.add('is-visible'));
  });

  /* -------- Sticky header shadow (optional polish) -------- */
  const header = document.querySelector('header');
  if (header) {
    const onScroll = () => {
      if (window.scrollY > 6) header.classList.add('header-scrolled');
      else header.classList.remove('header-scrolled');
    };
    onScroll();
    document.addEventListener('scroll', onScroll, { passive: true });
  }

  /* -------- Reveal-on-scroll + stagger -------- */
  if (!prefersReduced) {
    const observe = (els, cb) => {
      if (!('IntersectionObserver' in window)) { els.forEach(cb); return; }
      const io = new IntersectionObserver((entries, obs) => {
        entries.forEach(e => {
          if (e.isIntersecting) { cb(e.target); obs.unobserve(e.target); }
        });
      }, { rootMargin: '0px 0px -10% 0px', threshold: 0.05 });
      els.forEach(el => io.observe(el));
    };
    observe(document.querySelectorAll('.reveal'), el => el.classList.add('is-visible'));
    observe(document.querySelectorAll('[data-stagger]'), el => el.classList.add('is-visible'));
  } else {
    document.querySelectorAll('.reveal, [data-stagger]').forEach(el => {
      el.classList.add('is-visible');
      if (el.hasAttribute('data-stagger')) {
        el.querySelectorAll(':scope > *').forEach(c => c.style.transition = 'none');
      }
    });
  }

  /* ================= FAQ accordion (smooth, preserves your UI) ================= */
  (function initFAQ() {
    const faq = document.querySelector('.faq');
    if (!faq) return;

    const items = faq.querySelectorAll('.faq-item');
    items.forEach((item, idx) => {
      const q = item.querySelector('.faq-q');
      const a = item.querySelector('.faq-a');
      if (!q || !a) return;

      // Find/create icon span (uses your existing trailing span if present)
      let icon = q.querySelector('.faq-icon');
      if (!icon) {
        // Try to use the last span inside q (you already have one with ＋)
        const lastSpan = q.querySelector('span:last-child');
        if (lastSpan) {
          lastSpan.classList.add('faq-icon');
          icon = lastSpan;
        }
      }

      // Initial collapsed state
      a.style.maxHeight = '0px';
      a.style.opacity = '0';

      function open() {
        item.classList.add('is-open');
        // Measure
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
        if (isOpen) close(); else {
          // keep others open (classic FAQ allows multiple); change here to close others if you prefer
          if (a.style.maxHeight === 'none') {
            a.style.maxHeight = '0px';
            void a.offsetHeight;
          }
          open();
        }
      });
    });
  })();
})();
