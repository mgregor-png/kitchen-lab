# Kitchen Lab Web App - Design Spec

## Overview

Single-page web app for browsing recipes and generating shopping checklists. Static HTML hosted on GitHub Pages. Recipes stored as markdown in the git repo, fetched and rendered client-side.

## Architecture

- **Stack:** Single HTML file, vanilla JavaScript, Tailwind CSS via CDN
- **Hosting:** GitHub Pages (mgregor-png/kitchen-lab)
- **Data source:** Recipe markdown files fetched from GitHub raw URLs at runtime
- **Routing:** Hash-based (`#/`, `#/recipe/gyros`, `#/recipe/gyros/shop`)

## Design System

Taken from the Lab Kitchen Stitch mockups (brutalist-neon aesthetic).

- **Fonts:** Space Grotesk (headlines, labels, UI), Newsreader (body text, descriptions)
- **Colors:**
  - Primary green: `#2ff801`
  - Tertiary blue: `#0846ed`
  - Dark: `#2d2f2f`
  - Background: `#f6f6f6`
  - Surface white: `#ffffff`
- **Borders:** 4px solid, 0px border-radius (brutalist)
- **Shadows:** neo-shadow: `4px 4px 0px 0px #2d2f2f`
- **Icons:** Material Symbols Outlined (Google Fonts CDN)

## Recipe Data Format

Each recipe markdown file includes YAML-like frontmatter:

```markdown
---
title: Gyros / Shawarma Meal Prep
time: 25
tags: [meal-prep, high-protein]
description: roasted veg, rice, tzatziki
---

# Gyros / Shawarma Meal Prep Guide

## Meat
- 600-800 g chicken thighs
...

## Ingredients
- 600-800 g chicken thighs
- 500-700 g Greek yogurt
...
```

An index file `recipes.json` lists all recipes with metadata for the list view:

```json
[
  {
    "slug": "gyros",
    "title": "Gyros / Shawarma Meal Prep",
    "time": 25,
    "tags": ["meal-prep", "high-protein"],
    "description": "roasted veg, rice, tzatziki"
  }
]
```

## Views

### 1. Recipe List (home - `#/`)

- **Header:** LAB KITCHEN branding, font-black uppercase italic, border-b-4
- **Filter bar:** Horizontal row of pill buttons. ALL is selected by default (dark bg). Other pills: generated from all unique tags across recipes. Clicking a pill filters the list to recipes matching that tag. Multiple selection toggles.
- **Recipe rows:** Brutalist cards with neo-shadow. Layout:
  - Left side: recipe title (font-black uppercase) + description (Newsreader italic) + tag pills below
  - Right side: time column separated by border-left-3, big number + "MIN" label
- **Tag pill colors:**
  - Category tags (meal-prep, bowls, etc.): `#2ff801` bg, black text
  - Type tags (quick, one-pot, etc.): `#0846ed` bg, white text
  - Nutrition tags (high-protein, low-cal, etc.): transparent bg, `#2d2f2f` text, 1px border
- **Click:** navigates to recipe detail view

### 2. Recipe Detail (`#/recipe/{slug}`)

- **Mobile (<768px):** Single column layout
  - Ingredients section at top, collapsible (tap to expand/collapse)
  - Recipe steps below, rendered from markdown
  - "Shopping List" button at bottom of ingredients
- **Desktop (>=768px):** Split layout (matches Stitch cook_mode mockup)
  - Left sidebar (md:col-span-4): dark background (`#2d2f2f`), white text, ingredient list with quantities aligned right in green. "Shopping List" button at bottom.
  - Right main area (md:col-span-8): light background, numbered steps with step numbers in bordered squares (hover turns green)
- **Back button:** returns to recipe list

### 3. Shopping List (`#/recipe/{slug}/shop`)

- **Header:** recipe name + "Shopping List" label
- **Ingredient checkboxes:** Each ingredient from the recipe's `## Ingredients` section
  - Unchecked: full opacity, normal text
  - Checked (items you have): dimmed (opacity 0.4), strikethrough text, sorted to bottom of list
- **"Copy to Clipboard" button:** copies only unchecked (needed) items as plain text list
- **Persistence:** checkbox state saved to localStorage keyed by recipe slug
- **Back button:** returns to recipe detail

## Data Flow

1. App loads, fetches `recipes.json` from GitHub raw URL
2. Renders recipe list view from the index data (no need to fetch individual files yet)
3. On recipe click, fetches `recipes/{slug}.md` from GitHub raw URL
4. Parses frontmatter (simple regex, no library needed) and markdown body
5. Renders recipe detail view with parsed content
6. Markdown rendering: use marked.js from CDN for reliable markdown-to-HTML conversion

## GitHub Raw URL Pattern

```
https://raw.githubusercontent.com/mgregor-png/kitchen-lab/main/recipes.json
https://raw.githubusercontent.com/mgregor-png/kitchen-lab/main/recipes/{slug}.md
```

Note: GitHub raw URLs have a ~5 minute cache. Changes pushed from iOS app or Claude Code will appear within 5 minutes.

## Tag System

Tags are freeform strings defined in recipe frontmatter. No fixed taxonomy - new tags appear automatically in the filter bar as recipes are added. Tag color assignment:

- Tags containing "prep", "project", "sunday": green (category)
- Tags containing "bowl", "quick", "one-pot", "wrap", "salad": blue (type)
- Tags containing "protein", "cal", "carb", "vegan", "gluten": outline (nutrition)
- Default for unrecognized tags: outline style

## Not in Scope (v1)

- Search box
- Dark mode toggle
- Rohlik API integration
- Offline/PWA mode
- Recipe editing in-app
- Image support (future: recipe hero images)
