/* Read-only DOM probe. Evaluate this function through a permitted browser adapter. */
(options = {}) => {
  const limit = options.limit || 100;
  const scanLimit = 5000;
  const path = (el) => {
    if (!(el instanceof Element)) return null;
    if (el.id) return '#' + CSS.escape(el.id);
    const parts = [];
    for (let node = el; node && parts.length < 7; node = node.parentElement) {
      if (node.id) { parts.unshift('#' + CSS.escape(node.id)); break; }
      const peers = node.parentElement ? [...node.parentElement.children].filter(n => n.tagName === node.tagName) : [node];
      parts.unshift(node.localName + (peers.length > 1 ? `:nth-of-type(${peers.indexOf(node) + 1})` : ''));
    }
    return parts.join(' > ');
  };
  const visible = el => {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility === 'visible' && r.width > 0 && r.height > 0;
  };
  const properties = ['display', 'position', 'width', 'max-width', 'height', 'padding', 'margin', 'gap',
    'grid-template-columns', 'grid-auto-flow', 'flex-direction', 'flex-wrap', 'flex-grow', 'align-items',
    'justify-content', 'overflow', 'z-index', 'isolation', 'color', 'background-color', 'background-image',
    'font-family', 'font-size', 'font-weight', 'line-height', 'letter-spacing', 'border', 'border-radius',
    'box-shadow', 'opacity', 'filter', 'backdrop-filter', 'mix-blend-mode', 'transform', 'transition',
    'animation-name', 'animation-duration', 'animation-iteration-count', 'outline', 'text-decoration'];
  const style = (el, pseudo = null) => {
    const s = getComputedStyle(el, pseudo);
    return Object.fromEntries(properties.concat(pseudo ? ['content'] : []).map(p => [p, s.getPropertyValue(p)]));
  };
  const candidates = new Set();
  const selectorErrors = [];
  for (const selector of (options.selectors?.length ? options.selectors : [
    'html,body,header,nav,main,footer,h1,h2,h3,section,article',
    '[class*="card"],[class*="hero"],p,button,a,input,select,textarea,[role="dialog"]'
  ])) {
    try {
      for (const el of document.querySelectorAll(selector)) {
        if (candidates.size >= limit) break;
        if (visible(el)) candidates.add(el);
      }
    } catch (error) { selectorErrors.push({selector, error: String(error)}); }
  }
  const elements = [...candidates].map(el => {
    const r = el.getBoundingClientRect();
    return {selector: path(el), tag: el.localName, parent: path(el.parentElement),
      child_tags: [...el.children].slice(0, 20).map(n => n.localName),
      text: (el.matches('input,textarea,select') ? '' : el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 180),
      role: el.getAttribute('role'), aria_expanded: el.getAttribute('aria-expanded'),
      bounds: {x: r.x, y: r.y, width: r.width, height: r.height},
      styles: style(el), before: style(el, '::before'), after: style(el, '::after')};
  });
  const rules = [], inaccessible = [], ruleLimit = 350;
  const walk = (list, source, conditions = [], prefix = '') => {
    for (let index = 0; index < list.length && rules.length < ruleLimit; index++) {
      const rule = list[index], locator = prefix + 'cssRules[' + index + ']';
      if (rule.selectorText) {
        const selector = rule.selectorText.replace(/::(before|after)/g, '');
        const matched = [...candidates].filter(el => { try { return el.matches(selector); } catch { return false; } }).map(path);
        if (matched.length) rules.push({source, locator,
          selector: rule.selectorText, declaration: rule.style.cssText.slice(0, 2400), conditions, matched});
      } else if (rule.cssRules) {
        let condition = null;
        if (rule.type === CSSRule.MEDIA_RULE) condition = {type: 'media', text: rule.conditionText, matches: matchMedia(rule.conditionText).matches};
        if (rule.type === CSSRule.SUPPORTS_RULE) condition = {type: 'supports', text: rule.conditionText, matches: CSS.supports(rule.conditionText)};
        walk(rule.cssRules, source, condition ? conditions.concat(condition) : conditions, locator + '.');
      }
    }
  };
  for (const [index, sheet] of [...document.styleSheets].entries()) {
    const source = sheet.href || location.href + '#inline-style-' + index;
    try { walk(sheet.cssRules, source); }
    catch (error) { inaccessible.push({source, reason: String(error)}); }
  }
  const variables = {};
  const rootStyle = getComputedStyle(document.documentElement);
  for (const rule of rules) {
    for (const match of rule.declaration.matchAll(/(--[\w-]+)\s*:/g)) {
      variables[match[1]] = rootStyle.getPropertyValue(match[1]).trim();
    }
  }
  const issues = [];
  const issue = (rule, severity, el, message, details = {}) =>
    issues.push({rule, severity, selector: el ? path(el) : 'html', message, ...details});
  const all = [...document.querySelectorAll('*')].slice(0, scanLimit);
  const shown = all.filter(visible);
  const name = el => {
    const labelled = (el.getAttribute('aria-labelledby') || '').split(/\s+/).filter(Boolean)
      .map(id => document.getElementById(id)?.textContent || '').join(' ').trim();
    const associated = [...(el.labels || [])].map(label => label.textContent).join(' ').trim();
    return el.getAttribute('aria-label')?.trim() || labelled || associated || el.getAttribute('title')?.trim() ||
      (el.matches('input[type=button],input[type=submit]') ? el.value : '') ||
      (el.matches('button,a,[role=button]') ? (el.textContent || '').trim() || el.querySelector('img[alt]')?.alt || el.querySelector('svg title')?.textContent : '');
  };
  if (document.documentElement.scrollWidth > innerWidth + 1)
    issue('page-overflow', 'error', null, 'Document is wider than the viewport.', {scroll_width: document.documentElement.scrollWidth, viewport_width: innerWidth});
  for (const el of shown) {
    if (el.matches('img') && !el.hasAttribute('alt')) issue('image-alt', 'error', el, 'Image has no alt attribute; decorative images need alt="".');
    if (el.matches('input:not([type=hidden]):not([type=submit]):not([type=button]):not([type=reset]),select,textarea') && !name(el))
      issue('control-label', 'error', el, 'No label found by the basic name heuristic.');
    if (el.matches('button,a[href],[role=button]')) {
      if (!name(el)) issue('interactive-name', 'error', el, 'No accessible name found by the basic heuristic.');
      const r = el.getBoundingClientRect();
      if ((r.width < 24 || r.height < 24) && !el.matches('p a,li a'))
        issue('small-target', 'warning', el, 'Target is smaller than 24 CSS pixels; review spacing and applicable exceptions.');
    }
  }
  const rgb = value => {
    const match = value.match(/^rgba?\(([^)]+)\)$/);
    if (!match) return null;
    const values = match[1].split(/[, /]+/).map(Number);
    return values.length === 3 || values[3] === 1 ? values.slice(0, 3) : null;
  };
  const luminance = color => color.map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)
    .reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
  let contrastChecked = 0, contrastSkipped = 0;
  for (const el of candidates) {
    if (![...el.childNodes].some(n => n.nodeType === Node.TEXT_NODE && n.textContent.trim())) continue;
    const s = getComputedStyle(el), foreground = rgb(s.color);
    let background = null, complex = false;
    for (let parent = el; parent; parent = parent.parentElement) {
      const ps = getComputedStyle(parent);
      if (ps.opacity !== '1' || ps.backgroundImage !== 'none' || ps.filter !== 'none' || ps.mixBlendMode !== 'normal') complex = true;
      for (const pseudo of ['::before', '::after']) {
        const p = getComputedStyle(parent, pseudo);
        if (p.content !== 'none' && p.content !== 'normal') complex = true;
      }
      if (!background) background = rgb(ps.backgroundColor);
    }
    if (!foreground || !background || complex) { contrastSkipped++; continue; }
    const a = luminance(foreground), b = luminance(background), ratio = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
    const large = parseFloat(s.fontSize) >= 24 || (parseFloat(s.fontSize) >= 18.667 && parseInt(s.fontWeight) >= 700);
    contrastChecked++;
    if (ratio < (large ? 3 : 4.5)) issue('text-contrast', 'warning', el, 'Simple solid-background contrast is below the text threshold; verify the rendered context.', {ratio: +ratio.toFixed(2)});
  }
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
    for (const el of shown) {
      const s = getComputedStyle(el);
      if (s.animationName !== 'none' && s.animationIterationCount.includes('infinite'))
        issue('reduced-motion-review', 'warning', el, 'Infinite animation remains under reduced motion; review whether an appropriate alternative exists.');
    }
  }
  return {url: location.href, title: document.title,
    viewport: {width: innerWidth, height: innerHeight},
    reduced_motion: matchMedia('(prefers-reduced-motion: reduce)').matches,
    elements, rules, root_variables: variables, inaccessible_stylesheets: inaccessible,
    scripts: [...document.scripts].map(s => ({url: s.src || null, type: s.type || 'classic', inline: !s.src})),
    fonts: {status: document.fonts.status, faces: [...document.fonts].slice(0, 50).map(f => ({family: f.family, weight: f.weight, status: f.status}))},
    issues, selector_errors: selectorErrors,
    coverage: {sampled_elements: elements.length, sample_limit: limit,
      scanned_elements: all.length, dom_scan_truncated: document.querySelectorAll('*').length > scanLimit,
      matched_rules: rules.length, rule_limit_reached: rules.length >= ruleLimit,
      contrast_checked: contrastChecked, contrast_skipped: contrastSkipped,
      cross_origin_frames_not_inspected: [...document.querySelectorAll('iframe')].map(f => f.src)}};
}
