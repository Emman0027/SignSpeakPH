"""
Constants for SignSpeakPH deployment.

SIGN_INFO lists the signs deployed in production. Its labels MUST match
data/models/production/labels_<version>.json (tests/unit/test_signs.py checks
this, including the ORDER). It feeds the "Learn the Signs" guide through
GET /signs.
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
    {"label": "sino", "display": "Sino", "description": "Who"},
    {"label": "saan", "display": "Saan", "description": "Where"},
    {"label": "ulitin", "display": "Ulitin", "description": "Repeat / Again"},
    {"label": "please", "display": "Please", "description": "Please"},
    {"label": "paalam", "display": "Paalam", "description": "Goodbye"},
    {"label": "tulong", "display": "Tulong", "description": "Help"},
    {
        "label": "walang_anuman",
        "display": "Walang Anuman",
        "description": "You're welcome",
    },
    {"label": "ingat", "display": "Ingat", "description": "Take care"},
    {"label": "gusto", "display": "Gusto", "description": "Want"},
    {"label": "hindi_gusto", "display": "Hindi Gusto", "description": "Don't want"},
    {"label": "tulog", "display": "Tulog", "description": "Sleep"},
    {"label": "masaya", "display": "Masaya", "description": "Happy"},
    {"label": "takot", "display": "Takot", "description": "Scared"},
    {"label": "CR", "display": "CR / Toilet", "description": "Comfort room / Toilet"},
    {"label": "pera", "display": "Pera", "description": "Money"},
    {"label": "nanay", "display": "Nanay", "description": "Mother"},
    {"label": "tatay", "display": "Tatay", "description": "Father"},
]
