path = "app.py"
content = open(path, encoding="utf-8").read()

old = "import tflite_runtime.interpreter as tflite"
new = (
    "try:\n"
    "    import tflite_runtime.interpreter as tflite\n"
    "except ModuleNotFoundError:\n"
    "    import tensorflow as tf\n"
    "    tflite = tf.lite\n"
    "    print(\"[info] tflite_runtime not found - using tensorflow.lite.Interpreter instead (fine for local testing)\")"
)

if "except ModuleNotFoundError" in content:
    print("Already patched - no changes made.")
elif old in content:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("Patched successfully.")
else:
    print("Could not find the expected import line - no changes made.")