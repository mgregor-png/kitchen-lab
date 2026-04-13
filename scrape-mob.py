#!/usr/bin/env python3
"""Scrape Finn Tonry recipes from mob.co.uk using JSON-LD structured data.

Extracts recipe name, ingredients, method steps, time, image, and nutrition
from the schema.org Recipe markup embedded in each page.
"""

import json
import os
import re
import ssl
import sys
import time
import urllib.request
import urllib.error
from html.parser import HTMLParser

# macOS Python SSL fix
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

CHEF_SLUG = 'finn-tonry'
BASE_URL = 'https://www.mob.co.uk'
RECIPES_DIR = os.path.join(os.path.dirname(__file__), 'recipes')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'recipes', 'images')
PAGES = 4  # Known pagination count


class JSONLDExtractor(HTMLParser):
    """Extract JSON-LD script blocks from HTML."""
    def __init__(self):
        super().__init__()
        self.in_jsonld = False
        self.data = []
        self.current = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            attr_dict = dict(attrs)
            if attr_dict.get('type') == 'application/ld+json':
                self.in_jsonld = True
                self.current = ''

    def handle_data(self, data):
        if self.in_jsonld:
            self.current += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.in_jsonld:
            self.in_jsonld = False
            try:
                parsed = json.loads(self.current)
                self.data.append(parsed)
            except json.JSONDecodeError:
                pass


def fetch_page(url, retries=3):
    """Fetch a URL with retries and delay."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml',
            })
            with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
                return resp.read().decode('utf-8', errors='replace')
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            print(f'  Retry {attempt + 1}/{retries} for {url}: {e}')
            time.sleep(2)
    return None


def get_recipe_urls():
    """Collect all recipe URLs from the chef's paginated listing."""
    urls = set()
    for page in range(1, PAGES + 1):
        url = f'{BASE_URL}/chefs/{CHEF_SLUG}' if page == 1 else f'{BASE_URL}/chefs/{CHEF_SLUG}/page/{page}'
        print(f'Fetching listing page {page}...')
        html = fetch_page(url)
        if not html:
            print(f'  Failed to fetch page {page}')
            continue
        # Extract /recipes/... hrefs
        for match in re.finditer(r'href="(/recipes/[^"]+)"', html):
            path = match.group(1)
            urls.add(path)
        time.sleep(1)
    return sorted(urls)


def extract_recipe_jsonld(html):
    """Extract the Recipe JSON-LD from a page."""
    parser = JSONLDExtractor()
    parser.feed(html)
    for item in parser.data:
        # Handle @graph wrapper
        if isinstance(item, dict) and '@graph' in item:
            for node in item['@graph']:
                if isinstance(node, dict) and node.get('@type') == 'Recipe':
                    return node
        if isinstance(item, dict) and item.get('@type') == 'Recipe':
            return item
        if isinstance(item, list):
            for node in item:
                if isinstance(node, dict) and node.get('@type') == 'Recipe':
                    return node
    return None


def parse_duration(iso):
    """Parse ISO 8601 duration like PT10M, PT1H30M to minutes."""
    if not iso:
        return 0
    m = re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?', iso)
    if not m:
        return 0
    days = int(m.group(1) or 0)
    hours = int(m.group(2) or 0)
    mins = int(m.group(3) or 0)
    return days * 1440 + hours * 60 + mins


def slugify(text):
    """Convert recipe name to a filename slug."""
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s-]+', '-', s)
    return s.strip('-')


def download_image(image_url, slug):
    """Download recipe image and return local relative path."""
    if not image_url:
        return None
    os.makedirs(IMAGES_DIR, exist_ok=True)
    ext = '.jpg'
    if '.png' in image_url.lower():
        ext = '.png'
    elif '.webp' in image_url.lower():
        ext = '.webp'
    local_path = os.path.join(IMAGES_DIR, f'{slug}{ext}')
    if os.path.exists(local_path):
        return f'images/{slug}{ext}'
    try:
        req = urllib.request.Request(image_url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        })
        with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
            with open(local_path, 'wb') as f:
                f.write(resp.read())
        return f'images/{slug}{ext}'
    except Exception as e:
        print(f'  Failed to download image: {e}')
        return None


def recipe_to_markdown(recipe, image_url):
    """Convert a JSON-LD Recipe to Kitchen Lab markdown format."""
    name = recipe.get('name', 'Untitled')
    slug = slugify(name)

    total_time = parse_duration(recipe.get('totalTime') or recipe.get('cookTime') or recipe.get('prepTime'))
    if total_time == 0:
        total_time = 30  # default

    # Tags
    tags = ['finn-tonry']
    categories = recipe.get('recipeCategory', '')
    if isinstance(categories, str):
        categories = [c.strip().lower() for c in categories.split(',')]
    else:
        categories = [c.lower() for c in categories]

    if any('high protein' in c or 'high-protein' in c for c in categories):
        tags.append('high-protein')
    if any('meal-prep' in c or 'meal prep' in c for c in categories):
        tags.append('meal-prep')
    if any('vegetarian' in c for c in categories):
        tags.append('vegetarian')
    if any('vegan' in c for c in categories):
        tags.append('vegan')
    if any('pescatarian' in c for c in categories):
        tags.append('fish')

    cuisine = recipe.get('recipeCuisine', '')
    if isinstance(cuisine, str) and cuisine:
        cuisine_lower = cuisine.lower()
        cuisine_map = {
            'asian': 'asian', 'chinese': 'asian', 'japanese': 'japanese',
            'thai': 'thai', 'indian': 'indian', 'italian': 'italian',
            'mexican': 'mexican', 'mediterranean': 'mediterranean',
            'middle eastern': 'middle-eastern', 'french': 'french',
        }
        for key, tag in cuisine_map.items():
            if key in cuisine_lower:
                tags.append(tag)
                break

    # Quick tag
    if total_time < 30:
        tags.append('quick')

    description = recipe.get('description', '')
    if len(description) > 100:
        description = description[:97] + '...'

    # Frontmatter
    lines = ['---']
    lines.append(f'title: "{name}"')
    lines.append(f'time: {total_time}')
    lines.append(f'tags: [{", ".join(tags)}]')
    lines.append(f'description: "{description}"')
    if image_url:
        lines.append(f'image: "{image_url}"')
    lines.append(f'chef: "Finn Tonry"')
    lines.append(f'source: "https://www.mob.co.uk/recipes/{slug}"')
    lines.append('---')
    lines.append('')
    lines.append(f'# {name}')
    lines.append('')

    # Servings
    servings = recipe.get('recipeYield')
    if servings:
        lines.append(f'Serves {servings}')
        lines.append('')

    # Nutrition
    nutrition = recipe.get('nutrition', {})
    if nutrition and nutrition.get('calories'):
        lines.append(f'**Nutrition per serving:** {nutrition.get("calories", "")} cal, '
                     f'{nutrition.get("protein", "")}g protein, '
                     f'{nutrition.get("fat", "")}g fat, '
                     f'{nutrition.get("carbohydrates", "")}g carbs')
        lines.append('')

    # Method
    lines.append('## Method')
    lines.append('')
    instructions = recipe.get('recipeInstructions', [])
    for i, step in enumerate(instructions, 1):
        if isinstance(step, dict):
            text = step.get('text', '')
        else:
            text = str(step)
        lines.append(f'{i}. {text}')
        lines.append('')

    # Ingredients
    lines.append('## Ingredients')
    lines.append('')
    for ing in recipe.get('recipeIngredient', []):
        lines.append(f'- {ing}')

    return slug, '\n'.join(lines)


def main():
    os.makedirs(RECIPES_DIR, exist_ok=True)

    # Step 1: Collect recipe URLs
    print(f'Collecting recipe URLs for {CHEF_SLUG}...')
    recipe_paths = get_recipe_urls()
    print(f'Found {len(recipe_paths)} recipe URLs')

    # Deduplicate - some recipes have -2 variants (meal prep vs regular)
    # Keep all variants as they have different content

    # Step 2: Fetch each recipe and extract JSON-LD
    saved = 0
    skipped = 0
    failed = 0

    for i, path in enumerate(recipe_paths, 1):
        url = f'{BASE_URL}{path}'
        print(f'[{i}/{len(recipe_paths)}] {path}')

        html = fetch_page(url)
        if not html:
            print(f'  FAILED to fetch')
            failed += 1
            continue

        recipe = extract_recipe_jsonld(html)
        if not recipe:
            print(f'  No JSON-LD Recipe found')
            failed += 1
            continue

        slug, md = recipe_to_markdown(recipe, recipe.get('image'))

        # Download image
        image_cdn = recipe.get('image') or recipe.get('thumbnailUrl')

        # Save markdown
        filepath = os.path.join(RECIPES_DIR, f'{slug}.md')
        if os.path.exists(filepath):
            print(f'  SKIP (exists): {slug}.md')
            skipped += 1
        else:
            with open(filepath, 'w') as f:
                f.write(md)
            print(f'  SAVED: {slug}.md')
            saved += 1

        time.sleep(0.5)  # Be polite

    print(f'\nDone! Saved: {saved}, Skipped: {skipped}, Failed: {failed}')
    print(f'Total recipe files in recipes/: {len([f for f in os.listdir(RECIPES_DIR) if f.endswith(".md")])}')
    print(f'\nRun build-recipes.py to regenerate recipes.json')


if __name__ == '__main__':
    main()
