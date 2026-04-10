# Cooking App — Build Plan

## Workflow Split

| You (Martin) | Claude Code |
|---|---|
| Design all UI screens in Google Stitch | Scaffold project, nav structure, component shells |
| Export/screenshot Stitch screens | Wire Stitch UI to live data + navigation |
| Define which screen to tackle next | Backend: Supabase schema, auth, APIs, real-time |
| Test on device, give feedback | Instagram import logic, state management |
| UX decisions, feature prioritization | Styling foundations (tokens, dark theme, typography) |

---

## Phase 0: Foundation (Before any UI)
**Goal:** Runnable app shell with auth, DB, and navigation — so Stitch screens drop straight in.

- [ ] **0.1** Init Expo project with TypeScript + file-based routing (Expo Router)
- [ ] **0.2** Set up Supabase project (DB, Auth, Realtime enabled)
- [ ] **0.3** Design & deploy DB schema (see below)
- [ ] **0.4** Implement auth flow (Google + Apple social login via Supabase Auth)
- [ ] **0.5** Set up bottom tab navigation: Home Feed, The Lab, Cook Mode, The Pantry, My Stash
- [ ] **0.6** Create design token file — colors, typography scale, spacing, card styles (Mob Cooking-inspired dark theme)
- [ ] **0.7** Build reusable base components: Card, Button, ScreenWrapper, ListItem

**Your part:** While I scaffold, design the 5 main screens in Google Stitch. Reference Mob Cooking screenshots for visual direction.

---

## Phase 1: My Stash + Instagram Import
**Goal:** Core save-a-recipe loop working end to end.

- [ ] **1.1** Instagram import — manual URL paste (oEmbed fetch → extract title, thumbnail, video link)
- [ ] **1.2** Instagram import — Share Sheet integration (iOS/Android deep link handler)
- [ ] **1.3** Recipe detail screen (data model → UI shell)
- [ ] **1.4** My Stash screen — list of saved recipes, basic profile
- [ ] **1.5** Wire Stitch UI for My Stash + Recipe Detail when ready

**Your part:** Design My Stash and Recipe Detail screens in Stitch. Test the Instagram share flow on your phone.

---

## Phase 2: The Lab (Discovery)
**Goal:** Browse and search recipes.

- [ ] **2.1** Seed recipe data (manual entries or scraped for testing)
- [ ] **2.2** Category filtering: Speedy / Midweek / Sunday Projects
- [ ] **2.3** "What's in the Fridge?" — ingredient-based search (text input → match against recipe ingredients)
- [ ] **2.4** Wire Stitch UI for The Lab when ready

**Your part:** Design The Lab screen with category tabs and search bar in Stitch.

---

## Phase 3: Home Feed (Social)
**Goal:** See what friends are saving and cooking.

- [ ] **3.1** Friendships — add/accept friend flow, social graph in DB
- [ ] **3.2** Activity feed — query friends' recent saves/cooks, render as cards
- [ ] **3.3** Quick-save from feed to My Stash
- [ ] **3.4** Wire Stitch UI for Home Feed when ready

**Your part:** Design Home Feed and Add Friend screens in Stitch.

---

## Phase 4: Cook Mode (Real-time)
**Goal:** Step-by-step cooking with live friend sync.

- [ ] **4.1** Step-by-step recipe view (large text, high contrast, swipe between steps)
- [ ] **4.2** Supabase Realtime channel — broadcast current step to session participants
- [ ] **4.3** "Cook Together" session creation + join flow
- [ ] **4.4** Show friend avatars + their current step in real time
- [ ] **4.5** Wire Stitch UI for Cook Mode when ready

**Your part:** Design Cook Mode screen (kitchen-optimized: big text, minimal chrome, step indicator).

---

## Phase 5: The Pantry (Shared Shopping)
**Goal:** Collaborative shopping list with real-time sync.

- [ ] **5.1** Shopping list CRUD — add items, organize by aisle
- [ ] **5.2** Assign items to friends
- [ ] **5.3** Supabase Realtime sync — all collaborators see updates live
- [ ] **5.4** Auto-generate shopping list from recipe ingredients
- [ ] **5.5** Wire Stitch UI for The Pantry when ready

**Your part:** Design The Pantry screen in Stitch (list view with aisle grouping + friend assignment chips).

---

## Database Schema (Phase 0)

```
users
  id (uuid, PK)
  display_name (text)
  avatar_url (text)
  instagram_handle (text, nullable)
  cooking_streak (int, default 0)
  created_at (timestamptz)

recipes
  id (uuid, PK)
  title (text)
  description (text, nullable)
  source_url (text) — Instagram post URL
  thumbnail_url (text, nullable)
  video_url (text, nullable)
  ingredients (jsonb) — [{name, quantity, unit, aisle}]
  steps (jsonb) — [{order, instruction, duration_min}]
  effort_category (text) — 'speedy' | 'midweek' | 'sunday_project'
  prep_time_min (int)
  created_by (uuid, FK → users)
  created_at (timestamptz)

saved_recipes
  user_id (uuid, FK → users)
  recipe_id (uuid, FK → recipes)
  saved_at (timestamptz)
  PK (user_id, recipe_id)

friendships
  id (uuid, PK)
  requester_id (uuid, FK → users)
  addressee_id (uuid, FK → users)
  status (text) — 'pending' | 'accepted'
  created_at (timestamptz)

cooking_sessions
  id (uuid, PK)
  recipe_id (uuid, FK → recipes)
  host_id (uuid, FK → users)
  status (text) — 'active' | 'completed'
  created_at (timestamptz)

session_participants
  session_id (uuid, FK → cooking_sessions)
  user_id (uuid, FK → users)
  current_step (int, default 0)
  joined_at (timestamptz)
  PK (session_id, user_id)

shopping_lists
  id (uuid, PK)
  name (text)
  created_by (uuid, FK → users)
  created_at (timestamptz)

shopping_list_members
  list_id (uuid, FK → shopping_lists)
  user_id (uuid, FK → users)
  PK (list_id, user_id)

shopping_list_items
  id (uuid, PK)
  list_id (uuid, FK → shopping_lists)
  name (text)
  quantity (text, nullable)
  aisle (text, nullable)
  assigned_to (uuid, FK → users, nullable)
  is_checked (boolean, default false)
  added_by (uuid, FK → users)
  created_at (timestamptz)

activity_feed
  id (uuid, PK)
  user_id (uuid, FK → users)
  action (text) — 'saved' | 'cooked' | 'started_session'
  recipe_id (uuid, FK → recipes, nullable)
  created_at (timestamptz)
```

---

## Key Architectural Decisions (Need Your Input)

1. **Instagram OAuth** — Meta's API is heavily restricted. Realistic MVP path is URL paste + Share Sheet only. Full OAuth would require app review. **Recommendation: skip OAuth for MVP, revisit later.** OK?

2. **Recipe parsing** — When a user pastes an Instagram URL, we get the embed (thumbnail + caption) via oEmbed. Structured recipe data (ingredients, steps) will need manual entry or an LLM extraction step. **Recommendation: start with manual entry, add AI extraction as a fast-follow.** OK?

3. **State management** — Zustand for local UI state + React Query (TanStack Query) for server state/caching. This is the modern standard for Expo apps. OK?

4. **Expo Router vs React Navigation** — Expo Router (file-based) is simpler for MVP and works well with Stitch-imported screens. OK?

5. **Where to host the codebase** — I can scaffold this inside `projects/cooking-app/app/` in this workspace, or we create a separate repo. **Recommendation: separate repo** (it's a real app, not CoS workspace tooling). You'd create a GitHub repo and I'd work in it. OK?
