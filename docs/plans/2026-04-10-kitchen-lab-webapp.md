# Kitchen Lab Web App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page web app to browse recipes and generate shopping checklists, hosted on GitHub Pages.

**Architecture:** Single `index.html` with vanilla JS and Tailwind CDN. Recipes stored as markdown with YAML frontmatter in `recipes/`. An index file `recipes.json` provides metadata for the list view. Markdown fetched from GitHub raw URLs, parsed client-side with marked.js.

**Tech Stack:** HTML, vanilla JavaScript, Tailwind CSS (CDN), marked.js (CDN), Material Symbols (CDN), Space Grotesk + Newsreader (Google Fonts)

**Spec:** `docs/specs/2026-04-10-kitchen-lab-webapp-design.md`

---

### Task 1: Recipe Data Prep

Add YAML frontmatter to existing recipe markdown files and create `recipes.json` index.

**Files:**
- Modify: `recipes/gyros.md` (add frontmatter)
- Modify: `recipes/taco-beef-bowl.md` (add frontmatter)
- Modify: `recipes/taco-beef-bowl-classic.md` (add frontmatter)
- Create: `recipes.json`

- [ ] **Step 1: Add frontmatter to `recipes/gyros.md`**

Add this block at the very top of the file (before the `# Gyros` heading):

```markdown
---
title: Gyros / Shawarma Meal Prep
time: 25
tags: [meal-prep, high-protein]
description: roasted veg, rice, tzatziki
---
```

- [ ] **Step 2: Add frontmatter to `recipes/taco-beef-bowl.md`**

```markdown
---
title: Taco Beef Bowl
time: 30
tags: [bowls, low-cal]
description: sweet potato, goat cheese, hot honey
---
```

- [ ] **Step 3: Add frontmatter to `recipes/taco-beef-bowl-classic.md`**

```markdown
---
title: Taco Beef Bowl Classic
time: 20
tags: [bowls, meal-prep, high-protein]
description: black beans, corn, avocado, crema
---
```

- [ ] **Step 4: Create `recipes.json`**

```json
[
  {
    "slug": "gyros",
    "title": "Gyros / Shawarma Meal Prep",
    "time": 25,
    "tags": ["meal-prep", "high-protein"],
    "description": "roasted veg, rice, tzatziki"
  },
  {
    "slug": "taco-beef-bowl",
    "title": "Taco Beef Bowl",
    "time": 30,
    "tags": ["bowls", "low-cal"],
    "description": "sweet potato, goat cheese, hot honey"
  },
  {
    "slug": "taco-beef-bowl-classic",
    "title": "Taco Beef Bowl Classic",
    "time": 20,
    "tags": ["bowls", "meal-prep", "high-protein"],
    "description": "black beans, corn, avocado, crema"
  }
]
```

- [ ] **Step 5: Commit**

```bash
git add recipes/*.md recipes.json
git commit -m "feat: add frontmatter to recipes and create recipes.json index"
```

---

### Task 2: HTML Shell - Boilerplate, Design System, Router

Create `index.html` with Tailwind config, design tokens, fonts, header, and hash router.

**Files:**
- Create: `index.html`

- [ ] **Step 1: Create `index.html` with head, Tailwind config, and design tokens**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LAB KITCHEN</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800;900&family=Newsreader:ital,opsz,wght@0,6..72,200..800;1,6..72,200..800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
<script>
tailwind.config = {
  theme: {
    extend: {
      colors: {
        "primary-fixed": "#2ff801",
        "tertiary": "#0846ed",
        "on-background": "#2d2f2f",
        "background": "#f6f6f6",
        "surface-white": "#ffffff",
        "outline": "#757777",
        "outline-variant": "#acadad",
      },
      fontFamily: {
        headline: ["Space Grotesk", "sans-serif"],
        body: ["Newsreader", "serif"],
      },
      borderRadius: { DEFAULT: "0px", lg: "0px", xl: "0px", full: "9999px" },
    },
  },
};
</script>
<style>
  .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
  .neo-shadow { box-shadow: 4px 4px 0px 0px #2d2f2f; }
  /* Markdown rendered content styling */
  .recipe-content h2 { font-family: 'Space Grotesk'; font-weight: 900; font-size: 1.5rem; text-transform: uppercase; letter-spacing: -0.025em; margin-top: 2rem; margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 3px solid #2d2f2f; }
  .recipe-content h3 { font-family: 'Space Grotesk'; font-weight: 700; font-size: 1.1rem; text-transform: uppercase; margin-top: 1.5rem; margin-bottom: 0.5rem; }
  .recipe-content ul { list-style: disc; padding-left: 1.5rem; margin-bottom: 1rem; }
  .recipe-content li { margin-bottom: 0.25rem; font-size: 1.1rem; line-height: 1.6; }
  .recipe-content p { margin-bottom: 0.75rem; font-size: 1.1rem; line-height: 1.6; }
  .recipe-content strong { font-family: 'Space Grotesk'; font-weight: 700; }
</style>
</head>
<body class="bg-background text-on-background min-h-screen font-body">
```

- [ ] **Step 2: Add header and main container**

```html
<header class="bg-background fixed top-0 w-full z-50 border-b-4 border-on-background flex justify-between items-center px-6 py-4">
  <div class="flex items-center gap-3">
    <span class="material-symbols-outlined text-primary-fixed text-2xl">biotech</span>
    <h1 class="font-headline font-black uppercase tracking-tighter text-3xl text-on-background italic">LAB KITCHEN</h1>
  </div>
  <a id="back-btn" href="#/" class="hidden font-headline font-bold text-sm uppercase tracking-widest border-2 border-on-background px-3 py-1 hover:bg-on-background hover:text-white transition-colors">
    <span class="material-symbols-outlined text-sm align-middle">arrow_back</span> BACK
  </a>
</header>

<main id="app" class="pt-24 px-6 max-w-4xl mx-auto pb-16">
  <!-- Views rendered here by JS -->
</main>
```

- [ ] **Step 3: Add JavaScript - config, state, router**

```html
<script>
const REPO = 'mgregor-png/kitchen-lab';
const BRANCH = 'main';
const RAW = `https://raw.githubusercontent.com/${REPO}/${BRANCH}`;

const state = {
  recipes: [],
  activeFilters: new Set(),
  currentRecipe: null,
  shopChecked: {},  // { slug: Set([ingredient indices]) }
};

// --- Router ---
function router() {
  const hash = location.hash || '#/';
  const app = document.getElementById('app');
  const backBtn = document.getElementById('back-btn');

  if (hash === '#/') {
    backBtn.classList.add('hidden');
    renderRecipeList(app);
  } else if (hash.match(/^#\/recipe\/([^/]+)\/shop$/)) {
    const slug = hash.match(/^#\/recipe\/([^/]+)\/shop$/)[1];
    backBtn.classList.remove('hidden');
    backBtn.href = `#/recipe/${slug}`;
    renderShoppingList(app, slug);
  } else if (hash.match(/^#\/recipe\/([^/]+)$/)) {
    const slug = hash.match(/^#\/recipe\/([^/]+)$/)[1];
    backBtn.classList.remove('hidden');
    backBtn.href = '#/';
    renderRecipeDetail(app, slug);
  }
}

window.addEventListener('hashchange', router);
window.addEventListener('DOMContentLoaded', async () => {
  await loadRecipes();
  router();
});

async function loadRecipes() {
  try {
    const res = await fetch(`${RAW}/recipes.json`);
    state.recipes = await res.json();
  } catch (e) {
    console.error('Failed to load recipes:', e);
    state.recipes = [];
  }
}
</script>
```

- [ ] **Step 4: Close body/html tags**

```html
</body>
</html>
```

- [ ] **Step 5: Verify shell loads**

Open `index.html` in browser. Should see LAB KITCHEN header on light gray background. No errors in console.

- [ ] **Step 6: Commit**

```bash
git add index.html
git commit -m "feat: add HTML shell with design system, router, and recipe loader"
```

---

### Task 3: Recipe List View

Render the recipe list with filter pills and recipe cards.

**Files:**
- Modify: `index.html` (add `renderRecipeList` function and helpers)

- [ ] **Step 1: Add tag classification helper**

Insert before the closing `</script>` tag:

```javascript
function getTagStyle(tag) {
  const t = tag.toLowerCase();
  // Category tags - green
  if (['meal-prep', 'prep', 'project', 'sunday'].some(k => t.includes(k)))
    return 'background:#2ff801; color:#000;';
  // Type tags - blue
  if (['bowl', 'quick', 'one-pot', 'wrap', 'salad'].some(k => t.includes(k)))
    return 'background:#0846ed; color:#fff;';
  // Nutrition tags - outline
  if (['protein', 'cal', 'carb', 'vegan', 'gluten'].some(k => t.includes(k)))
    return 'background:transparent; color:#2d2f2f; border:1px solid #999;';
  // Default - outline
  return 'background:transparent; color:#2d2f2f; border:1px solid #999;';
}
```

- [ ] **Step 2: Add `renderRecipeList` function**

```javascript
function renderRecipeList(container) {
  const allTags = [...new Set(state.recipes.flatMap(r => r.tags))].sort();

  const filtered = state.activeFilters.size === 0
    ? state.recipes
    : state.recipes.filter(r => r.tags.some(t => state.activeFilters.has(t)));

  container.innerHTML = `
    <section class="mb-8">
      <div class="flex flex-wrap gap-2 mb-8">
        <button onclick="clearFilters()" class="font-headline font-bold text-xs uppercase tracking-widest px-3 py-1 border-2 transition-colors ${
          state.activeFilters.size === 0
            ? 'bg-on-background text-white border-on-background'
            : 'bg-transparent text-on-background border-outline-variant hover:border-on-background'
        }">ALL</button>
        ${allTags.map(tag => `
          <button onclick="toggleFilter('${tag}')" class="font-headline font-bold text-xs uppercase tracking-widest px-3 py-1 border-2 transition-colors ${
            state.activeFilters.has(tag)
              ? 'bg-on-background text-white border-on-background'
              : 'bg-transparent text-on-background border-outline-variant hover:border-on-background'
          }">${tag}</button>
        `).join('')}
      </div>
    </section>

    <section class="flex flex-col gap-4">
      ${filtered.map(r => `
        <a href="#/recipe/${r.slug}" class="block border-4 border-on-background bg-surface-white p-4 neo-shadow hover:translate-y-0.5 hover:shadow-[2px_2px_0px_0px_#2d2f2f] transition-all flex justify-between items-center gap-4">
          <div class="flex-1 min-w-0">
            <div class="font-headline font-black text-xl uppercase leading-tight truncate">${r.title}</div>
            <div class="font-body italic text-sm text-outline mt-1">${r.description}</div>
            <div class="flex flex-wrap gap-1.5 mt-2">
              ${r.tags.map(t => `<span class="font-headline font-bold text-[10px] uppercase tracking-wide px-2 py-0.5" style="${getTagStyle(t)}">${t}</span>`).join('')}
            </div>
          </div>
          <div class="text-center pl-4 border-l-[3px] border-on-background min-w-[60px] flex-none">
            <div class="font-headline font-black text-3xl leading-none">${r.time}</div>
            <div class="font-headline font-bold text-[10px] uppercase text-outline">MIN</div>
          </div>
        </a>
      `).join('')}
    </section>

    ${filtered.length === 0 ? '<p class="font-headline text-center text-outline mt-12 uppercase">No recipes match these filters</p>' : ''}
  `;
}

function toggleFilter(tag) {
  if (state.activeFilters.has(tag)) state.activeFilters.delete(tag);
  else state.activeFilters.add(tag);
  renderRecipeList(document.getElementById('app'));
}

function clearFilters() {
  state.activeFilters.clear();
  renderRecipeList(document.getElementById('app'));
}
```

- [ ] **Step 3: Verify recipe list renders**

Open `index.html` in browser. Should see 3 recipe cards with filter pills. Click a filter pill - list should update. Click ALL to reset.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add recipe list view with tag filtering"
```

---

### Task 4: Recipe Detail View

Fetch and render a single recipe markdown with responsive split/single-column layout.

**Files:**
- Modify: `index.html` (add `renderRecipeDetail`, `fetchRecipe`, `parseFrontmatter`, `parseIngredients`)

- [ ] **Step 1: Add markdown fetching and parsing helpers**

```javascript
async function fetchRecipe(slug) {
  const res = await fetch(`${RAW}/recipes/${slug}.md`);
  if (!res.ok) return null;
  const text = await res.text();
  return parseRecipeMarkdown(text);
}

function parseRecipeMarkdown(text) {
  let body = text;
  let meta = {};

  // Parse YAML frontmatter
  const fmMatch = text.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (fmMatch) {
    const fmText = fmMatch[1];
    body = fmMatch[2];
    // Simple YAML parsing for our known fields
    const titleMatch = fmText.match(/title:\s*(.+)/);
    const timeMatch = fmText.match(/time:\s*(\d+)/);
    const descMatch = fmText.match(/description:\s*(.+)/);
    const tagsMatch = fmText.match(/tags:\s*\[([^\]]*)\]/);
    if (titleMatch) meta.title = titleMatch[1].trim();
    if (timeMatch) meta.time = parseInt(timeMatch[1]);
    if (descMatch) meta.description = descMatch[1].trim();
    if (tagsMatch) meta.tags = tagsMatch[1].split(',').map(t => t.trim());
  }

  // Extract ingredients from ## Ingredients section
  const ingMatch = body.match(/## Ingredients\n([\s\S]*?)(?=\n## |\n$|$)/);
  const ingredients = ingMatch
    ? ingMatch[1].trim().split('\n').filter(l => l.startsWith('- ')).map(l => l.replace(/^- /, ''))
    : [];

  // Remove ## Ingredients section from body for display (we show it separately)
  const displayBody = body.replace(/## Ingredients\n[\s\S]*?(?=\n## |\n$|$)/, '').trim();

  return { meta, body: displayBody, ingredients, raw: body };
}
```

- [ ] **Step 2: Add `renderRecipeDetail` function**

```javascript
async function renderRecipeDetail(container, slug) {
  container.innerHTML = '<p class="font-headline text-center text-outline mt-12 uppercase animate-pulse">Loading recipe...</p>';

  const recipe = await fetchRecipe(slug);
  if (!recipe) {
    container.innerHTML = '<p class="font-headline text-center text-outline mt-12 uppercase">Recipe not found</p>';
    return;
  }

  const { meta, body, ingredients } = recipe;
  const htmlBody = marked.parse(body);
  const title = meta.title || slug;

  container.innerHTML = `
    <!-- Mobile: single column. Desktop: split layout -->
    <div class="grid grid-cols-1 md:grid-cols-12 -mx-6 -mt-2">

      <!-- Ingredients sidebar (desktop: dark sidebar, mobile: collapsible) -->
      <aside class="md:col-span-4 bg-on-background text-white p-6 md:p-8 border-b-4 md:border-b-0 md:border-r-4 border-black md:min-h-[80vh]">
        <button onclick="this.nextElementSibling.classList.toggle('hidden'); this.querySelector('.arrow').classList.toggle('rotate-180')" class="md:pointer-events-none flex justify-between items-center w-full mb-6">
          <h3 class="font-headline font-black text-2xl uppercase tracking-tight flex items-center gap-2">
            <span class="material-symbols-outlined text-primary-fixed">list_alt</span>
            Ingredients
          </h3>
          <span class="material-symbols-outlined arrow transition-transform md:hidden">expand_more</span>
        </button>
        <div class="md:!block">
          <ul class="space-y-3 mb-8">
            ${ingredients.map(ing => {
              // Try to split quantity from ingredient name
              const qtyMatch = ing.match(/^([\d.,/\-~]+\s*(?:g|kg|ml|l|tbsp|tsp|cloves?|heads?|packs?|cans?|bunch(?:es)?)?)\s+(.+)$/i);
              if (qtyMatch) {
                return `<li class="flex justify-between border-b border-white/20 pb-2">
                  <span class="font-body italic text-lg">${qtyMatch[2]}</span>
                  <span class="font-headline font-bold text-sm text-primary-fixed uppercase">${qtyMatch[1]}</span>
                </li>`;
              }
              return `<li class="border-b border-white/20 pb-2">
                <span class="font-body italic text-lg">${ing}</span>
              </li>`;
            }).join('')}
          </ul>
          <a href="#/recipe/${slug}/shop" class="block w-full bg-primary-fixed text-on-background font-headline font-black py-3 border-4 border-black neo-shadow hover:translate-y-0.5 hover:shadow-[2px_2px_0px_0px_black] transition-all uppercase tracking-widest text-center text-sm">
            Shopping List
          </a>
        </div>
      </aside>

      <!-- Recipe body -->
      <section class="md:col-span-8 p-6 md:p-8 bg-surface-white">
        <div class="flex justify-between items-start mb-8">
          <h2 class="font-headline font-black text-3xl md:text-4xl uppercase leading-none tracking-tight">${title}</h2>
          <div class="flex flex-col items-center flex-none ml-4">
            <span class="font-headline font-black text-[10px] uppercase text-outline">TIME</span>
            <span class="font-headline font-bold text-lg uppercase">${meta.time || '?'} MIN</span>
          </div>
        </div>
        <div class="recipe-content">
          ${htmlBody}
        </div>
      </section>
    </div>
  `;
}
```

- [ ] **Step 3: Verify recipe detail renders**

Click a recipe card. Should see split layout on desktop (dark ingredients sidebar + light steps area). Resize to mobile - should collapse to single column with collapsible ingredients. "Shopping List" button should be visible.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: add recipe detail view with responsive split layout"
```

---

### Task 5: Shopping List View

Render ingredient checkboxes with dim/sort behavior, localStorage persistence, and clipboard copy.

**Files:**
- Modify: `index.html` (add `renderShoppingList` and helpers)

- [ ] **Step 1: Add localStorage helpers for shopping state**

```javascript
function getShopChecked(slug) {
  try {
    const stored = localStorage.getItem(`kitchen-lab-shop-${slug}`);
    return stored ? new Set(JSON.parse(stored)) : new Set();
  } catch { return new Set(); }
}

function saveShopChecked(slug, checkedSet) {
  localStorage.setItem(`kitchen-lab-shop-${slug}`, JSON.stringify([...checkedSet]));
}
```

- [ ] **Step 2: Add `renderShoppingList` function**

```javascript
async function renderShoppingList(container, slug) {
  container.innerHTML = '<p class="font-headline text-center text-outline mt-12 uppercase animate-pulse">Loading...</p>';

  const recipe = await fetchRecipe(slug);
  if (!recipe) {
    container.innerHTML = '<p class="font-headline text-center text-outline mt-12 uppercase">Recipe not found</p>';
    return;
  }

  const { meta, ingredients } = recipe;
  const checked = getShopChecked(slug);

  // Sort: unchecked first, then checked
  const sorted = ingredients.map((ing, i) => ({ ing, i }))
    .sort((a, b) => {
      const aChecked = checked.has(a.i);
      const bChecked = checked.has(b.i);
      if (aChecked === bChecked) return a.i - b.i;
      return aChecked ? 1 : -1;
    });

  container.innerHTML = `
    <section class="max-w-2xl mx-auto">
      <div class="border-b-4 border-on-background pb-3 mb-8">
        <h2 class="font-headline font-black text-2xl uppercase tracking-tight">${meta.title || slug}</h2>
        <span class="font-headline font-bold text-xs uppercase tracking-widest text-outline">Shopping List</span>
      </div>

      <div class="flex flex-col gap-2 mb-8" id="shop-items">
        ${sorted.map(({ ing, i }) => {
          const isChecked = checked.has(i);
          return `
            <label class="flex items-center gap-3 p-3 border-4 border-on-background cursor-pointer transition-all select-none ${
              isChecked ? 'opacity-40 bg-background' : 'bg-surface-white neo-shadow'
            }" onclick="toggleShopItem('${slug}', ${i})">
              <div class="w-6 h-6 border-3 border-on-background flex items-center justify-center flex-none ${
                isChecked ? 'bg-on-background' : 'bg-transparent'
              }">
                ${isChecked ? '<span class="material-symbols-outlined text-white text-sm">check</span>' : ''}
              </div>
              <span class="font-body text-lg ${isChecked ? 'line-through' : ''}">${ing}</span>
            </label>
          `;
        }).join('')}
      </div>

      <div class="flex gap-3">
        <button onclick="copyShopList('${slug}')" class="flex-1 bg-primary-fixed text-on-background font-headline font-black py-3 border-4 border-on-background neo-shadow hover:translate-y-0.5 hover:shadow-[2px_2px_0px_0px_#2d2f2f] transition-all uppercase tracking-widest text-sm flex items-center justify-center gap-2">
          <span class="material-symbols-outlined text-lg">content_copy</span>
          Copy Needed Items
        </button>
        <button onclick="clearShopList('${slug}')" class="bg-transparent text-on-background font-headline font-bold py-3 px-4 border-4 border-outline-variant hover:border-on-background transition-colors uppercase tracking-widest text-sm">
          Reset
        </button>
      </div>
    </section>
  `;
}
```

- [ ] **Step 3: Add toggle, copy, and clear handlers**

```javascript
function toggleShopItem(slug, index) {
  const checked = getShopChecked(slug);
  if (checked.has(index)) checked.delete(index);
  else checked.add(index);
  saveShopChecked(slug, checked);
  // Re-render to re-sort
  renderShoppingList(document.getElementById('app'), slug);
}

async function copyShopList(slug) {
  const recipe = await fetchRecipe(slug);
  if (!recipe) return;
  const checked = getShopChecked(slug);
  const needed = recipe.ingredients.filter((_, i) => !checked.has(i));
  const text = needed.map(ing => `- ${ing}`).join('\n');
  await navigator.clipboard.writeText(text);

  // Flash feedback on button
  const btn = event.target.closest('button');
  const original = btn.innerHTML;
  btn.innerHTML = '<span class="material-symbols-outlined text-lg">check</span> Copied!';
  btn.classList.add('bg-on-background', 'text-white');
  btn.classList.remove('bg-primary-fixed', 'text-on-background');
  setTimeout(() => {
    btn.innerHTML = original;
    btn.classList.remove('bg-on-background', 'text-white');
    btn.classList.add('bg-primary-fixed', 'text-on-background');
  }, 1500);
}

function clearShopList(slug) {
  localStorage.removeItem(`kitchen-lab-shop-${slug}`);
  renderShoppingList(document.getElementById('app'), slug);
}
```

- [ ] **Step 4: Verify shopping list works**

Navigate to a recipe, click "Shopping List". Check some items - they should dim and sort to bottom. Click "Copy Needed Items" - paste somewhere to verify only unchecked items are copied. Refresh page - checked state should persist. Click "Reset" - all items unchecked.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: add shopping list view with checkboxes, sort, and clipboard copy"
```

---

### Task 6: Deploy to GitHub Pages

Enable GitHub Pages and push all changes.

**Files:**
- No new files

- [ ] **Step 1: Push all changes**

```bash
git push
```

- [ ] **Step 2: Enable GitHub Pages**

```bash
gh api repos/mgregor-png/kitchen-lab/pages -X POST -f source.branch=main -f source.path=/ 2>/dev/null || \
gh api repos/mgregor-png/kitchen-lab/pages -X PUT -f source.branch=main -f source.path=/
```

- [ ] **Step 3: Verify deployment**

Wait ~60 seconds, then open: `https://mgregor-png.github.io/kitchen-lab/`

Should see recipe list. Click a recipe - should load and render. Click shopping list - should work with checkboxes.

- [ ] **Step 4: Commit any final fixes**

If any URLs or paths need adjustment after testing on GitHub Pages, fix and push.
