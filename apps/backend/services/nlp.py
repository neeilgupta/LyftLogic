# apps/backend/services/nlp.py
import re

# Dictionary mapping common gym slang/abbreviations to standardized muscle names
# Example: "tris" -> "triceps", "delts" -> "shoulders"
ALIASES = {
    "tris":"triceps","tri":"triceps","bi":"biceps","hams":"hamstrings",
    "delts":"shoulders","rear delts":"rear_delts","calf":"calves"
}

# Set of all valid muscle groups that the system recognizes
# Used for validating parsed muscle names and ensuring consistency
MUSCLES = {
    "triceps","biceps","quads","hamstrings","glutes","chest",
    "back","shoulders","rear_delts","calves"
}

def parse_soreness(text: str) -> dict:
    """Process natural language soreness descriptions into structured data.
    
    Args:
        text (str): Natural language description of muscle soreness
                   Example: "triceps 3, quads 2" or "triceps are sore"
    
    Returns:
        dict: Mapping of muscle names to soreness levels (1-5 scale)
              Example: {'triceps':3, 'quads':2}
    
    Features:
    - Converts common aliases to standard names (e.g., "tris" -> "triceps")
    - Clamps soreness levels to 1-5 range
    - Default level 3 for muscles mentioned without a number
    - Ignores unrecognized muscle names
    """
    if not text:
        return {}
    t = text.lower()
    for k, v in ALIASES.items():
        t = t.replace(k, v)

    out = {}
    # e.g., "muscle 3", "muscle:3", "muscle = 4"
    for raw_muscle, level in re.findall(r'([a-z_ ]+?)\s*[:=\s]\s*([1-5])', t):
        m = raw_muscle.strip().replace(" ", "_")
        if m in MUSCLES:
            out[m] = max(1, min(5, int(level)))

    # pick up lone mentions
    for m in MUSCLES:
        if m in t and m not in out:
            out[m] = 3
    return out
