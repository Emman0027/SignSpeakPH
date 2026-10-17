"""
Constants for SignSpeakPH deployment.

SIGN_INFO lists the signs deployed in production. Its labels MUST match
data/models/production/labels_<version>.json (tests/unit/test_signs.py checks
this). It feeds the "Learn the Signs" guide through GET /signs.
"""

# "description" is shown in the guide under each sign. It currently gives the
# meaning of the sign; add how to perform it later, checked against an FSL
# reference. An empty description is simply not shown.
SIGN_INFO = [
    {"label": "kamusta", "display": "Kamusta", "description": "Hello / How are you?"},
    {"label": "salamat", "display": "Salamat", "description": "Thank you"},
    {"label": "mahalkita", "display": "Mahalkita", "description": "I love you"},
    {"label": "oo", "display": "Oo", "description": "Yes"},
    {"label": "hindi", "display": "Hindi", "description": "No"},
]
