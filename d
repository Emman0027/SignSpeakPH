[1mdiff --git a/app.py b/app.py[m
[1mindex 5478fe5..5dd64a3 100644[m
[1m--- a/app.py[m
[1m+++ b/app.py[m
[36m@@ -92,6 +92,7 @@[m [mfrom src.config.settings import ([m
     SEQUENCE_LENGTH,[m
     THRESHOLD,[m
 )[m
[32m+[m[32mfrom src.constants import SIGN_INFO[m
 from src.utils.mediapipe_utils import create_models  # noqa: E402[m
 from src.utils.mediapipe_utils import extract_keypoints, mediapipe_detection[m
 [m
[36m@@ -204,6 +205,14 @@[m [mdef get_config():[m
     return jsonify({"threshold": THRESHOLD}), 200[m
 [m
 [m
[32m+[m[32m@app.route("/signs")[m
[32m+[m[32m@limiter.exempt[m
[32m+[m[32mdef get_signs():[m
[32m+[m[32m    """Sign vocabulary for the 'Learn the Signs' guide in templates/index.html.[m
[32m+[m[32m    Exempt from rate limiting because the guide loads it on demand."""[m
[32m+[m[32m    return jsonify(SIGN_INFO), 200[m
[32m+[m
[32m+[m
 @app.route("/predict_batch", methods=["POST"])[m
 def predict_batch():[m
     """[m
[36m@@ -435,6 +444,42 @@[m [mdef metrics():[m
     return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}[m
 [m
 [m
[32m+[m[32m@app.route("/signs")[m
[32m+[m[32mdef get_signs():[m
[32m+[m[32m    """Return sign language guide data for the sign modal."""[m
[32m+[m[32m    # Map of sign labels to their display names and descriptions[m
[32m+[m[32m    signs_data = {[m
[32m+[m[32m        "kamusta": {[m
[32m+[m[32m            "display": "Kamusta",[m
[32m+[m[32m            "description": "Hello / How are you?"[m
[32m+[m[32m        },[m
[32m+[m[32m        "salamat": {[m
[32m+[m[32m            "display": "Salamat",[m
[32m+[m[32m            "description": "Thank you"[m
[32m+[m[32m        },[m
[32m+[m[32m        "mahalkita": {[m
[32m+[m[32m            "display": "Mahalkita",[m
[32m+[m[32m            "description": "I love you"[m
[32m+[m[32m        },[m
[32m+[m[32m        "oo": {[m
[32m+[m[32m            "display": "Oo",[m
[32m+[m[32m            "description": "Yes"[m
[32m+[m[32m        },[m
[32m+[m[32m        "hindi": {[m
[32m+[m[32m            "display": "Hindi",[m
[32m+[m[32m            "description": "No"[m
[32m+[m[32m        }[m
[32m+[m[32m    }[m
[32m+[m
[32m+[m[32m    # Convert to list format expected by frontend[m
[32m+[m[32m    signs_list = [[m
[32m+[m[32m        {"display": data["display"], "description": data["description"]}[m
[32m+[m[32m        for label, data in signs_data.items()[m
[32m+[m[32m    ][m
[32m+[m
[32m+[m[32m    return jsonify(signs_list)[m
[32m+[m
[32m+[m
 if __name__ == "__main__":[m
     port = int(os.environ.get("PORT", 5000))[m
     app.run(host="0.0.0.0", port=port, debug=False)[m
