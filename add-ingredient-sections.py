#!/usr/bin/env python3
"""
add-ingredient-sections.py

Groups flat ingredient lists in Finn Tonry recipes into logical sub-sections
based on heuristics derived from the method steps.

Only modifies files with `chef: "Finn Tonry"` in frontmatter.
Only rewrites the ## Ingredients section; everything else is left untouched.
Requires at least 2 distinct component groups before adding headers.
"""

import os
import re
import sys

RECIPES_DIR = os.path.join(os.path.dirname(__file__), "recipes")


# ---------------------------------------------------------------------------
# Component detection patterns
# Each entry: (section_name, [regex patterns that indicate this component])
# Patterns are matched against method step text (case-insensitive).
# ---------------------------------------------------------------------------

COMPONENT_PATTERNS = [
    # Protein / main item (order matters — check before generic "sauce")
    ("Salmon",          [r"\bsalmon\b"]),
    ("Cod",             [r"\bcod\b"]),
    ("Prawns",          [r"\bprawn"]),
    ("Chicken",         [r"\bchicken\b"]),
    ("Beef",            [r"\bbeef\b"]),
    ("Lamb",            [r"\blamb\b"]),
    ("Pork",            [r"\bpork\b"]),
    ("Tofu",            [r"\btofu\b"]),
    ("Eggs",            [r"\begg(?:s)?\b"]),
    # Carbs / sides
    ("Rice",            [r"\brice\b", r"\bjasmine rice\b", r"\bfried rice\b"]),
    ("Noodles",         [r"\bnoodle"]),
    ("Pasta",           [r"\bpasta\b", r"\bspaghetti\b", r"\bpenne\b", r"\bfettuccine\b", r"\bmacaroni\b", r"\brigatoni\b", r"\borecchiette\b"]),
    # Components
    ("Sauce",           [r"\bsauce\b", r"\bfor the sauce\b", r"\bmake the sauce\b", r"\bsauce ingredient"]),
    ("Dressing",        [r"\bdressing\b", r"\bfor the dressing\b", r"\bwhisk the dressing\b"]),
    ("Marinade",        [r"\bmarinад", r"\bmarinate\b", r"\bmarinade\b"]),
    ("Salad",           [r"\bsalad\b", r"\bfor the salad\b", r"\bherb salad\b", r"\bcucumber salad\b"]),
    ("Salsa",           [r"\bsalsa\b"]),
    ("Slaw",            [r"\bslaw\b"]),
    ("Guacamole",       [r"\bguacamole\b", r"\bavocado crem"]),
    ("Hummus",          [r"\bhummus\b"]),
    ("Cream Cheese",    [r"\bcream cheese\b"]),
    ("Yoghurt",         [r"\byoghurt\b", r"\bgreek yoghurt\b"]),
    ("Smoothie",        [r"\bsmoothie\b", r"\bblend\b"]),
    ("Granola",         [r"\bgranola\b"]),
    ("Crumble",         [r"\bcrumble\b"]),
    ("Oats",            [r"\boat\b", r"\boats\b"]),
    # Garnish / serving
    ("To Serve",        [r"\bto serve\b", r"\bplate up\b", r"\bto assemble\b", r"\bto finish\b", r"\bfinish with\b", r"\bserve with\b"]),
]

# Ingredient name normalisation for matching:
# strip leading quantity/units and trailing prep notes
_STRIP_QTY_RE = re.compile(
    r"^(?:"
    r"(?:\d[\d,.]*[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]?)"
    r"(?:\s*[-–]\s*\d[\d,.]*[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]?)?"
    r"(?:\s+\d+/\d+)?"
    r"|[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]"
    r"|\d+/\d+"
    r")"
    r"(?:\s*(?:kg|g|mg|lb|oz|lbs|ml|l|tsp|tbsp|teaspoon|tablespoon|cup|cups|clove|cloves|fillet|fillets|piece|pieces|bunch|bunches|handful|handfuls|pinch|pinches|whole|large|small|medium|x)\.?)?"
    r"\s+",
    re.IGNORECASE,
)

def normalise_ingredient(raw: str) -> str:
    """Return lowercase ingredient name with quantity/units stripped."""
    name = raw.strip().lstrip("- ").strip()
    # Strip leading multiplier like "1x"
    name = re.sub(r"^\d+x\s+", "", name, flags=re.IGNORECASE)
    # Strip quantity
    for _ in range(3):
        new = _STRIP_QTY_RE.sub("", name).strip()
        if new == name:
            break
        name = new
    # Strip trailing prep notes
    name = re.sub(r",.*$", "", name).strip()
    # Strip parenthetical
    name = re.sub(r"\(.*?\)", "", name).strip()
    return name.lower()


def parse_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith("---"):
        return {}, content
    end = content.find("\n---", 3)
    if end == -1:
        return {}, content
    fm_block = content[3:end].strip()
    body = content[end + 4:]
    fm = {}
    for line in fm_block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        fm[key] = value
    return fm, body


def extract_method_steps(body: str) -> list[str]:
    """Return all method step text as a flat list of strings."""
    match = re.search(r"^## Method\s*$", body, re.MULTILINE)
    if not match:
        return []
    section = body[match.end():]
    next_heading = re.search(r"^##\s", section, re.MULTILINE)
    if next_heading:
        section = section[:next_heading.start()]
    steps = []
    for line in section.splitlines():
        line = line.strip()
        if line and not re.match(r"^\d+\.", line):
            # continuation line
            if steps:
                steps[-1] += " " + line
        elif line:
            steps.append(re.sub(r"^\d+\.\s*", "", line))
    return steps


def extract_ingredients_block(body: str) -> tuple[str, str, str]:
    """Return (before_ingredients, ingredients_lines, after_ingredients).
    ingredients_lines includes everything inside ## Ingredients until next ##.
    """
    match = re.search(r"^## Ingredients\s*\n", body, re.MULTILINE)
    if not match:
        return body, "", ""
    start = match.start()
    section_content_start = match.end()
    rest = body[section_content_start:]
    next_heading = re.search(r"^##\s", rest, re.MULTILINE)
    if next_heading:
        section_content = rest[:next_heading.start()]
        after = rest[next_heading.start():]
    else:
        section_content = rest
        after = ""
    before = body[:start] + "## Ingredients\n"
    return before, section_content, after


def detect_components_from_method(steps: list[str]) -> list[str]:
    """Return ordered list of component names found in method steps."""
    seen = []
    for name, patterns in COMPONENT_PATTERNS:
        for step in steps:
            for pat in patterns:
                if re.search(pat, step, re.IGNORECASE):
                    if name not in seen:
                        seen.append(name)
                    break
    return seen


def assign_ingredients_to_components(
    ingredient_lines: list[str],
    method_text: str,
    components: list[str],
) -> dict[str, list[str]]:
    """Assign each ingredient line to a component bucket.

    Strategy:
    1. Find all steps that mention this component.
    2. Check if any ingredient name appears in those steps.
    3. First matching component wins.
    4. Unmatched go to None (will become 'Base').
    """
    # Build a per-component bag of words from the method steps
    component_step_words: dict[str, str] = {}
    for name, patterns in COMPONENT_PATTERNS:
        if name not in components:
            continue
        relevant = []
        for step in method_text.split("\n"):
            for pat in patterns:
                if re.search(pat, step, re.IGNORECASE):
                    relevant.append(step.lower())
                    break
        component_step_words[name] = " ".join(relevant)

    buckets: dict[str, list[str]] = {c: [] for c in components}
    buckets[None] = []  # unmatched

    for raw_line in ingredient_lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("###"):
            continue  # skip blanks and existing sub-headers
        if not stripped.startswith("- "):
            # Could be a blank line or already-processed header — skip
            continue

        name = normalise_ingredient(stripped)
        if not name:
            buckets[None].append(raw_line)
            continue

        assigned = False
        for comp in components:
            words = component_step_words.get(comp, "")
            # Split ingredient name into tokens and look for any in method text
            tokens = re.split(r"[\s\-/]+", name)
            # Longer tokens are more specific — prefer them
            tokens_by_length = sorted(tokens, key=len, reverse=True)
            for token in tokens_by_length:
                if len(token) >= 3 and token in words:
                    buckets[comp].append(raw_line)
                    assigned = True
                    break
            if assigned:
                break

        if not assigned:
            buckets[None].append(raw_line)

    return buckets


def build_sectioned_ingredients(
    ingredient_lines: list[str],
    components: list[str],
    buckets: dict,
) -> str:
    """Build the new ingredient section body with ### sub-headers."""
    lines_out = []

    for comp in components:
        items = buckets.get(comp, [])
        if items:
            lines_out.append(f"### {comp}\n")
            for item in items:
                lines_out.append(item if item.endswith("\n") else item + "\n")
            lines_out.append("\n")

    # Unmatched
    leftover = buckets.get(None, [])
    if leftover:
        # If everything ended up in leftover, don't add a header
        all_items = sum(len(v) for k, v in buckets.items() if k is not None)
        if all_items > 0:
            lines_out.append("### Other\n")
        for item in leftover:
            lines_out.append(item if item.endswith("\n") else item + "\n")
        if all_items > 0:
            lines_out.append("\n")

    return "".join(lines_out)


def process_recipe(filepath: str) -> tuple[bool, str]:
    """Process a single recipe file. Returns (modified, reason)."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    fm, body = parse_frontmatter(content)
    if fm.get("chef") != "Finn Tonry":
        return False, "not Finn Tonry"

    # Check if already has sub-sections
    if re.search(r"^### ", body, re.MULTILINE):
        return False, "already has sub-sections"

    before, ingredients_block, after = extract_ingredients_block(body)
    if not ingredients_block.strip():
        return False, "no ingredients section"

    # Get ingredient lines (preserve originals including blank lines)
    ingredient_lines = [line + "\n" for line in ingredients_block.splitlines()]
    actual_items = [l for l in ingredient_lines if l.strip().startswith("- ")]
    if len(actual_items) < 4:
        return False, "too few ingredients to group"

    steps = extract_method_steps(body)
    method_text = "\n".join(steps)
    components = detect_components_from_method(steps)

    if len(components) < 2:
        return False, f"only {len(components)} component(s) detected — leaving flat"

    buckets = assign_ingredients_to_components(actual_items, method_text, components)

    # Count components that got at least one ingredient
    populated = [c for c in components if buckets.get(c)]
    leftover = buckets.get(None, [])

    # Need at least 2 populated sections to justify adding headers
    effective_sections = len(populated) + (1 if leftover else 0)
    if effective_sections < 2:
        return False, f"only {effective_sections} effective section(s) — leaving flat"

    new_ingredients_body = build_sectioned_ingredients(actual_items, components, buckets)

    # Reconstruct the frontmatter + body
    # Find frontmatter end in original content
    fm_end = content.find("\n---", 3)
    frontmatter_raw = content[:fm_end + 4]  # includes closing ---
    new_body = before + "\n" + new_ingredients_body + after
    new_content = frontmatter_raw + new_body

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    summary_parts = [f"{c}({len(buckets[c])})" for c in components if buckets.get(c)]
    if leftover:
        summary_parts.append(f"Other({len(leftover)})")
    return True, " | ".join(summary_parts)


def main():
    md_files = sorted(
        os.path.join(RECIPES_DIR, f)
        for f in os.listdir(RECIPES_DIR)
        if f.endswith(".md")
    )

    modified = []
    skipped = []

    for filepath in md_files:
        name = os.path.basename(filepath)
        try:
            changed, reason = process_recipe(filepath)
            if changed:
                modified.append((name, reason))
                print(f"  MODIFIED  {name}: {reason}")
            else:
                skipped.append((name, reason))
        except Exception as exc:
            print(f"  ERROR     {name}: {exc}", file=sys.stderr)
            import traceback
            traceback.print_exc()

    print()
    print(f"{'='*60}")
    print(f"Modified : {len(modified)} recipes")
    print(f"Skipped  : {len(skipped)} recipes")
    print(f"{'='*60}")

    if skipped:
        print("\nSkipped breakdown:")
        from collections import Counter
        reasons = Counter(r for _, r in skipped)
        for reason, count in reasons.most_common():
            print(f"  {count:3d}  {reason}")


if __name__ == "__main__":
    main()
