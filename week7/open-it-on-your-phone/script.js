(() => {
  const polishStylesheet = document.createElement('link');
  polishStylesheet.rel = 'stylesheet';
  polishStylesheet.href = document.location.pathname.includes('/projects/')
    ? '../mobile-polish.css'
    : 'mobile-polish.css';
  document.head.appendChild(polishStylesheet);

  const toggle = document.querySelector('[data-nav-toggle]');
  const nav = document.querySelector('[data-nav]');
  const header = document.querySelector('[data-header]');
  const year = document.querySelector('[data-year]');

  if (year) year.textContent = new Date().getFullYear();

  const closeNav = () => {
    if (!toggle || !nav) return;
    toggle.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
    document.body.classList.remove('nav-open');
  };

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('is-open', !open);
      document.body.classList.toggle('nav-open', !open);
    });
    nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeNav));
    window.addEventListener('resize', () => {
      if (window.innerWidth > 760) closeNav();
    });
  }

  const setHeader = () => header?.classList.toggle('is-scrolled', window.scrollY > 16);
  setHeader();
  window.addEventListener('scroll', setHeader, { passive: true });

  document.querySelectorAll('.case-visual img').forEach((image) => {
    image.tabIndex = 0;
    image.setAttribute('role', 'link');
    image.setAttribute('aria-label', `${image.alt || 'Project diagram'}. Open full-size image in a new tab.`);

    const openImage = () => {
      window.open(image.currentSrc || image.src, '_blank', 'noopener,noreferrer');
    };

    image.addEventListener('click', openImage);
    image.addEventListener('keydown', (event) => {
      if (event.key !== 'Enter' && event.key !== ' ') return;
      event.preventDefault();
      openImage();
    });

    const hint = document.createElement('p');
    hint.className = 'image-hint';
    hint.textContent = 'Tap the diagram to view it at full size.';
    image.insertAdjacentElement('afterend', hint);
  });

  const nodes = document.querySelectorAll('[data-reveal]');
  if (
    window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
    !('IntersectionObserver' in window)
  ) {
    nodes.forEach((node) => node.classList.add('is-visible'));
    return;
  }

  const observer = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      });
    },
    { threshold: 0.12 }
  );

  nodes.forEach((node) => observer.observe(node));
})();
