# apps/backend/services/nutrition/allergens.py
from __future__ import annotations

import re
from typing import Iterable
from services.nutrition.contracts import Meal

_PUNCT_RE = re.compile(r"[^a-z0-9\s]+")
_WS_RE = re.compile(r"\s+")

# Canonical allergen tokens already used in meal_library contains:
# dairy, egg, gluten, soy, fish, shellfish, peanut, tree_nut, sesame

# Alias expansion: user terms -> canonical tokens (and common variants)
# Safety > recall: we expand aggressively and keep unknown tokens too.
_ALIAS_MAP: dict[str, set[str]] = {
    # ---- Categories / broad terms ----
    "nut": {"nut", "nuts", "tree_nut", "peanut"},
    "nuts": {"nut", "nuts", "tree_nut", "peanut"},
    "tree nut": {"tree_nut", "nuts"},
    "tree nuts": {"tree_nut", "nuts"},
    "treenut": {"tree_nut", "nuts"},
    "peanut": {"peanut", "nuts"},
    "peanuts": {"peanut", "nuts"},

    # ---- Dairy family ----
    "milk": {"milk", "dairy", "whey", "casein", "butter", "cheese", "yogurt"},
    "dairy": {"milk", "dairy", "whey", "casein", "butter", "cheese", "yogurt"},
    "whey": {"whey", "dairy", "milk"},
    "casein": {"casein", "dairy", "milk"},
    "butter": {"butter", "dairy", "milk"},
    "cheese": {"cheese", "dairy", "milk"},
    "yogurt": {"yogurt", "dairy", "milk"},
    "lactose": {"dairy", "milk"},
    "protein powder": {"whey", "dairy"},  # conservative

    # ---- Eggs / gluten / etc (common) ----
    "egg": {"egg", "eggs"},
    "eggs": {"egg", "eggs"},
    "gluten": {"gluten", "wheat"},
    "wheat": {"wheat", "gluten"},
    "soy": {"soy"},
    "fish": {"fish"},
    "shellfish": {"shellfish"},
    "sesame": {"sesame"},

    # ---- Specific nuts -> tree_nut ----
    "almond": {"almond", "almonds", "tree_nut", "nuts"},
    "almonds": {"almond", "almonds", "tree_nut", "nuts"},
    "walnut": {"walnut", "walnuts", "tree_nut", "nuts"},
    "walnuts": {"walnut", "walnuts", "tree_nut", "nuts"},
    "cashew": {"cashew", "cashews", "tree_nut", "nuts"},
    "cashews": {"cashew", "cashews", "tree_nut", "nuts"},
    "pistachio": {"pistachio", "pistachios", "tree_nut", "nuts"},
    "pistachios": {"pistachio", "pistachios", "tree_nut", "nuts"},
    "pecan": {"pecan", "pecans", "tree_nut", "nuts"},
    "pecans": {"pecan", "pecans", "tree_nut", "nuts"},
    "hazelnut": {"hazelnut", "hazelnuts", "tree_nut", "nuts"},
    "hazelnuts": {"hazelnut", "hazelnuts", "tree_nut", "nuts"},
    "macadamia": {"macadamia", "macadamias", "tree_nut", "nuts"},
    "macadamias": {"macadamia", "macadamias", "tree_nut", "nuts"},

    # ---- Existing examples ----
    "potato": {"potato", "potatoes"},
    "potatoes": {"potato", "potatoes"},
    "chocolate": {"chocolate", "cocoa"},
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


def _singularize_token(tok: str) -> str:
    # Minimal + deterministic singularization (good enough for “almonds”, “peanuts”, etc.)
    if len(tok) > 3 and tok.endswith("s"):
        return tok[:-1]
    return tok


def build_allergen_set(user_terms: list[str]) -> set[str]:
    """
    Turns user allergy terms into a canonical token set, expanding aliases.
    Safety-first behavior:
      - splits comma-separated input
      - lowercases + punctuation-strip
      - expands category inputs like "nuts" -> {"tree_nut","peanut",...}
      - keeps unknown tokens too (fail-safe)
    """
    out: set[str] = set()
    for raw in user_terms or []:
        if raw is None:
            continue

        # Allow user strings like "dairy, nuts"
        parts = [p.strip() for p in str(raw).split(",") if p.strip()]
        for p in parts:
            tok = normalize_term(p)
            if not tok:
                continue

            # Add raw token + singular form
            out.add(tok)
            out.add(_singularize_token(tok))

            # Expand aliases for both forms
            for k in (tok, _singularize_token(tok)):
                if k in _ALIAS_MAP:
                    out |= _ALIAS_MAP[k]

    # Normalize final set (strip empties)
    out = {normalize_term(x) for x in out if normalize_term(x)}
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
    """
    return meal_rejection_reason(meal, allergen_set, required_diet_tags=required_diet_tags) is None


def meal_rejection_reason(
    meal: Meal,
    allergen_set: set[str],
    required_diet_tags: set[str] | None = None,
) -> str | None:
    """
    Returns a deterministic reason string if meal is rejected; otherwise None.
    This keeps 'why rejected' centralized without changing API schema.
    """
    required_diet_tags = required_diet_tags or set()

    if not isinstance(meal, dict):
        return "Rejected: invalid_meal_non_dict"

    ingredients = meal.get("ingredients")
    if not isinstance(ingredients, list) or len(ingredients) == 0:
        return "Rejected: invalid_meal_missing_ingredients"

    for ing in ingredients:
        if not isinstance(ing, dict):
            return "Rejected: invalid_ingredient_non_dict"

        if ing.get("is_compound") is True:
            return "Rejected: invalid_ingredient_compound"

        contains = ing.get("contains")
        if not _contains_list_is_valid(contains):
            return "Rejected: invalid_contains_list"

        diet_tags = ing.get("diet_tags")
        if not _diet_tags_list_is_valid(diet_tags):
            return "Rejected: invalid_diet_tags_list"

        ing_tokens = {normalize_term(x) for x in contains}
        if "" in ing_tokens:
            return "Rejected: invalid_contains_empty_token"

        # HARD allergy rejection
        hit = sorted(list(ing_tokens & allergen_set))
        if hit:
            return f"Rejected: allergy_conflict blocked_by={hit}"

        ing_diet = {normalize_term(x) for x in diet_tags}
        if "" in ing_diet:
            return "Rejected: invalid_diet_tags_empty_token"

        # Diet enforcement (fail-closed)
        if required_diet_tags:
            if required_diet_tags == {"vegetarian"}:
                if not (("vegetarian" in ing_diet) or ("vegan" in ing_diet)):
                    return "Rejected: diet_conflict requires=vegetarian"
            else:
                if not required_diet_tags.issubset(ing_diet):
                    req = sorted(list(required_diet_tags))
                    return f"Rejected: diet_conflict requires={req}"

    return None


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
