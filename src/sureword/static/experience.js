/* Progressive enhancement: all reading content is present before this script runs. */
(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const stageTabs = [...document.querySelectorAll('.stage-controls [role=tab]')];
  const panels = [...document.querySelectorAll('.stage-panel')];
  function selectStage(index) {
    stageTabs.forEach((tab, i) => {
      tab.setAttribute('aria-selected', String(i === index));
      tab.tabIndex = i === index ? 0 : -1;
      panels[i].hidden = i !== index;
      panels[i].setAttribute('role', 'tabpanel');
    });
  }
  document.querySelector('.stage-controls').hidden = false;
  stageTabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectStage(index));
    tab.addEventListener('keydown', event => {
      let next = index;
      if (event.key === 'ArrowRight') next = (index + 1) % stageTabs.length;
      else if (event.key === 'ArrowLeft') next = (index + stageTabs.length - 1) % stageTabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = stageTabs.length - 1;
      else return;
      event.preventDefault(); selectStage(next); stageTabs[next].focus();
    });
  });
  selectStage(0);
  const workspaceTabs = [...document.querySelectorAll('.nav-tabs [role=tab]')];
  workspaceTabs.forEach((tab, index) => {
    tab.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? 1 : 1 - index;
      workspaceTabs[next].click(); workspaceTabs[next].focus();
    });
  });
  if ('IntersectionObserver' in window) {
    const reveals = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      if (!reduced.matches) entry.target.classList.add('revealed');
      reveals.unobserve(entry.target);
    }), { threshold: .15 });
    document.querySelectorAll('[data-reveal]').forEach(el => reveals.observe(el));
  }
  const header = document.querySelector('.app-header');
  addEventListener('scroll', () => header.classList.toggle('scrolled', scrollY > 8), { passive: true });

  const canvas = document.getElementById('particle-field');
  const ctx = canvas.getContext('2d');
  const pause = document.getElementById('particle-pause');
  const mode = document.getElementById('particle-mode');
  if (!ctx) { pause.hidden = true; mode.hidden = true; return; }
  let width = 0, height = 0, frame = 0, last = 0, phase = 0;
  let paused = false, orbital = false, visible = true;
  const pointer = { x: -1000, y: -1000 };
  const particles = Array.from({ length: matchMedia('(max-width:767px)').matches ? 36 : 80 }, (_, i) => ({
    x: 0, y: 0, vx: 0, vy: 0, home: i / 80 * Math.PI * 2,
    depth: .4 + Math.random() * .8, size: 1.1 + Math.random() * 2.2,
    rotation: Math.random() * Math.PI, spin: (Math.random() - .5) * .02,
    seed: Math.random() * Math.PI * 2, shape: i % 4,
  }));
  // Cached shape sprites; the frame loop reuses the same objects and images.
  const sprites = Array.from({ length: 4 }, (_, i) => {
    const sprite = document.createElement('canvas'); sprite.width = sprite.height = 16;
    const paint = sprite.getContext('2d'); paint.fillStyle = i % 2 ? '#73b8db' : '#1684ba';
    paint.beginPath();
    if (i === 0) paint.arc(8, 8, 4, 0, Math.PI * 2);
    else if (i === 1) paint.roundRect(4, 4, 8, 8, 2);
    else if (i === 2) { paint.moveTo(8, 3); paint.lineTo(13, 12); paint.lineTo(3, 12); paint.closePath(); }
    else paint.roundRect(2, 6, 12, 4, 2);
    paint.fill(); return sprite;
  });
  function resize() {
    const box = canvas.getBoundingClientRect(); width = box.width; height = box.height;
    const dpr = Math.min(devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    particles.forEach(p => { p.x = width * (.1 + Math.random() * .8); p.y = height * (.1 + Math.random() * .8); });
    draw(0);
  }
  function draw(dt) {
    ctx.clearRect(0, 0, width, height);
    particles.forEach((p, i) => {
      if (orbital) {
        const angle = i / particles.length * Math.PI * 2 + phase * .15;
        const tx = width / 2 + Math.cos(angle) * width * .39;
        const ty = height / 2 + Math.sin(angle) * height * .36;
        if (dt === 0 && reduced.matches) { p.x = tx; p.y = ty; }
        else { p.vx += (tx - p.x) * .006 * dt; p.vy += (ty - p.y) * .006 * dt; }
      } else {
        p.vx += Math.sin(phase + p.seed) * .018 * dt;
        p.vy += (-.065 + Math.cos(phase * .6 + p.seed) * .025) * dt;
      }
      const dx = p.x - pointer.x, dy = p.y - pointer.y, dist = Math.hypot(dx, dy);
      if (!reduced.matches && dist < 100 && dist > 1) {
        const force = (1 - dist / 100) * .35 * dt;
        p.vx += dx / dist * force; p.vy += dy / dist * force;
      }
      p.vx = Math.max(-2, Math.min(2, p.vx * Math.pow(.95, dt)));
      p.vy = Math.max(-2, Math.min(2, p.vy * Math.pow(.95, dt)));
      p.x += p.vx * dt; p.y += p.vy * dt; p.rotation += p.spin * dt;
      if (p.x < 0) p.x = width; if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height; if (p.y > height) p.y = 0;
      ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.rotation);
      ctx.globalAlpha = .25 + p.depth * .4;
      const size = p.size * p.depth * 3;
      ctx.drawImage(sprites[p.shape], -size / 2, -size / 2, size, size); ctx.restore();
    });
  }
  function tick(now) {
    const dt = Math.min((now - last) / 16.667 || 1, 2); last = now; phase += dt * .008;
    draw(dt); frame = requestAnimationFrame(tick);
  }
  function sync() {
    cancelAnimationFrame(frame); last = 0;
    const stopped = paused || reduced.matches;
    pause.textContent = stopped ? 'Resume motion' : 'Pause motion';
    pause.setAttribute('aria-pressed', String(stopped));
    pause.disabled = reduced.matches;
    if (!stopped && visible && !document.hidden && !navigator.connection?.saveData) frame = requestAnimationFrame(tick);
    else draw(0);
  }
  pause.addEventListener('click', () => { paused = !paused; sync(); });
  mode.addEventListener('click', () => { orbital = !orbital; mode.setAttribute('aria-pressed', String(orbital)); sync(); });
  canvas.parentElement.addEventListener('pointermove', event => {
    if (event.pointerType === 'touch') return;
    const box = canvas.getBoundingClientRect(); pointer.x = event.clientX - box.left; pointer.y = event.clientY - box.top;
  }, { passive: true });
  canvas.parentElement.addEventListener('pointerleave', () => { pointer.x = pointer.y = -1000; }, { passive: true });
  new ResizeObserver(resize).observe(canvas.parentElement);
  new IntersectionObserver(entries => { visible = entries[0].isIntersecting; sync(); }).observe(canvas);
  reduced.addEventListener('change', sync);
  document.addEventListener('visibilitychange', sync);
  addEventListener('pagehide', () => cancelAnimationFrame(frame));
  resize(); sync();
})();
