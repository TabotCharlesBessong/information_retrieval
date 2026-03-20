from __future__ import annotations


def render_ui_html() -> str:
  return """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>IR Search Console</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    :root {
      --bg: #f5efe1;
      --paper: #fffaf1;
      --ink: #1f1f1f;
      --muted: #5f5b53;
      --accent: #0f766e;
      --accent-2: #f97316;
      --line: #e2d7c0;
      --card-shadow: 0 10px 30px rgba(69, 40, 7, 0.1);
      --radius: 14px;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: 'IBM Plex Sans', sans-serif;
      color: var(--ink);
      background:
        radial-gradient(900px 400px at 8% -5%, #ffd8a8 0%, transparent 70%),
        radial-gradient(800px 350px at 98% 8%, #b6f0ea 0%, transparent 72%),
        linear-gradient(180deg, #f7f2e8 0%, #f5efe1 100%);
      min-height: 100vh;
    }

    .shell {
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 16px 40px;
    }

    .hero {
      background: linear-gradient(135deg, #fffaf1 0%, #fff3dd 100%);
      border: 1px solid var(--line);
      border-radius: calc(var(--radius) + 6px);
      box-shadow: var(--card-shadow);
      padding: 20px;
      margin-bottom: 18px;
      animation: rise 420ms ease-out;
    }

    h1 {
      margin: 0 0 8px;
      font-family: 'Space Grotesk', sans-serif;
      font-size: clamp(1.6rem, 2.2vw, 2.4rem);
      line-height: 1.05;
      letter-spacing: -0.02em;
    }

    .sub {
      margin: 0;
      color: var(--muted);
      font-size: 0.98rem;
    }

    .layout {
      display: grid;
      grid-template-columns: 320px minmax(0, 1fr);
      gap: 16px;
    }

    .panel {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--card-shadow);
      padding: 14px;
      animation: rise 480ms ease-out;
    }

    .panel h2 {
      margin: 0 0 12px;
      font-family: 'Space Grotesk', sans-serif;
      font-size: 1.05rem;
    }

    .grid {
      display: grid;
      gap: 10px;
    }

    label {
      font-size: 0.8rem;
      color: var(--muted);
      display: block;
      margin-bottom: 4px;
    }

    input, select {
      width: 100%;
      border: 1px solid #d4c7ad;
      background: #fffdf7;
      border-radius: 9px;
      padding: 9px 10px;
      font-size: 0.93rem;
      color: var(--ink);
    }

    .row2 {
      display: grid;
      gap: 8px;
      grid-template-columns: 1fr 1fr;
    }

    .row3 {
      display: grid;
      gap: 8px;
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .btn {
      appearance: none;
      border: none;
      border-radius: 999px;
      padding: 10px 14px;
      font-weight: 600;
      cursor: pointer;
      transition: transform .14s ease, filter .14s ease;
    }

    .btn:active { transform: translateY(1px); }

    .btn-main {
      width: 100%;
      background: linear-gradient(90deg, var(--accent) 0%, #0c948a 100%);
      color: #fff;
      margin-top: 2px;
    }

    .btn-main:hover { filter: brightness(1.05); }

    .results-header {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }

    .summary {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }

    .pill {
      border: 1px solid #d8ccb4;
      background: #fffaf1;
      padding: 5px 9px;
      border-radius: 999px;
      font-size: 0.78rem;
      color: #4e473c;
    }

    .card {
      border: 1px solid #e4d8c2;
      border-radius: 12px;
      background: #fffefa;
      padding: 12px;
      margin-bottom: 10px;
      animation: stagger .32s ease both;
    }

    .card h3 {
      margin: 0 0 6px;
      font-size: 1rem;
      line-height: 1.2;
    }

    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      font-size: 0.78rem;
      color: var(--muted);
      margin: 0 0 7px;
    }

    .snippet {
      margin: 0 0 9px;
      color: #2f2d28;
      line-height: 1.45;
      font-size: 0.92rem;
    }

    .link {
      color: #0b6a63;
      font-size: 0.84rem;
      text-decoration: none;
      word-break: break-word;
    }

    .small-btn {
      background: linear-gradient(90deg, #f97316 0%, #fb923c 100%);
      color: #fff;
      padding: 7px 11px;
      font-size: 0.8rem;
    }

    .small-btn:hover { filter: brightness(1.05); }

    .recommendation {
      border-left: 3px solid #14b8a6;
      padding-left: 8px;
      margin-bottom: 10px;
    }

    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }

    .pager {
      display: flex;
      gap: 6px;
      align-items: center;
    }

    .btn-ghost {
      border: 1px solid #d9ccb5;
      background: #fff9ef;
      color: #3e392f;
      padding: 7px 11px;
      font-size: 0.82rem;
    }

    .btn-ghost:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .status {
      font-size: 0.8rem;
      color: #4f4a40;
    }

    .empty {
      color: var(--muted);
      font-style: italic;
      padding: 10px 0;
    }

    .error {
      color: #a11111;
      font-weight: 500;
      margin-top: 8px;
    }

    @keyframes rise {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes stagger {
      from { opacity: 0; transform: translateY(5px) scale(0.995); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }

    @media (max-width: 980px) {
      .layout { grid-template-columns: 1fr; }
      .row3 { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main class=\"shell\">
    <section class=\"hero\">
      <h1>Phase F Search Studio</h1>
      <p class=\"sub\">Filter results, apply profile-aware boosts, and generate content-based recommendations from one UI.</p>
    </section>

    <section class=\"layout\">
      <aside class=\"panel\">
        <h2>Search Controls</h2>
        <form id=\"searchForm\" class=\"grid\">
          <div>
            <label for=\"q\">Query</label>
            <input id=\"q\" value=\"african fintech funding\" list=\"querySuggestions\" required />
            <datalist id=\"querySuggestions\"></datalist>
          </div>

          <div class=\"row2\">
            <div>
              <label for=\"mode\">Mode</label>
              <select id=\"mode\">
                <option value=\"bm25\">bm25</option>
                <option value=\"boolean\">boolean</option>
                <option value=\"probabilistic\">probabilistic</option>
              </select>
            </div>
            <div>
              <label for=\"size\">Size</label>
              <input id=\"size\" type=\"number\" min=\"1\" max=\"50\" value=\"10\" />
            </div>
          </div>

          <div>
            <label for=\"phrase\">Phrase match (optional)</label>
            <input id=\"phrase\" placeholder=\"exact phrase to enforce\" />
          </div>

          <div class=\"row2\">
            <div>
              <label for=\"source\">Only include source(s) (comma-separated)</label>
              <input id=\"source\" placeholder=\"TechCabal, Techpoint\" />
            </div>
            <div>
              <label for=\"recSize\">Recommendation size</label>
              <input id=\"recSize\" type=\"number\" min=\"1\" max=\"30\" value=\"5\" />
            </div>
          </div>

          <div class=\"row2\">
            <div>
              <label for=\"publishedFrom\">Published from</label>
              <input id=\"publishedFrom\" type=\"date\" />
            </div>
            <div>
              <label for=\"publishedTo\">Published to</label>
              <input id=\"publishedTo\" type=\"date\" />
            </div>
          </div>

          <div>
            <label for=\"mustInclude\">Must include (comma-separated)</label>
            <input id=\"mustInclude\" placeholder=\"funding, payments\" />
          </div>

          <div>
            <label for=\"excludeTerms\">Exclude terms (comma-separated)</label>
            <input id=\"excludeTerms\" placeholder=\"rumor, gossip\" />
          </div>

          <div>
            <label for=\"excludeSource\">Exclude source (comma-separated)</label>
            <input id=\"excludeSource\" placeholder=\"some source\" />
          </div>

          <div>
            <label for=\"interests\">Profile interests (comma-separated)</label>
            <input id=\"interests\" placeholder=\"fintech, payments\" />
          </div>

          <div>
            <label for=\"preferredSources\">Preferred sources (comma-separated)</label>
            <input id=\"preferredSources\" placeholder=\"TechCabal, Techpoint\" />
          </div>

          <div>
            <label for=\"blockedProfileSources\">Profile excluded sources (comma-separated)</label>
            <input id=\"blockedProfileSources\" placeholder=\"blocked source\" />
          </div>

          <button class=\"btn btn-main\" type=\"submit\">Run Search</button>
          <p id=\"formError\" class=\"error\"></p>
        </form>
      </aside>

      <section class=\"panel\">
        <div class=\"results-header\">
          <h2 style=\"margin: 0\">Results</h2>
          <span id=\"resultMeta\" class=\"pill\">No search yet</span>
        </div>

        <div id=\"summary\" class=\"summary\"></div>
        <div id=\"facets\" class=\"summary\"></div>

        <div class=\"toolbar\">
          <div id=\"status\" class=\"status\">Ready</div>
          <div class=\"pager\">
            <button id=\"prevPage\" type=\"button\" class=\"btn btn-ghost\" disabled>Prev</button>
            <span id=\"pageMeta\" class=\"pill\">Page 1</span>
            <button id=\"nextPage\" type=\"button\" class=\"btn btn-ghost\" disabled>Next</button>
          </div>
        </div>

        <div id=\"results\"><p class=\"empty\">Submit a query to see results.</p></div>

        <hr style=\"border: none; border-top: 1px solid #e7dcc8; margin: 16px 0;\" />

        <h2>Recommendations</h2>
        <p class=\"sub\" style=\"margin-bottom: 10px\">Click \"Find related\" on any result to query <code>/recommendations</code>.</p>
        <div id=\"recommendations\"><p class=\"empty\">No recommendations yet.</p></div>
      </section>
    </section>
  </main>

  <script>
    const form = document.getElementById('searchForm');
    const resultMeta = document.getElementById('resultMeta');
    const summary = document.getElementById('summary');
    const facets = document.getElementById('facets');
    const results = document.getElementById('results');
    const recommendations = document.getElementById('recommendations');
    const formError = document.getElementById('formError');
    const pageMeta = document.getElementById('pageMeta');
    const prevPage = document.getElementById('prevPage');
    const nextPage = document.getElementById('nextPage');
    const status = document.getElementById('status');
    const querySuggestions = document.getElementById('querySuggestions');

    let currentPage = 1;
    let currentTotal = 0;
    let lastParams = null;

    function setStatus(text) {
      status.textContent = text;
    }

    function safeNum(value, fallback) {
      const n = Number(value);
      return Number.isFinite(n) ? n : fallback;
    }

    function clearSuggestions() {
      querySuggestions.innerHTML = '';
    }

    function updatePagination(total, page, size) {
      currentTotal = total;
      currentPage = page;
      const totalPages = Math.max(1, Math.ceil(total / size));
      pageMeta.textContent = `Page ${page} / ${totalPages}`;
      prevPage.disabled = page <= 1;
      nextPage.disabled = page >= totalPages || total === 0;
    }

    function appendText(el, value, fallback = '') {
      el.textContent = value || fallback;
    }

    function parseCsv(value) {
      if (!value || !value.trim()) return [];
      return value.split(',').map(v => v.trim()).filter(Boolean);
    }

    function appendList(params, key, values) {
      values.forEach(v => params.append(key, v));
    }

    function renderPills(container, pairs) {
      container.innerHTML = '';
      pairs.forEach(([label, value]) => {
        const el = document.createElement('span');
        el.className = 'pill';
        el.textContent = `${label}: ${value}`;
        container.appendChild(el);
      });
    }

    function renderRecommendations(items) {
      if (!items || !items.length) {
        recommendations.innerHTML = '<p class=\"empty\">No related documents found.</p>';
        return;
      }

      recommendations.innerHTML = '';
      items.forEach(item => {
        const block = document.createElement('div');
        block.className = 'recommendation';

        const strong = document.createElement('strong');
        appendText(strong, item.title, '(untitled)');

        const meta = document.createElement('span');
        meta.className = 'meta';
        meta.style.margin = '4px 0';
        meta.textContent = `source: ${item.source || 'unknown source'} | score: ${safeNum(item.score, 0).toFixed(4)}`;

        const reason = document.createElement('div');
        reason.style.fontSize = '0.86rem';
        reason.style.color = '#3f3b34';
        appendText(reason, item.reason, '');

        block.appendChild(strong);
        block.appendChild(document.createElement('br'));
        block.appendChild(meta);
        block.appendChild(reason);
        recommendations.appendChild(block);
      });
    }

    async function fetchRecommendations(seedDocId) {
      setStatus('Loading recommendations...');
      const excluded = parseCsv(document.getElementById('blockedProfileSources').value);
      const recSizeRaw = document.getElementById('recSize').value || '5';
      const recSize = String(Math.max(1, Math.min(30, safeNum(recSizeRaw, 5))));
      const params = new URLSearchParams({ seed_doc_id: seedDocId, size: recSize });
      appendList(params, 'profile_excluded_sources', excluded);

      const res = await fetch(`/recommendations?${params.toString()}`);
      if (!res.ok) {
        recommendations.innerHTML = `<p class=\"error\">Recommendation request failed (${res.status}).</p>`;
        setStatus(`Recommendation request failed (${res.status})`);
        return;
      }

      const data = await res.json();
      renderRecommendations(data.items || []);
      setStatus('Recommendations loaded');
    }

    function renderResults(items) {
      if (!items || !items.length) {
        results.innerHTML = '<p class=\"empty\">No documents matched your filters.</p>';
        return;
      }

      results.innerHTML = '';
      items.forEach((item, idx) => {
        const card = document.createElement('article');
        card.className = 'card';
        card.style.animationDelay = `${Math.min(idx * 30, 240)}ms`;

        const title = document.createElement('h3');
        appendText(title, item.title, '(untitled)');

        const meta = document.createElement('p');
        meta.className = 'meta';
        meta.textContent = `${item.source || 'unknown source'} | ${item.published_at || '-'} | score ${safeNum(item.score, 0).toFixed(4)}`;

        const snippet = document.createElement('p');
        snippet.className = 'snippet';
        appendText(snippet, item.snippet, '');

        const link = document.createElement('a');
        link.className = 'link';
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        const urlValue = item.url || '#';
        link.href = urlValue;
        appendText(link, item.url, '');

        const actionWrap = document.createElement('div');
        actionWrap.style.marginTop = '9px';

        const btn = document.createElement('button');
        btn.className = 'btn small-btn';
        btn.type = 'button';
        btn.textContent = 'Find related';
        btn.addEventListener('click', () => fetchRecommendations(String(item.id || '')));
        actionWrap.appendChild(btn);

        card.appendChild(title);
        card.appendChild(meta);
        card.appendChild(snippet);
        card.appendChild(link);
        card.appendChild(actionWrap);
        results.appendChild(card);
      });
    }

    function getBaseParams() {
      const q = document.getElementById('q').value.trim();
      const params = new URLSearchParams({
        q,
        mode: document.getElementById('mode').value,
        size: document.getElementById('size').value || '10',
      });

      const phrase = document.getElementById('phrase').value.trim();
      const publishedFrom = document.getElementById('publishedFrom').value;
      const publishedTo = document.getElementById('publishedTo').value;

      if (phrase) params.set('phrase', phrase);
      if (publishedFrom) params.set('published_from', publishedFrom);
      if (publishedTo) params.set('published_to', publishedTo);

      appendList(params, 'source', parseCsv(document.getElementById('source').value));
      appendList(params, 'must_include', parseCsv(document.getElementById('mustInclude').value));
      appendList(params, 'exclude_terms', parseCsv(document.getElementById('excludeTerms').value));
      appendList(params, 'exclude_source', parseCsv(document.getElementById('excludeSource').value));
      appendList(params, 'profile_interests', parseCsv(document.getElementById('interests').value));
      appendList(params, 'profile_preferred_sources', parseCsv(document.getElementById('preferredSources').value));
      appendList(params, 'profile_excluded_sources', parseCsv(document.getElementById('blockedProfileSources').value));

      return params;
    }

    async function runSearch(page) {
      const q = document.getElementById('q').value.trim();
      if (!q) {
        formError.textContent = 'Please enter a query.';
        return;
      }

      const params = getBaseParams();
      params.set('page', String(page));
      lastParams = new URLSearchParams(params);
      setStatus('Searching...');

      const res = await fetch(`/search?${params.toString()}`);
      if (!res.ok) {
        resultMeta.textContent = `Search failed (${res.status})`;
        results.innerHTML = '<p class=\"error\">Search request failed.</p>';
        setStatus(`Search failed (${res.status})`);
        updatePagination(0, 1, safeNum(document.getElementById('size').value, 10));
        return;
      }

      const data = await res.json();
      resultMeta.textContent = `total ${data.total} | page ${data.page} | mode ${data.mode}`;
      renderPills(summary, [
        ['input', data.filtering_summary?.input_count ?? 0],
        ['kept', data.filtering_summary?.kept_count ?? 0],
        ['drop source', data.filtering_summary?.dropped_source ?? 0],
        ['drop terms', data.filtering_summary?.dropped_excluded_terms ?? 0],
        ['drop must', data.filtering_summary?.dropped_missing_must_terms ?? 0],
      ]);

      const facetPairs = (data.facets?.sources || []).slice(0, 8).map(f => [f.value, f.count]);
      renderPills(facets, facetPairs);
      renderResults(data.items || []);
      recommendations.innerHTML = '<p class=\"empty\">Select a result and click Find related.</p>';

      updatePagination(
        safeNum(data.total, 0),
        safeNum(data.page, 1),
        Math.max(1, safeNum(data.size, 10)),
      );
      setStatus('Search complete');
    }

    async function refreshSuggestions() {
      const q = document.getElementById('q').value.trim();
      if (q.length < 2) {
        clearSuggestions();
        return;
      }

      const res = await fetch(`/search/suggest?q=${encodeURIComponent(q)}&limit=6`);
      if (!res.ok) {
        clearSuggestions();
        return;
      }

      const data = await res.json();
      const suggestions = data.suggestions || [];
      clearSuggestions();
      suggestions.forEach(value => {
        const option = document.createElement('option');
        option.value = String(value || '');
        querySuggestions.appendChild(option);
      });
    }

    form.addEventListener('submit', async (evt) => {
      evt.preventDefault();
      formError.textContent = '';
      await runSearch(1);
    });

    prevPage.addEventListener('click', async () => {
      if (!lastParams || currentPage <= 1) return;
      await runSearch(currentPage - 1);
    });

    nextPage.addEventListener('click', async () => {
      if (!lastParams) return;
      const size = Math.max(1, safeNum(document.getElementById('size').value, 10));
      const totalPages = Math.max(1, Math.ceil(currentTotal / size));
      if (currentPage >= totalPages) return;
      await runSearch(currentPage + 1);
    });

    let suggestTimer = null;
    document.getElementById('q').addEventListener('input', () => {
      if (suggestTimer) {
        clearTimeout(suggestTimer);
      }
      suggestTimer = setTimeout(() => {
        refreshSuggestions().catch(() => clearSuggestions());
      }, 220);
    });
  </script>
</body>
</html>
"""
