#!/usr/bin/env python3
"""
DETAILED PESCATARIAN DIAGNOSTIC

This will show you EXACTLY what's happening with tag matching.
Run in your backend directory: python3 debug_pescatarian_detailed.py
"""

import sys
sys.path.insert(0, "backend")  # if you run from repo root
from services.nutrition.meal_library import MEAL_LIBRARY


# Test the EXACT code from stub_meals.py
required = {"pescatarian", "vegetarian", "vegan"}

print("="*70)
print("PESCATARIAN FILTER DIAGNOSTIC")
print("="*70)
print(f"Required tags (from _diet_required_tags): {required}")
print(f"Total meals in library: {len(MEAL_LIBRARY)}")
print()

# Collect all unique diet tags used in the library
all_tags = set()
for m in MEAL_LIBRARY:
    for ing in m.get("ingredients", []):
        for tag in ing.get("diet_tags", []):
            all_tags.add(str(tag).lower())

print(f"All unique diet_tags found in library: {sorted(all_tags)}")
print()

# Test each meal
passing = []
failing = []

for m in MEAL_LIBRARY:
    meal_pass = True
    bad_ingredients = []
    
    for ing in m.get("ingredients", []):
        tags = set(t.lower() for t in (ing.get("diet_tags") or []))
        
        # Check if this ingredient is compatible
        if tags.isdisjoint(required):  # NO overlap = bad
            meal_pass = False
            bad_ingredients.append((ing.get("name"), list(tags)))
    
    if meal_pass:
        passing.append(m)
    else:
        failing.append((m, bad_ingredients))

print(f"Results:")
print(f"  ✓ PASSING: {len(passing)} meals")
print(f"  ✗ FAILING: {len(failing)} meals")
print()

if len(passing) == 0:
    print("❌ CRITICAL: NO MEALS PASSING!")
    print()
    print("This means your fix is working, but there's a tag mismatch.")
    print()
    print("Sample failing meals:")
    for m, bad_ings in failing[:3]:
        print(f"\n  Meal: {m['name']}")
        print(f"  Key: {m['key']}")
        for ing_name, ing_tags in bad_ings[:2]:
            print(f"    ✗ {ing_name}")
            print(f"      Has tags: {ing_tags}")
            print(f"      Required: one of {required}")
            print(f"      Intersection: {set(ing_tags) & required}")
    
    print("\n" + "="*70)
    print("SOLUTION:")
    print("="*70)
    print("The issue is that ingredient tags don't match the required set.")
    print()
    print("Check if tags are using different values, like:")
    print("  - 'omnivore' instead of 'pescatarian'?")
    print("  - Missing tags entirely?")
    print("  - Extra whitespace or capitalization?")
    print()
    print("Look at services/nutrition/meal_library.py and verify:")
    print("  1. Fish ingredients have: diet_tags=['pescatarian']")
    print("  2. Egg/dairy ingredients have: diet_tags=['vegetarian']") 
    print("  3. Plant ingredients have: diet_tags=['vegan']")
    
else:
    print("✓ SUCCESS: Filter is working correctly!")
    print()
    print("Sample passing meals:")
    for m in passing[:5]:
        print(f"  ✓ {m['key']}: {m['name']}")

print()
print("="*70)
print("TAG COMPATIBILITY CHECK")
print("="*70)
print(f"Required: {required}")
print(f"Found in library: {sorted(all_tags)}")
print(f"Overlap: {required & all_tags}")
print(f"Missing: {required - all_tags}")

if required & all_tags != required:
    print()
    print("⚠️  WARNING: Some required tags are not found in the library!")
    print("This will cause ALL meals to be rejected.")