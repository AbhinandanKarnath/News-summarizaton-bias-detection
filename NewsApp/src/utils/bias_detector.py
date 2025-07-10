import re

# Example bias keywords and types
BIAS_KEYWORDS = {
    'Political': [
        'left-wing', 'right-wing', 'liberal', 'conservative', 'bjp', 'congress', 'modi', 'rahul gandhi',
        'hindutva', 'secular', 'communal', 'propaganda', 'agenda', 'nationalist', 'fascist', 'commie',
        'sanghi', 'bhakt', 'tukde tukde', 'urban naxal', 'islamist', 'muslim appeasement', 'anti-national',
        'patriot', 'traitor', 'dynasty', 'godi media', 'presstitute', 'fake news', 'mainstream media'
    ],
    'Religious': [
        'hindu', 'muslim', 'christian', 'islam', 'temple', 'mosque', 'church', 'communal', 'religious',
        'minority', 'majority', 'dalit', 'caste', 'reservation', 'conversion', 'cow vigilante', 'lynching'
    ],
    'Loaded Language': [
        'shocking', 'outrage', 'slam', 'blast', 'attack', 'expose', 'scam', 'controversy', 'uproar',
        'sensational', 'alleged', 'accused', 'claimed', 'reportedly', 'sources say', 'unverified',
        'massive', 'huge', 'unprecedented', 'disaster', 'crisis', 'catastrophe', 'disgrace', 'failure'
    ],
    'Gender': [
        'feminist', 'patriarchy', 'gender bias', 'sexist', 'misogynist', 'womanizer', 'eve-teasing',
        'molestation', 'rape', 'victim blaming', 'empowerment', 'glass ceiling'
    ]
}

# Flatten all keywords for quick search
ALL_BIAS_KEYWORDS = [(typ, kw) for typ, kws in BIAS_KEYWORDS.items() for kw in kws]


def detect_bias(text):
    """
    Detects bias in the given text. Returns a bias_score (0-1) and a list of bias_types found.
    """
    if not text or not isinstance(text, str):
        return 0.0, []
    text_lower = text.lower()
    found_types = set()
    found_keywords = 0
    for bias_type, keyword in ALL_BIAS_KEYWORDS:
        # Use word boundaries for whole word match
        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
            found_types.add(bias_type)
            found_keywords += 1
    # Score: fraction of unique types found, weighted by keyword count
    bias_score = min(1.0, (len(found_types) + found_keywords / 10) / (len(BIAS_KEYWORDS) + 1))
    return round(bias_score, 2), sorted(found_types)

# Example usage
if __name__ == "__main__":
    sample = "The left-wing media slammed the government in a shocking expose."
    score, types = detect_bias(sample)
    print(f"Bias Score: {score}, Types: {types}") 