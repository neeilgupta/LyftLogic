from __future__ import annotations

import re
from typing import Iterable
from services.nutrition.contracts import Meal



_PUNCT_RE = re.compile(r"[^a-z0-9\s]+")
_WS_RE = re.compile(r"\s+")

# Alias expansion is allowed (helps catch common variants),
# but users are not restricted to a fixed allergy vocabulary.
_ALIAS_MAP: dict[str, set[str]] = {
    "potato": {"potato", "potatoes"},
    "potatoes": {"potato", "potatoes"},
    "chocolate": {"chocolate", "cocoa"},
    "milk": {"milk", "dairy", "whey", "casein", "butter", "cheese"},
    "dairy": {"milk", "dairy", "whey", "casein", "butter", "cheese"},
}


def normalize_term(term: str) -> str:
    """
    Canonicalizes a free-text term into a stable token.
    - lowercase
    - strip punctuation
    - collapse whitespace
    """
    if term is None:
        return ""
    t = term.strip().lower()
    t = _PUNCT_RE.sub(" ", t)
    t = _WS_RE.sub(" ", t).strip()
    return t


def build_allergen_set(user_terms: list[str]) -> set[str]:
    """
    Turns user allergy terms into a canonical token set, expanding aliases.
    Fail-safe behavior:
      - ignores empty/whitespace-only terms
    """
    out: set[str] = set()
    for raw in user_terms or []:
        tok = normalize_term(raw)
        if not tok:
            continue
        out.add(tok)
        if tok in _ALIAS_MAP:
            out |= _ALIAS_MAP[tok]
    return out


def _contains_list_is_valid(contains: object) -> bool:
    if not isinstance(contains, list) or len(contains) == 0:
        return False
    for x in contains:
        if not isinstance(x, str):
            return False
        if not normalize_term(x):
            return False
    return True

def _diet_tags_list_is_valid(diet_tags: object) -> bool:
    if not isinstance(diet_tags, list) or len(diet_tags) == 0:
        return False
    for x in diet_tags:
        if not isinstance(x, str):
            return False
        if not normalize_term(x):
            return False
    return True


def meal_is_safe(meal: Meal, allergen_set: set[str], required_diet_tags: set[str] | None = None) -> bool:
    """
    FAIL-CLOSED enforcement for BOTH:
      - allergens (must-not-contain)
      - diet tags (must-satisfy)

    required_diet_tags examples:
      - vegan: {"vegan"}
      - vegetarian: {"vegetarian"}  (AND allow vegan)
    """
    required_diet_tags = required_diet_tags or set()

    if not isinstance(meal, dict):
        return False

    ingredients = meal.get("ingredients")
    if not isinstance(ingredients, list) or len(ingredients) == 0:
        return False

    for ing in ingredients:
        if not isinstance(ing, dict):
            return False

        if ing.get("is_compound") is True:
            return False

        contains = ing.get("contains")
        if not _contains_list_is_valid(contains):
            return False

        diet_tags = ing.get("diet_tags")
        if not _diet_tags_list_is_valid(diet_tags):
            return False

        ing_tokens = {normalize_term(x) for x in contains}
        if "" in ing_tokens:
            return False
        if ing_tokens & allergen_set:
            return False

        ing_diet = {normalize_term(x) for x in diet_tags}
        if "" in ing_diet:
            return False

        # Diet enforcement (fail-closed)
        if required_diet_tags:
            # Special case: vegetarian allows vegan ingredients too
            if required_diet_tags == {"vegetarian"}:
                if not (("vegetarian" in ing_diet) or ("vegan" in ing_diet)):
                    return False
            else:
                # For vegan etc: ingredient must include all required tags
                if not required_diet_tags.issubset(ing_diet):
                    return False

    return True


def enforce_allergies(meals: list[dict], allergen_set: set[str], required_diet_tags: set[str] | None = None):
    """
    Returns (safe_meals, rejected_meals). No regeneration.
    """
    safe: list[dict] = []
    rejected: list[dict] = []

    for meal in meals or []:
        if meal_is_safe(meal, allergen_set, required_diet_tags=required_diet_tags):
            safe.append(meal)
        else:
            rejected.append(meal)

    return safe, rejected
