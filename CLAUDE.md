# Kitchen Lab

Recipes, meal planning, and Rohlik shopping list generation.

## How It Works

1. **Recipes** live in `recipes/` as markdown files with a `## Ingredients` section
2. **Product preferences** in `product-preferences.md` map ingredients to specific Rohlik products
3. To make a shopping list: read recipe ingredients, match against preferences first, search Rohlik live for the rest, create list via MCP

## Adding Recipes

- Paste text - save as structured md in `recipes/`
- Instagram/URL - try `get_url_content` first, fall back to paste text/screenshot
- Screenshot - read image, extract recipe

## Product Selection Rules

- **Meat:** always prefer farm ("od farmáře") and BIO
- **Everything else:** prefer user's Rohlik favourites
- Check `product-preferences.md` before searching

## Key Files

- `recipes/` - recipe markdown files
- `product-preferences.md` - ingredient-to-Rohlik-product mappings

## Domain Learnings

- Rohlik MCP `batch_search_products` handles up to 4 queries at once; plan batches of 4 for efficiency
- Product search results include `favourite: true` flag - use this to pick user-preferred products
- `get_url_content` supports browser actions (click, scroll, wait) for dynamic pages like Instagram
- Rohlik shopping lists support up to 15 products per `add_products_to_shopping_list` call
