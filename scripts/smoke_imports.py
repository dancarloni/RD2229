import importlib

modules = [
    "app.domain.models",
    "app.domain.sections",
    "app.domain.materials",
    "app.verification.dispatcher",
    "app.verification.methods_ta",
]
for m in modules:
    importlib.import_module(m)
print("IMPORTS_OK")
