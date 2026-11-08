const root = document.documentElement;
const mouseAvailable = matchMedia('(any-hover: hover) and (any-pointer: fine)');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const interactive = 'a[href], button, summary, [role="button"], [role="tab"]';
const nativeCursor = 'input, textarea, [contenteditable], iframe';

async function initializeCursor() {
  const cursorDirectory = new URL('./assets/maplestory/ui/cursor/', import.meta.url);
  const states = {
    default: [{ file: 'default/0.png', origin: { x: 0, y: 3 } }],
    pointer: [
      { file: 'pointer/0.png', origin: { x: 3, y: 6 }, delay: 500 },
      { file: 'pointer/1.png', origin: { x: 4, y: 4 }, delay: 500 },
    ],
    pressed: [{ file: 'pressed/0.png', origin: { x: 4, y: 1 } }],
  };

  // Decode every frame before changing the pointer, so a missing asset leaves
  // the browser's cursor intact instead of blinking between loaded frames.
  await Promise.all(Object.values(states).flat().map(async (frame) => {
    const image = new Image();
    image.src = new URL(frame.file, cursorDirectory).href;
    await image.decode();
    frame.cursor = `url("${image.src}") ${frame.origin.x} ${frame.origin.y}, auto`;
  }));

  let state = null;
  let frameIndex = 0;
  let timer;

  function clearCursor() {
    clearTimeout(timer);
    state = null;
    root.removeAttribute('data-maple-cursor');
    root.style.removeProperty('--maple-cursor');
  }

  function drawFrame() {
    const frames = states[state];
    const frame = frames[frameIndex];
    root.style.setProperty('--maple-cursor', frame.cursor);
    root.setAttribute('data-maple-cursor', state);
    if (frames.length > 1 && !reducedMotion.matches) {
      timer = setTimeout(() => {
        frameIndex = (frameIndex + 1) % frames.length;
        drawFrame();
      }, frame.delay);
    }
  }

  function setState(nextState) {
    if (state === nextState) return;
    clearTimeout(timer);
    state = nextState;
    frameIndex = 0;
    drawFrame();
  }

  function updateCursor(event) {
    const target = event.target instanceof Element ? event.target : null;
    if (!mouseAvailable.matches || event.pointerType !== 'mouse' ||
        !target || target.closest(nativeCursor)) {
      clearCursor();
      return;
    }

    const control = target.closest(interactive);
    const clickable = control && !control.closest('[disabled], [aria-disabled="true"], [inert]');
    setState(event.buttons & 1 ? 'pressed' : clickable ? 'pointer' : 'default');
  }

  for (const event of ['pointerover', 'pointermove', 'pointerdown', 'pointerup']) {
    document.addEventListener(event, updateCursor, { passive: true });
  }
  document.addEventListener('pointerout', (event) => {
    if (!event.relatedTarget) clearCursor();
  });
  document.addEventListener('pointercancel', clearCursor);
  window.addEventListener('blur', clearCursor);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) clearCursor();
  });
  mouseAvailable.addEventListener('change', clearCursor);
  reducedMotion.addEventListener('change', () => {
    if (!state) return;
    clearTimeout(timer);
    frameIndex = 0;
    drawFrame();
  });
}

// Keep the native cursor if an image cannot be loaded.
initializeCursor().catch(() => {});
