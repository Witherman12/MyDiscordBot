import ast
import pathlib
import re
import sys

SHORTCODE_RE = re.compile(r"^:[a-zA-Z0-9_+-]+:$")
VALID_CUSTOM_EMOJI_RE = re.compile(r"<a?:[a-zA-Z0-9_]+:\d{17,20}>")
IGNORE_DIRS = {".venv", "venv", "env", ".git", "__pycache__", ".vscode", ".ruff_cache"}

self_path = pathlib.Path(__file__).resolve()
errors = []

for path in pathlib.Path(".").rglob("*.py"):
    if path.resolve() == self_path or any(part in IGNORE_DIRS for part in path.parts):
        continue

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except Exception as e:
        errors.append(f"❌ {path}: Σφάλμα σύνταξης ({e})")
        continue

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value.strip()

            # 1. Πιάνει shortcodes τύπου ":japanese_ogre:"
            if SHORTCODE_RE.match(val):
                errors.append(
                    f"❌ {path} (γραμμή {node.lineno}): Βρέθηκε shortcode '{val}'. "
                    f"Βάλε το κανονικό Unicode emoji (π.χ. 👹) ή custom ID."
                )

            # 2. Πιάνει κακογραμμένα custom emojis (π.χ. λείπει '>' ή το ID)
            if ("<:" in val or "<a:" in val) and val not in ("<:", "<a:"):
                cleaned = VALID_CUSTOM_EMOJI_RE.sub("", val)
                if "<:" in cleaned or "<a:" in cleaned:
                    errors.append(
                        f"❌ {path} (γραμμή {node.lineno}): Χαλασμένο custom emoji -> {val[:60]}"
                    )

if errors:
    print("\n".join(errors))
    sys.exit(1)

print("✅ Όλα τα emojis είναι έγκυρα!")