#!/usr/bin/env python3
"""
Verify the fix was applied correctly in stub_meals.py
"""

import sys

print("="*70)
print("VERIFICATION: Check if fix was applied correctly")
print("="*70)

# Read the actual file
try:
    with open('services/nutrition/stub_meals.py', 'r') as f:
        content = f.read()
    
    print("\n1. Checking for _meal_passes_diet function...")
    if 'def _meal_passes_diet(meal: dict) -> bool:' in content:
        print("   ✓ Found _meal_passes_diet function")
    else:
        print("   ❌ MISSING _meal_passes_diet function")
    
    print("\n2. Checking for diet_candidates list...")
    if 'diet_candidates = [m for m in MEAL_LIBRARY if _meal_passes_diet(m)]' in content:
        print("   ✓ Found diet_candidates list comprehension")
    else:
        print("   ❌ MISSING diet_candidates list comprehension")
    
    print("\n3. Checking for fail-closed check...")
    if 'if diet and not diet_candidates:' in content:
        print("   ✓ Found fail-closed check")
    else:
        print("   ❌ MISSING fail-closed check")
    
    print("\n4. Checking for pool variable...")
    if 'pool = diet_candidates if diet else MEAL_LIBRARY' in content:
        print("   ✓ Found pool variable")
    else:
        print("   ❌ MISSING pool variable")
    
    print("\n5. Checking that loop uses pool not MEAL_LIBRARY...")
    # Find the candidates_by_key section
    import re
    pattern = r'candidates_by_key:.*?=.*?\{\}.*?for m in (\w+):'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        var_used = match.group(1)
        if var_used == 'pool':
            print(f"   ✓ Loop uses 'pool' variable")
        else:
            print(f"   ❌ Loop uses '{var_used}' instead of 'pool'")
    else:
        print("   ❌ Could not find candidates_by_key loop")
    
    print("\n6. Checking debug function was removed...")
    if '_debug_diet_rejections' in content:
        print("   ❌ WARNING: _debug_diet_rejections still present")
    else:
        print("   ✓ _debug_diet_rejections removed")
    
    print("\n7. Checking _diet_required_tags for pescatarian...")
    pattern = r'if d == "pescatarian":\s*return \{([^}]+)\}'
    match = re.search(pattern, content)
    if match:
        tags = match.group(1)
        if 'pescatarian' in tags and 'vegetarian' in tags and 'vegan' in tags:
            print(f"   ✓ Pescatarian returns all 3 tags")
        else:
            print(f"   ❌ Pescatarian tags incomplete: {tags}")
    else:
        print("   ❌ Could not find pescatarian case")
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    # Count issues
    issues = []
    if 'def _meal_passes_diet(meal: dict) -> bool:' not in content:
        issues.append("Missing _meal_passes_diet function")
    if 'diet_candidates = [m for m in MEAL_LIBRARY if _meal_passes_diet(m)]' not in content:
        issues.append("Missing diet_candidates list")
    if 'pool = diet_candidates if diet else MEAL_LIBRARY' not in content:
        issues.append("Missing pool variable")
    
    if issues:
        print("❌ FIX NOT FULLY APPLIED!")
        print("\nMissing components:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ All fix components present")
        print("\nIf test still fails, the issue is elsewhere in the code flow.")

except FileNotFoundError:
    print("❌ Could not find services/nutrition/stub_meals.py")
    print("Make sure you're running this from the backend directory")
except Exception as e:
    print(f"❌ Error: {e}")