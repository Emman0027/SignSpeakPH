path = "app.py"
content = open(path, encoding="utf-8").read()

if "import logging" in content:
    print("Already has logging import - no changes made.")
else:
    old = "import base64\nimport json\nimport os\nimport time"
    new = "import base64\nimport json\nimport logging\nimport os\nimport time\n\nlogging.basicConfig(level=logging.INFO)"
    if old in content:
        content = content.replace(old, new)
        open(path, "w", encoding="utf-8").write(content)
        print("Patched successfully - logging import added.")
    else:
        print("Could not find the expected import block - no changes made.")