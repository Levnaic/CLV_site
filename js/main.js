(() => {
    document.documentElement.classList.add('js');

    // ---------- Translations (German text lives in the HTML, English here) ----------
    const EN = {
        title: "C'est la vie Sports Bar – Frankfurt-Niederrad",
        skip: 'Skip to content', navLabel: 'Main menu', menuOpen: 'Open menu', menuClose: 'Close menu', themeLight: 'Switch to light mode', themeDark: 'Switch to dark mode',
        navAbout: 'About', navSport: 'Live Sport', navDrinks: 'Drinks', navEvents: 'Events', navGallery: 'Gallery', navVisit: 'Find us', navContact: 'Contact',
        heroAlt: 'Bar interior (placeholder)', tagline: 'Live Sport · Cold Drinks · Good People', btnLive: 'Live today', btnRoute: 'Find us',
        aboutTitle: 'About us',
        aboutP1: 'In the heart of Frankfurt-Niederrad, fans, neighbours and friends meet at our place. Bundesliga, Champions League or a relaxed evening after work – there is always something going on.',
        aboutP2: "Big screens, proper sound and a team that knows how to pour a good drink. Welcome to C'est la vie.",
        aboutAlt: 'The team behind the bar (placeholder)',
        sportTitle: 'Live Sport', sportLead: "Never miss a match – we show the sport you want to see.",
        sport1: 'Every matchday live, including the Saturday conference.',
        sport2: 'Home or away – watch the SGE from kick-off to the final whistle.',
        sport3: "Europe's best teams on midweek evenings.",
        sport4Title: 'More highlights', sport4: 'Formula 1, darts, internationals and major tournaments.',
        sport5: 'Several big screens and sound that lets you hear every goal.',
        drinksTitle: 'Drinks', drinksLead: 'Pick a category to see all drinks with prices. Subject to change.', drinksError: 'The drinks menu could not be loaded. Please ask at the bar.',
        ev1Tag: 'Every matchday', ev1: 'Kick-off, atmosphere, drink specials. Come early, seats go fast.',
        ev2Tag: 'Regularly', ev2Title: 'Party nights', ev2: 'Music, drinks and good vibes late into the night.',
        ev1More: 'We show Bundesliga, Champions League and more on several screens. Drink specials during matches – table reservations on request. (Placeholder – to be adjusted.)',
        ev2More: 'With a DJ or playlist, cocktail specials and no fixed end. Find current dates on Instagram. (Placeholder – to be adjusted.)',
        ev3More: 'We reserve areas or the whole bar, with buffet and drink packages if needed. Message us on WhatsApp or by email. (Placeholder – to be adjusted.)',
        ev4Tag: 'Weekly', ev4Title: 'Quiz night', ev4: 'Test your knowledge as a team and win drinks.',
        ev4More: 'New questions on sport, music and general knowledge every week. Teams of up to six, sign up on site. (Placeholder – to be adjusted.)',
        ev3Tag: 'On request', ev3Title: 'Private parties', ev3: 'Birthday, club night or company party – just talk to us.',
        galleryTitle: 'Gallery',
        visitTitle: 'Opening hours & directions', btnRoute2: 'Plan route',
        mapText: 'Loading the map connects to OpenStreetMap and transfers data (e.g. your IP address).', mapBtn: 'Load map',
        contactTitle: 'Contact', phone: 'Phone', waText: 'Send us a message',
        privacy: 'Privacy policy', quick: 'Quick actions', call: 'Call', route: 'Directions',
        open: 'Open now', closed: 'Closed right now', until: 'until', lbClose: 'Close', lbPrev: 'Previous', lbNext: 'Next', zoom: 'Enlarge image',
        // legal pages
        legalTitle: 'Legal notice', legalBack: '← Back to home',
        l1h: 'Information pursuant to § 5 DDG', l1p: 'C\'est la vie Sports Bar, [Owner name], Musterstraße 1, 60528 Frankfurt am Main. (Placeholder – to be completed.)',
        l2h: 'Contact', l2p: 'Phone: +49 69 000000 · Email: info@example.com',
        l3h: 'Registration & VAT ID', l3p: '[Trade register / VAT ID – to be completed]',
        pTitle: 'Privacy policy',
        p1h: '1. Controller', p1p: 'C\'est la vie Sports Bar, [Owner name], Musterstraße 1, 60528 Frankfurt am Main, info@example.com. (Placeholder – to be completed.)',
        p2h: '2. Hosting & server logs', p2p: 'When you visit this site, the hosting provider may process technical data (IP address, time, browser) in server log files. [Provider – to be completed]',
        p3h: '3. OpenStreetMap', p3p: 'The map is only loaded after you click "Load map". Your IP address is then transferred to OpenStreetMap (OpenStreetMap Foundation).',
        p4h: '4. Cookies & local storage', p4p: 'This site sets no cookies. Your language choice is stored locally in your browser only.',
        p5h: '5. Your rights', p5p: 'You have the right to access, rectification, erasure, restriction, data portability and objection, as well as to lodge a complaint with a supervisory authority.'
    };
    const DAYS = {
        de: ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'],
        en: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    };
    const DE_DYN = { themeLight: 'Helles Design aktivieren', themeDark: 'Dunkles Design aktivieren', drinksError: 'Die Getränkekarte konnte nicht geladen werden. Bitte frag an der Theke.', open: 'Jetzt geöffnet', closed: 'Gerade geschlossen', until: 'bis', lbClose: 'Schließen', lbPrev: 'Zurück', lbNext: 'Weiter', zoom: 'Bild vergrößern', menuOpen: 'Menü öffnen', menuClose: 'Menü schließen' };

    // Opening hours (PLACEHOLDER) – index 0 = Sunday. Close > 24 means after midnight.
    const HOURS = [[14, 24], [16, 25], [16, 25], [16, 25], [16, 25], [16, 27], [16, 27]];

    const $ = (s, r = document) => r.querySelector(s);
    const $$ = (s, r = document) => [...r.querySelectorAll(s)];
    const store = {
        get: k => { try { return localStorage.getItem(k); } catch { return null; } },
        set: (k, v) => { try { localStorage.setItem(k, v); } catch { /* ignore */ } }
    };

    let lang = store.get('lang') === 'en' ? 'en' : 'de';
    const t = key => (lang === 'en' ? EN[key] : DE_DYN[key]) ?? key;

    // ---------- Theme (system default, manual override remembered) ----------
    const darkMq = window.matchMedia('(prefers-color-scheme: dark)');
    const isDark = () => (document.documentElement.dataset.theme || (darkMq.matches ? 'dark' : 'light')) === 'dark';
    function renderTheme() {
        const btn = $('#themeBtn');
        if (!btn) return;
        btn.textContent = isDark() ? '☀' : '☾';
        btn.setAttribute('aria-label', t(isDark() ? 'themeLight' : 'themeDark'));
    }
    $('#themeBtn')?.addEventListener('click', () => {
        const next = isDark() ? 'light' : 'dark';
        document.documentElement.dataset.theme = next;
        store.set('theme', next);
        renderTheme();
    });
    darkMq.addEventListener('change', renderTheme);

    // ---------- Language switch ----------
    function translate() {
        document.documentElement.lang = lang;
        const attrs = [['data-i18n', null], ['data-i18n-label', 'aria-label'], ['data-i18n-alt', 'alt']];
        attrs.forEach(([sel, attr]) => $$('[' + sel + ']').forEach(el => {
            const key = el.getAttribute(sel);
            el._de = el._de || {};
            if (el._de[sel] === undefined) el._de[sel] = attr ? el.getAttribute(attr) : el.textContent;
            const val = lang === 'en' && EN[key] ? EN[key] : el._de[sel];
            if (attr) el.setAttribute(attr, val); else el.textContent = val;
        }));
        if (!$('title').hasAttribute('data-i18n')) {
            if (!$('title').dataset.de) $('title').dataset.de = document.title;
            document.title = lang === 'en' ? EN.title : $('title').dataset.de;
        }
        const btn = $('#langBtn');
        $$('[data-l]', btn).forEach(s => s.classList.toggle('is-active', s.dataset.l === lang));
        btn.setAttribute('aria-label', lang === 'en' ? 'Auf Deutsch wechseln' : 'Switch to English');
        $$('.gallery-item').forEach(b => b.setAttribute('aria-label', t('zoom')));
        if (lb) {
            $('#lbClose').setAttribute('aria-label', t('lbClose'));
            $('#lbPrev').setAttribute('aria-label', t('lbPrev'));
            $('#lbNext').setAttribute('aria-label', t('lbNext'));
        }
        setMenu(menuOpen);
        renderHours();
        renderDrinks();
        renderTheme();
    }
    $('#langBtn').addEventListener('click', () => {
        lang = lang === 'en' ? 'de' : 'en';
        store.set('lang', lang);
        translate();
    });

    // ---------- Mobile menu ----------
    const nav = $('#nav'), menuBtn = $('#menuBtn');
    let menuOpen = false;
    function setMenu(open) {
        if (!nav) return;
        menuOpen = open;
        nav.classList.toggle('open', open);
        menuBtn.setAttribute('aria-expanded', String(open));
        menuBtn.setAttribute('aria-label', t(open ? 'menuClose' : 'menuOpen'));
        document.body.style.overflow = open ? 'hidden' : '';
    }
    if (menuBtn) menuBtn.addEventListener('click', () => setMenu(!menuOpen));
    if (nav) nav.addEventListener('click', e => { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && menuOpen && menuBtn) { setMenu(false); menuBtn.focus(); } });
    window.matchMedia('(min-width: 900px)').addEventListener('change', e => { if (e.matches) setMenu(false); });

    // ---------- Header shadow ----------
    const header = $('.site-header');
    const onScroll = () => header && header.classList.toggle('scrolled', window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    // ---------- Opening hours + open/closed badge ----------
    const fmt = h => String(h % 24).padStart(2, '0') + ':00';
    function isOpen(now) {
        const day = now.getDay(), h = now.getHours() + now.getMinutes() / 60;
        const today = HOURS[day];
        if (h >= today[0] && h < today[1]) return today[1];
        const prev = HOURS[(day + 6) % 7];
        if (prev[1] > 24 && h < prev[1] - 24) return prev[1] - 24;
        return false;
    }
    function renderHours() {
        const tbody = $('#hours');
        if (!tbody) return;
        const now = new Date();
        tbody.innerHTML = '';
        [1, 2, 3, 4, 5, 6, 0].forEach(d => {
            const tr = document.createElement('tr');
            if (d === now.getDay()) tr.className = 'today';
            const th = document.createElement('th'); th.scope = 'row'; th.textContent = DAYS[lang][d];
            const td = document.createElement('td'); td.textContent = fmt(HOURS[d][0]) + ' – ' + fmt(HOURS[d][1]);
            tr.append(th, td);
            tbody.append(tr);
        });
        const close = isOpen(now), status = $('#status');
        status.className = 'status ' + (close ? 'open' : 'closed');
        status.textContent = close ? `${t('open')} · ${t('until')} ${fmt(close)}` : t('closed');
    }
    setInterval(renderHours, 60000);

    // ---------- Drinks menu (data lives in config/drinks.json) ----------
    let drinks = null, activeCat = null;
    const loc = v => (v && typeof v === 'object') ? (v[lang] ?? v.de ?? '') : (v ?? '');
    const price = n => n.toLocaleString(lang === 'en' ? 'en-GB' : 'de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '\u00a0' + (drinks.currency || '€');
    const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; };
    function renderDrinks() {
        const tabs = $('#drinkTabs'), panel = $('#drinkPanel');
        if (!tabs) return;
        if (!drinks) return;
        const cats = drinks.categories || [];
        if (!cats.some(c => c.id === activeCat)) activeCat = cats[0] && cats[0].id;
        tabs.replaceChildren(...cats.map(c => {
            const b = el('button', 'drink-tab', loc(c.name));
            b.type = 'button'; b.id = 'tab-' + c.id; b.setAttribute('role', 'tab');
            b.setAttribute('aria-selected', String(c.id === activeCat));
            b.setAttribute('aria-controls', 'drinkPanel');
            b.tabIndex = c.id === activeCat ? 0 : -1;
            b.addEventListener('click', () => { activeCat = c.id; renderDrinks(); });
            return b;
        }));
        const cat = cats.find(c => c.id === activeCat);
        panel.setAttribute('aria-labelledby', 'tab-' + activeCat);
        panel.replaceChildren(...((cat && cat.items) || []).map((it, i) => {
            const li = el('div', 'drink-item'); li.style.setProperty('--i', i);
            const head = el('div', 'drink-head');
            const name = el('span', 'drink-name', loc(it.name));
            if (it.size) name.append(el('span', 'drink-size', it.size));
            head.append(name, el('span', 'drink-dots'), el('span', 'drink-price', price(it.price)));
            li.append(head);
            const extra = loc(it.ingredients) || loc(it.description);
            if (extra) li.append(el('p', 'drink-desc', extra));
            return li;
        }));
    }
    $('#drinkTabs')?.addEventListener('keydown', e => {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        const tabs = $$('.drink-tab'), i = tabs.indexOf(document.activeElement);
        if (i < 0) return;
        const n = tabs[(i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length];
        n.click(); $('#' + n.id).focus();
    });
    if ($('#drinkTabs')) fetch('config/drinks.json')
        .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(d => { drinks = d; renderDrinks(); })
        .catch(() => { $('#drinkPanel').replaceChildren(el('p', 'drink-desc', t('drinksError'))); });

    // ---------- Lightbox ----------
    const lb = $('#lightbox'), lbImg = $('#lbImg'), items = $$('.gallery-item');
    if (lb) {
        let idx = 0;
        const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        function show(i, dir = 0) {
            idx = (i + items.length) % items.length;
            const img = $('img', items[idx]);
            lbImg.src = img.currentSrc || img.src;
            lbImg.alt = img.alt;
            if (dir && !reduceMotion.matches && lbImg.animate) lbImg.animate(
                [{ opacity: 0, transform: `translateX(${dir * 48}px)` }, { opacity: 1, transform: 'none' }],
                { duration: 280, easing: 'cubic-bezier(.2,.7,.2,1)' });
        }
        items.forEach((b, i) => b.addEventListener('click', () => { show(i); lb.showModal(); }));
        $('#lbClose').addEventListener('click', () => lb.close());
        $('#lbPrev').addEventListener('click', () => show(idx - 1, -1));
        $('#lbNext').addEventListener('click', () => show(idx + 1, 1));
        lb.addEventListener('click', e => { if (e.target === lb) lb.close(); });
        lb.addEventListener('keydown', e => {
            if (e.key === 'ArrowLeft') show(idx - 1, -1);
            if (e.key === 'ArrowRight') show(idx + 1, 1);
        });
        let touchX = null;
        lb.addEventListener('touchstart', e => { touchX = e.changedTouches[0].clientX; }, { passive: true });
        lb.addEventListener('touchend', e => {
            if (touchX === null) return;
            const dx = e.changedTouches[0].clientX - touchX;
            if (Math.abs(dx) > 50) show(dx < 0 ? idx + 1 : idx - 1, dx < 0 ? 1 : -1);
            touchX = null;
        });
    }

    // ---------- Map (loads only after click, for GDPR) ----------
    const mapBtn = $('#mapBtn');
    if (mapBtn) mapBtn.addEventListener('click', () => {
        const iframe = document.createElement('iframe');
        iframe.src = 'https://www.openstreetmap.org/export/embed.html?bbox=8.6150%2C50.0720%2C8.6600%2C50.0950&layer=mapnik&marker=50.0835%2C8.6375';
        iframe.title = 'OpenStreetMap';
        iframe.loading = 'lazy';
        iframe.referrerPolicy = 'no-referrer';
        const map = $('#map');
        map.replaceChildren(iframe);
    });

    // ---------- Footer year ----------
    const year = $('#year');
    if (year) year.textContent = new Date().getFullYear();

    // ---------- Scroll reveal ----------
    const reveals = $$('.reveal');
    if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        const io = new IntersectionObserver(entries => entries.forEach(en => {
            if (en.isIntersecting) { en.target.classList.add('visible'); io.unobserve(en.target); }
        }), { threshold: 0.15 });
        reveals.forEach(el => io.observe(el));
    } else {
        reveals.forEach(el => el.classList.add('visible'));
    }

    renderTheme();
    if (lang === 'en') translate(); else renderHours();
})();
