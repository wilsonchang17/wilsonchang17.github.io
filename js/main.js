document.documentElement.classList.add('js');

document.addEventListener('DOMContentLoaded', () => {
    const menuButton = document.querySelector('.menu-toggle');
    const navigation = document.querySelector('.nav-list');
    const header = document.querySelector('[data-header]');

    const setMenuState = (isOpen, returnFocus = false) => {
        if (!menuButton || !navigation) return;

        menuButton.setAttribute('aria-expanded', String(isOpen));
        menuButton.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
        navigation.classList.toggle('open', isOpen);
        document.body.classList.toggle('menu-open', isOpen);

        if (returnFocus) menuButton.focus();
    };

    menuButton?.addEventListener('click', () => {
        const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
        setMenuState(!isOpen);
    });

    navigation?.querySelectorAll('a').forEach((link) => {
        link.addEventListener('click', () => setMenuState(false));
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') {
            setMenuState(false, true);
        }
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 800) setMenuState(false);
    });

    const updateHeader = () => {
        header?.classList.toggle('is-scrolled', window.scrollY > 16);
    };

    updateHeader();
    window.addEventListener('scroll', updateHeader, { passive: true });

    const revealItems = document.querySelectorAll('.reveal');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (reducedMotion || !('IntersectionObserver' in window)) {
        revealItems.forEach((item) => item.classList.add('is-visible'));
    } else {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            });
        }, { rootMargin: '0px 0px -10% 0px', threshold: 0.08 });

        revealItems.forEach((item) => observer.observe(item));
    }

    document.querySelectorAll('[data-year]').forEach((item) => {
        item.textContent = String(new Date().getFullYear());
    });
});
