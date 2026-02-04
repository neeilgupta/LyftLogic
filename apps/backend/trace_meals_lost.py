#!/usr/bin/env python3
"""
TRACE WHERE MEALS ARE BEING LOST

This will add debug prints to trace the flow through generate_stub_meals.
Add these prints to your stub_meals.py temporarily to debug.
"""

print("""
Add these debug prints to your generate_stub_meals function:

After line where diet_candidates is created:
    print(f"DEBUG: diet_candidates count: {len(diet_candidates)}")

After line where candidates is created:
    print(f"DEBUG: candidates count (after allergy filter): {len(candidates)}")

After line where picked is created:
    print(f"DEBUG: picked count (after slot selection): {len(picked)}")

After line where out_meals is created:
    print(f"DEBUG: out_meals count (before returning): {len(out_meals)}")

Then run your test again and you'll see where meals are being lost.
""")

# Also create a standalone test
import sys
sys.path.insert(0, '.')

try:
    from services.nutrition.stub_meals import generate_stub_meals
    
    class MockReq:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    print("\n" + "="*70)
    print("STANDALONE TEST")
    print("="*70)
    
    req = MockReq(
        diet="pescatarian",
        allergies=[],
        target_calories=2600,
        calories=2600,
        targets={"maintenance": 2600},
        meals_needed=0,
        batch_size=0
    )
    
    print(f"\nCalling generate_stub_meals with:")
    print(f"  diet: pescatarian")
    print(f"  allergies: []")
    print(f"  target_calories: 2600")
    print(f"  meals_needed: 0 (infer)")
    print()
    
    result = generate_stub_meals(req, attempt=1)
    
    print(f"\nResults:")
    print(f"  Meals generated: {len(result['meals'])}")
    print(f"  Total calories: {result['totals']['calories']}")
    print(f"  Meta candidate_count: {result['meta']['candidate_count']}")
    print(f"  Meta diet_required: {result['meta']['diet_required']}")
    
    if len(result['meals']) == 0:
        print("\n❌ PROBLEM: No meals generated!")
        print("\nPossible causes:")
        print("1. Allergy filter removing all candidates")
        print("2. Slot selection not finding matches")
        print("3. Some post-processing removing meals")
    else:
        print("\n✓ SUCCESS: Meals generated!")
        print("\nSample meals:")
        for m in result['meals'][:3]:
            print(f"  - {m['name']} ({m['macros']['calories']} cal)")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()