/* Observation helpers for explicitly supplied interaction scenarios. */
(selectors) => {
  const locate = el => el instanceof Element ? (el.id ? '#' + CSS.escape(el.id) : el.localName) : 'document';
  const properties = ['display', 'visibility', 'opacity', 'position', 'transform', 'background-color',
    'background-image', 'color', 'border', 'border-radius', 'box-shadow', 'filter', 'backdrop-filter',
    'grid-template-columns', 'height', 'width', 'overflow', 'animation-name', 'transition', 'outline'];
  const attributes = el => Object.fromEntries([...el.attributes]
    .filter(a => /^(class|hidden|open|disabled|role|aria-[\w-]+|data-state|data-active)$/.test(a.name))
    .map(a => [a.name, a.value.slice(0, 500)]));
  const styles = (el, pseudo = null) => {
    const computed = getComputedStyle(el, pseudo);
    return Object.fromEntries(properties.concat(pseudo ? ['content'] : []).map(p => [p, computed.getPropertyValue(p)]));
  };
  let observer = null, events = [], mutations = [], truncated = false;
  const eventTypes = ['click', 'keydown', 'focusin', 'pointerover', 'scroll'];
  const listener = event => {
    if (events.length >= 100) { truncated = true; return; }
    events.push({type: event.type, target: locate(event.target), key: event.type === 'keydown' ? event.key : null});
  };
  const stop = () => {
    observer?.disconnect(); observer = null;
    for (const type of eventTypes) document.removeEventListener(type, listener, true);
  };
  return {
    snapshot() {
      const elements = [];
      for (const selector of selectors) {
        const nodes = [...document.querySelectorAll(selector)];
        if (!nodes.length) elements.push({selector, index: 0, exists: false});
        for (const [index, el] of nodes.slice(0, 8).entries()) {
          if (elements.length >= 120) break;
          const rect = el.getBoundingClientRect(), s = getComputedStyle(el);
          elements.push({selector, index, exists: true, attributes: attributes(el),
            visible: s.display !== 'none' && s.visibility === 'visible' && rect.width > 0 && rect.height > 0,
            text: el.matches('input,textarea,select') ? '' : (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 180),
            bounds: {x: rect.x, y: rect.y, width: rect.width, height: rect.height},
            styles: styles(el), before: styles(el, '::before'), after: styles(el, '::after'),
            focused: document.activeElement === el});
        }
      }
      return {elements, active_element: locate(document.activeElement), scroll: {x: scrollX, y: scrollY}};
    },
    start() {
      stop(); events = []; mutations = []; truncated = false;
      observer = new MutationObserver(records => {
        for (const record of records) {
          if (mutations.length >= 100) { truncated = true; break; }
          if (record.type === 'attributes' && !/^(class|hidden|open|disabled|style|aria-[\w-]+|data-state|data-active)$/.test(record.attributeName)) continue;
          mutations.push({type: record.type, target: locate(record.target), attribute: record.attributeName,
            old_value: record.type === 'attributes' ? record.oldValue?.slice(0, 500) : null,
            new_value: record.type === 'attributes' ? record.target.getAttribute(record.attributeName)?.slice(0, 500) : null,
            added_nodes: record.addedNodes.length, removed_nodes: record.removedNodes.length});
        }
      });
      observer.observe(document.documentElement, {attributes: true, attributeOldValue: true, childList: true, characterData: true, subtree: true});
      for (const type of eventTypes) document.addEventListener(type, listener, {capture: true, passive: true});
    },
    finish() { stop(); return {events, mutations, truncated}; },
    dispose: stop
  };
}
