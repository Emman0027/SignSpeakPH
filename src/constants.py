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
    {
        "label": "kamusta",
        "gif": "/static/gifs/kumusta.gif",
        "display": "Kamusta",
        "description": "Hello / How are you?",
    },
    {
        "label": "salamat",
        "gif": "/static/gifs/salamat.gif",
        "display": "Salamat",
        "description": "Thank you",
    },
    {
        "label": "mahalkita",
        "gif": "/static/gifs/mahalkita.gif",
        "display": "Mahalkita",
        "description": "I love you",
    },
    {
        "label": "oo",
        "gif": "/static/gifs/oo.gif",
        "display": "Oo",
        "description": "Yes",
    },
    {
        "label": "hindi",
        "gif": "/static/gifs/hindi.gif",
        "display": "Hindi",
        "description": "No",
    },
    {
        "label": "sino",
        "gif": "/static/gifs/sino.gif",
        "display": "Sino",
        "description": "Who",
    },
    {
        "label": "saan",
        "gif": "/static/gifs/saan.gif",
        "display": "Saan",
        "description": "Where",
    },
    {"label": "ulitin", "display": "Ulitin", "description": "Repeat / Again"},
    {
        "label": "pakiusap",
        "gif": "/static/gifs/pakiusap.gif",
        "display": "Pakiusap",
        "description": "Please",
    },  # was "please"
    {
        "label": "paalam",
        "gif": "/static/gifs/paalam.gif",
        "display": "Paalam",
        "description": "Goodbye",
    },
    {
        "label": "tulong",
        "gif": "/static/gifs/tulong.gif",
        "display": "Tulong",
        "description": "Help",
    },
    {
        "label": "walang_anuman",
        "gif": "/static/gifs/walang_anuman.gif",
        "display": "Walang Anuman",
        "description": "You're welcome",
    },
    {
        "label": "malungkot",
        "gif": "/static/gifs/malungkot.gif",
        "display": "Malungkot",
        "description": "Sad",
    },  # was "ingat" (Take care)
    {
        "label": "gusto",
        "gif": "/static/gifs/gusto.gif",
        "display": "Gusto",
        "description": "Want",
    },
    {
        "label": "hindi_gusto",
        "gif": "/static/gifs/hindi_gusto.gif",
        "display": "Hindi Gusto",
        "description": "Don't want",
    },
    {
        "label": "tulog",
        "gif": "/static/gifs/tulog.gif",
        "display": "Tulog",
        "description": "Sleep",
    },
    {
        "label": "masaya",
        "gif": "/static/gifs/masaya.gif",
        "display": "Masaya",
        "description": "Happy",
    },
    {
        "label": "takot",
        "gif": "/static/gifs/takot.gif",
        "display": "Takot",
        "description": "Scared",
    },
    {
        "label": "patawad",
        "gif": "/static/gifs/patawad.gif",
        "display": "Patawad",
        "description": "Sorry / Forgive me",
    },  # was "CR"
    {
        "label": "pera",
        "gif": "/static/gifs/pera.gif",
        "display": "Pera",
        "description": "Money",
    },
    {
        "label": "nanay",
        "gif": "/static/gifs/nanay.gif",
        "display": "Nanay",
        "description": "Mother",
    },
    {
        "label": "tatay",
        "gif": "/static/gifs/tatay.gif",
        "display": "Tatay",
        "description": "Father",
    },
]
