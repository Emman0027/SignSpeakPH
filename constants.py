"""
Constants for the SignSpeakPH application.
"""

# Display names and how-to descriptions for the sign guide UI. Keyed by the
# exact slug used in labels.json/actions. Add/edit entries here as you
# refine your sign set - the /signs endpoint only returns entries that
# actually exist in ACTIONS, so this dict can safely contain more (e.g.
# signs from other branches) without causing problems.
SIGN_INFO = {
    "kamusta": {"display": "Kamusta", "description": "Description not yet added - edit SIGN_INFO in app.py."},
    "salamat": {"display": "Salamat", "description": "Description not yet added - edit SIGN_INFO in app.py."},
    "mahalkita": {"display": "Mahal Kita", "description": "Description not yet added - edit SIGN_INFO in app.py."},
    "oo": {"display": "Oo", "description": "Description not yet added - edit SIGN_INFO in app.py."},
    "hindi": {"display": "Hindi", "description": "Description not yet added - edit SIGN_INFO in app.py."},
    "sino": {"display": "Sino", "description": "Itapat ang hinlalaki sa iyong baba habang ang hintuturo ay nakaturo pataas, pagkatapos ay i-kurba o i-galaw ang hintuturo nang paulit-ulit na parang tuka ng ibon."},
    "saan": {"display": "Saan", "description": "Itaas ang hintuturo (index finger) at i-kaway ito pakaliwa't kanan nang paulit-ulit na parang may hinahanap."},
    "ulitin": {"display": "Ulitin", "description": "I-latag nang patag ang kaliwang palad na nakaharap pataas. Gamit ang kanang kamay na naka-kurba ang mga daliri, i-untog o itama ang mga dulo nito sa gitna ng kaliwang palad."},
    "please": {"display": "Please", "description": "Buksan ang kanang palad at i-ikot ito nang pabilog sa gitna ng iyong dibdib."},
    "paalam": {"display": "Paalam", "description": "Itaas ang kamay na nakabuka ang palad at i-kaway ang mga daliri pababa at pataas (normal na pagkaway)."},
    "tulong": {"display": "Tulong", "description": "I-latag nang patag ang kaliwang palad. Ipatong dito ang kanang kamay na naka-kamao habang ang hinlalaki ay nakaturo pataas, pagkatapos ay sabay silang i-angat nang bahagya."},
    "walang_anuman": {"display": "Walang Anuman", "description": "Pagkatapos magpasalamat, i-bow nang bahagya ang ulo kasabay ng pagngiti, o gawin muli ang sign ng \"Salamat.\""},
    "ingat": {"display": "Ingat", "description": "I-krus o ipatong ang dalawang kamay na naka-\"K\" sign (hintuturo at gitnang daliri) sa ibabaw ng isa't isa."},
    "gusto": {"display": "Gusto", "description": "Itapat ang dalawang palad nang nakatingala, itiklop nang bahagya ang mga daliri habang hinihila palapit sa katawan."},
    "hindi_gusto": {"display": "Hindi Gusto", "description": "Gawin ang sign ng \"Gusto\" pero iikot ang mga palad pababa palayo sa katawan na parang nagtatapon."},
    "tulog": {"display": "Tulog", "description": "Buksan ang palad sa tapat ng mukha, sabay ibaba ito habang dahan-dahang ipinikit ang mga mata at itinikom ang kamay sa baba."},
    "masaya": {"display": "Masaya", "description": "Ipatong ang isa o dalawang palad sa dibdib at igalaw ito nang pabilog pataas nang mabilis habang nakangiti."},
    "takot": {"display": "Takot", "description": "Buksan ang dalawang kamay sa tapat ng dibdib at i-shake ito nang mabilis pabalik-balik na parang nanginginig sa takot."},
    "CR": {"display": "CR / Toilet", "description": "Isara ang kamay habang nakasingit ang thumb sa pagitan ng hintuturo at gitnang daliri (hugis \"T\"), tapos i-shake ito."},
    "pera": {"display": "Pera / Money", "description": "I-kuskos ang thumb sa hintuturo at gitnang daliri (parang nagbibilang ng barya)."},
    "ina": {"display": "Ina / Mother", "description": "I-buka ang palad at i-tap ang dulo ng hinlalaki sa iyong baba nang paulit-ulit."},
    "ama": {"display": "Ama / Father", "description": "I-buka ang palad at i-tap ang dulo ng hinlalaki sa iyong noo nang paulit-ulit."},
}