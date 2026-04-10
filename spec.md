# Cooking App — MVP Spec

## App Overview

A social cooking app where I and my friends save recipes from Instagram, discover new ones, cook together, and manage shared shopping lists. Design closely references the **Mob Cooking app** aesthetic — bold typography, rich/dark backgrounds, high visual contrast, food-forward imagery, tactile card-based layout, dark-mode-first.

## Core Features (MVP Scope)

### Home Feed
Social feed showing what friends are saving and cooking; activity cards with direct Instagram video links; quick-save to My Stash.

### The Lab (Discovery)
Recipes categorized by effort: "Speedy" (<30 min), "Midweek" (30–60 min), "Sunday Projects" (1h+); "What's in the Fridge?" ingredient-based search.

### Cook Mode
Full-screen recipe detail optimized for kitchen use (large text, high contrast, step-by-step); source Instagram video linked alongside; live collaborative session where friends can see which step you're on in real time.

### The Pantry
Shared shopping list organized by supermarket aisle; assign items to specific friends; syncs across collaborators in real time.

### My Stash
Personal profile with saved recipes, cooking streak tracking, and Instagram sync.

## Technical Stack

- **Frontend**: React Native (Expo) — cross-platform iOS/Android
- **Backend**: Node.js with real-time layer (Supabase Realtime preferred)
- **Database**: Supabase (PostgreSQL) — users, recipes, shopping lists, social graph
- **Auth**: Supabase Auth with Google/Apple social login
- **State Management**: Zustand or React Query
- **Instagram Recipe Import**: Support all three entry points — (1) iOS/Android Share Sheet (user shares post directly to app), (2) manual URL paste, (3) Instagram OAuth if feasible. Use oEmbed or deep links where the full API is restricted; clearly flag where manual input is the only viable path.

## Design Reference
- **Mob Cooking app** — bold typography, rich/dark backgrounds, high-contrast, food-forward imagery, tactile card-based layout, dark-mode-first

## Workflow
UI screens generated in **Google Stitch** → imported into codebase. Claude Code handles: backend wiring, API integrations, real-time logic, auth, and connecting Stitch-generated UI to live data.
