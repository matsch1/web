/* No provider request is made until explicit map activation or comment proximity. */
(() => {
  'use strict';
  const giscusAttributes = ['repo', 'repo-id', 'category', 'category-id', 'mapping',
    'strict', 'reactions-enabled', 'emit-metadata', 'input-position', 'theme', 'lang'];

  function komootURL(value) {
    try {
      const url = new URL(value);
      if (url.protocol !== 'https:' || url.username || url.password || url.port ||
          !/^(www\.)?komoot\.(com|de)$/.test(url.hostname) ||
          !/^\/(?:[a-z]{2}-[a-z]{2}\/)?tour\/\d+\/embed$/.test(url.pathname) || url.hash) return null;
      return url;
    } catch (_) { return null; }
  }

  function initialize() {
    document.querySelectorAll('[data-deferred-embed]').forEach((embed) => {
      if (embed.dataset.initialized) return;
      embed.dataset.initialized = 'true';
      const button = embed.querySelector('[data-embed-load]');
      const status = embed.querySelector('[data-embed-status]');
      const target = embed.querySelector('[data-embed-target]');
      let state = 'idle';
      let observer;
      let timeout;
      button.hidden = false;

      function activate() {
        if (state !== 'idle') return;
        const isMap = embed.dataset.deferredEmbed === 'komoot';
        if (isMap && !komootURL(embed.dataset.src)) {
          status.textContent = embed.dataset.error;
          return;
        }
        state = 'loading';
        button.disabled = true;
        status.textContent = embed.dataset.loading || '';
        if (observer) observer.unobserve(embed);
        const node = document.createElement(isMap ? 'iframe' : 'script');
        let settled = false;
        function fail() {
          if (settled) return;
          settled = true;
          clearTimeout(timeout);
          node.remove();
          state = 'idle';
          button.disabled = false;
          button.hidden = false;
          button.textContent = embed.dataset.retry || button.textContent;
          status.textContent = embed.dataset.error;
        }
        node.onerror = fail;
        node.onload = () => {
          if (settled) return;
          settled = true;
          clearTimeout(timeout);
          state = 'loaded';
          button.hidden = true;
          status.textContent = '';
        };
        if (isMap) {
          node.src = embed.dataset.src; // Original share token/query, not reconstructed.
          node.width = '100%';
          node.height = /^[1-9][0-9]{0,4}$/.test(embed.dataset.height) ? embed.dataset.height : '700';
          node.title = embed.dataset.title;
          node.setAttribute('referrerpolicy', 'no-referrer');
          // Native buttons provide Enter/Space activation, without duplicate key handlers.
        } else {
          node.src = 'https://giscus.app/client.js';
          giscusAttributes.forEach((name) => {
            const key = name.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
            if (embed.dataset[key] !== undefined) node.setAttribute('data-' + name, embed.dataset[key]);
          });
          node.crossOrigin = 'anonymous';
          node.async = true;
        }
        timeout = setTimeout(fail, 20000);
        target.appendChild(node);
      }

      button.addEventListener('click', activate);
      if (embed.dataset.deferredEmbed === 'giscus' && typeof IntersectionObserver !== 'undefined') {
        observer = new IntersectionObserver((entries) => {
          if (entries.some((entry) => entry.target === embed && entry.isIntersecting)) activate();
        }, { rootMargin: '200px 0px' });
        observer.observe(embed);
      }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, { once: true });
  else initialize();
})();
