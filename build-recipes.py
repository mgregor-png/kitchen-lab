#!/usr/bin/env python3
"""
build-recipes.py
Rebuilds recipes.json from all .md files in the recipes/ directory.
Adds an `ingredients` array of cleaned ingredient name strings.
"""

import json
import os
import re
import sys


RECIPES_DIR = os.path.join(os.path.dirname(__file__), "recipes")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "recipes.json")


# ---------------------------------------------------------------------------
# Quantity / unit patterns
# ---------------------------------------------------------------------------

# Numeric prefix: integers, decimals, fractions, ranges (e.g. "600g", "1 1/2",
# "2-3", "500-700", "1/2").  Also handles unicode fractions like "½".
_UNICODE_FRACTIONS = "½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞"

# Unit words (all lowercase; matched case-insensitively)
_UNITS = (
    r"kg|g|mg|lb|oz|lbs"          # weight
    r"|ml|l|litre|liter|litres|liters"  # volume
    r"|tsp|tbsp|teaspoon|tablespoon|teaspoons|tablespoons"
    r"|cup|cups|pint|pints|quart|quarts|fl oz"
    r"|bunch|bunches|handful|handfuls"
    r"|clove|cloves|head|heads|slice|slices|piece|pieces"
    r"|strip|strips|sprig|sprigs|stick|sticks|sheet|sheets"
    r"|can|cans|tin|tins|jar|jars|bag|bags|pack|packs|packet|packets"
    r"|pinch|pinches|dash|dashes|drop|drops"
    r"|stem|stems"                      # "5 stems curry leaves"
    r"|whole"                           # "1 whole chilli"
    r"|cm|mm|lt"                        # "4cm piece", "1lt stock"
    r"|large|small|medium|x large"     # size descriptors used as quantities
)

# Matches a leading quantity (number + optional unit), e.g.:
#   "600g ", "1 1/2 tsp ", "2-3 ", "500-700g ", "½ tsp ", "1  garlic"
_QUANTITY_RE = re.compile(
    r"^"
    r"(?:"
        # optional leading unicode fraction
        r"[" + _UNICODE_FRACTIONS + r"]"
        r"|"
        # numeric part: integer or decimal, optional range, optional fraction
        # \u2044 is the unicode FRACTION SLASH (⁄) used in some recipe sources
        # Also handles mixed numbers like "3⅓" (digit + unicode vulgar fraction)
        r"(?:\d[\d,.]*[" + _UNICODE_FRACTIONS + r"]?)"
        r"(?:\s*[-–]\s*\d[\d,.]*[" + _UNICODE_FRACTIONS + r"]?)?"
        r"(?:\s+\d+[\u2044/]\d+)?"
        r"(?:\s*%)?"  # optional percentage
        r"|"
        # plain vulgar fraction (with regular slash or fraction slash)
        r"\d+[\u2044/]\d+"
        r"|"
        # standalone unicode vulgar fraction (e.g. "½ tsp")
        r"[" + _UNICODE_FRACTIONS + r"]"
    r")"
    r"(?:\s*(?:" + _UNITS + r")\.?)?"   # optional unit
    r"\s+",                              # must be followed by a space
    re.IGNORECASE,
)

# Match compound quantity suffix: "plus N unit" e.g. "2 tbsp plus 1 tsp"
# Applied after primary quantity strip to clean up the remainder.
_COMPOUND_QTY_RE = re.compile(
    r"^plus\s+"
    r"(?:\d[\d,.]*(?:\s*[-–]\s*\d[\d,.]*)?(?:\s+\d+/\d+)?|[" + _UNICODE_FRACTIONS + r"]|\d+/\d+)"
    r"(?:\s*(?:" + _UNITS + r")\.?)?"
    r"\s+",
    re.IGNORECASE,
)

# Match a leading "of " after quantity stripping
_OF_RE = re.compile(r"^of\s+", re.IGNORECASE)

# Match trailing comma and everything after (e.g. ", halved", ", roughly chopped")
_TRAILING_PREP_RE = re.compile(r",.*$")

# Match parenthetical notes anywhere in the string
_PAREN_RE = re.compile(r"\(.*?\)")

# Lines that are clearly section headers or non-ingredient markers
_SKIP_LINE_RE = re.compile(r"^\*\*|^\+\s|^\(or\s", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body) from markdown content with --- delimiters."""
    if not content.startswith("---"):
        return {}, content

    end = content.find("\n---", 3)
    if end == -1:
        return {}, content

    fm_block = content[3:end].strip()
    body = content[end + 4:].lstrip("\n")

    fm = {}
    for line in fm_block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        # Strip surrounding quotes
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]

        # Parse YAML arrays: ["a", "b"] or [a, b]
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            items = [
                v.strip().strip('"').strip("'")
                for v in inner.split(",")
                if v.strip()
            ]
            fm[key] = items
        else:
            # Try numeric
            try:
                fm[key] = int(value)
            except ValueError:
                try:
                    fm[key] = float(value)
                except ValueError:
                    fm[key] = value

    return fm, body


def extract_ingredient_names(body: str) -> list[str]:
    """Extract cleaned ingredient name strings from the ## Ingredients section."""
    # Find the Ingredients section
    match = re.search(r"^## Ingredients\s*$", body, re.MULTILINE)
    if not match:
        return []

    section = body[match.end():]
    # Cut off at the next ## heading
    next_heading = re.search(r"^##\s", section, re.MULTILINE)
    if next_heading:
        section = section[:next_heading.start()]

    names = []
    for raw_line in section.splitlines():
        line = raw_line.strip()

        # Must start with "- "
        if not line.startswith("- "):
            continue
        line = line[2:].strip()

        # Skip section headers / non-ingredient markers
        if _SKIP_LINE_RE.match(line):
            continue

        # Skip lines that start with "(" (sub-recipe notes, alternatives)
        if line.startswith("("):
            continue

        # Normalize backslash-escaped fractions ("1\/8" -> "1/8")
        line = line.replace("\\/", "/")
        # Normalize ordinal fractions ("1/8th" -> "1/8")
        line = re.sub(r"(\d+/\d+)(?:th|rd|nd|st)\b", r"\1", line)

        # Strip parenthetical notes (e.g. "(about 2 large)", "(optional)")
        line = _PAREN_RE.sub("", line).strip()

        # Normalize "Nx" multiplier prefix like "1x 325g" -> "325g"
        line = re.sub(r"^\d+x\s+", "", line, flags=re.IGNORECASE).strip()

        # Normalize "Xunit-Yunit" ranges like "250g-280g" -> "250-280g"
        # so the range pattern can match them
        line = re.sub(
            r"(\d[\d,.]*)(" + _UNITS + r")\s*[-–]\s*(\d[\d,.]*)(\2)",
            r"\1-\3\4",
            line,
            flags=re.IGNORECASE,
        )

        # Strip dimension prefixes like "35cm x 22cm " -> ""
        line = re.sub(
            r"^\d[\d,.]*\s*(?:cm|mm)\s*x\s*\d[\d,.]*\s*(?:cm|mm)\s+",
            "",
            line,
            flags=re.IGNORECASE,
        ).strip()

        # Strip leading quantity+unit — loop up to 3 times to handle
        # chained quantities like "1 whole 5kg turkey" -> "5kg turkey" -> "turkey"
        for _ in range(3):
            new_line = _QUANTITY_RE.sub("", line).strip()
            if new_line == line:
                break
            line = new_line

        # Strip "Ncm-adjective" style descriptors that may be exposed after qty strip
        # (e.g. "10 2cm-thick slices" -> quantity loop -> "2cm-thick slices" -> "slices")
        line = re.sub(r"^\d[\d,.]*(?:cm|mm)-\w+\s+", "", line, flags=re.IGNORECASE).strip()

        # Strip compound quantity suffix (e.g. "plus 1 tsp" remaining after primary strip)
        line = _COMPOUND_QTY_RE.sub("", line).strip()

        # Strip leading "of " (e.g. "2 tbsp of olive oil" -> "olive oil")
        line = _OF_RE.sub("", line).strip()

        # Strip leading "tin of", "can of", "jar of" etc. if still present
        line = re.sub(r"^(?:tin|can|jar|bag|pack|packet)s?\s+of\s+", "", line, flags=re.IGNORECASE).strip()

        # Strip trailing prep instruction after first comma
        # "datterini tomatoes, or cherry tomatoes" -> "datterini tomatoes"
        line = _TRAILING_PREP_RE.sub("", line).strip()

        # Final cleanup: remove stray punctuation
        line = line.strip(".,;:")

        if line:
            names.append(line)

    return names


def slug_from_filename(filename: str) -> str:
    return os.path.splitext(os.path.basename(filename))[0]


def build_recipe_entry(filepath: str) -> dict:
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    fm, body = parse_frontmatter(content)
    slug = slug_from_filename(filepath)

    entry = {"slug": slug}

    if "title" in fm:
        entry["title"] = fm["title"]
    if "time" in fm:
        entry["time"] = fm["time"]
    if "tags" in fm:
        entry["tags"] = fm["tags"]
    if "description" in fm:
        entry["description"] = fm["description"]
    if "image" in fm:
        entry["image"] = fm["image"]
    if "chef" in fm:
        entry["chef"] = fm["chef"]

    entry["ingredients"] = extract_ingredient_names(body)

    return entry


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not os.path.isdir(RECIPES_DIR):
        print(f"ERROR: recipes directory not found at {RECIPES_DIR}", file=sys.stderr)
        sys.exit(1)

    md_files = sorted(
        [
            os.path.join(RECIPES_DIR, f)
            for f in os.listdir(RECIPES_DIR)
            if f.endswith(".md")
        ]
    )

    print(f"Processing {len(md_files)} recipe files...")

    recipes = []
    errors = []

    for filepath in md_files:
        try:
            entry = build_recipe_entry(filepath)
            recipes.append(entry)
        except Exception as exc:
            errors.append((filepath, str(exc)))
            print(f"  ERROR: {os.path.basename(filepath)}: {exc}", file=sys.stderr)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(recipes, f, indent=2, ensure_ascii=False)

    print(f"Written {len(recipes)} recipes to {OUTPUT_FILE}")
    if errors:
        print(f"{len(errors)} files failed — see errors above.", file=sys.stderr)

    # Quick sanity check: report stats
    with_ingredients = sum(1 for r in recipes if r.get("ingredients"))
    without_ingredients = sum(1 for r in recipes if not r.get("ingredients"))
    print(f"Recipes with ingredients: {with_ingredients}")
    print(f"Recipes without ingredients section: {without_ingredients}")


if __name__ == "__main__":
    main()
