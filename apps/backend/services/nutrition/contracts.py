from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict, NotRequired


# Diet tags supported by the rules engine.
DietTag = Literal["vegan", "vegetarian", "pescatarian", "omnivore"]


class Ingredient(TypedDict):
    """
    FAIL-CLOSED CONTRACT (nutrition)

    Every ingredient MUST declare:
      - name: human-readable ingredient name
      - contains: canonical tokens used for allergen overlap checks
      - diet_tags: classification tags; used to guarantee vegan/vegetarian enforcement
      - is_compound: True if the ingredient is a composed food not decomposed into ingredients
    """
    name: str
    contains: list[str]
    diet_tags: list[DietTag]
    is_compound: bool


class Meal(TypedDict):
    """
    FAIL-CLOSED CONTRACT (nutrition)

    Every meal MUST declare:
      - name
      - ingredients: non-empty list of Ingredient objects
    """
    name: str
    ingredients: list[Ingredient]
