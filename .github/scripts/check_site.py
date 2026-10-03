"""CI checks for the Jekyll site: post front matter and image references."""
import re
import sys
from pathlib import Path

ALLOWED_CATEGORIES = {"technicalArticles", "nonTechnicalArticles"}
# Template demo posts are allowed to use their own categories.
SKIP_POSTS = {"2012-02-07-example-content.md"}
IMAGE_REF = re.compile(r"public/images/[A-Za-z0-9_./-]+\.(?:png|jpe?g|gif|svg|webp)")

errors = []

for post in sorted(Path("_posts").glob("*.md")):
    text = post.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append(f"{post}: missing front matter")
        continue
    front = dict(
        (k.strip(), v.strip())
        for k, _, v in (line.partition(":") for line in match.group(1).splitlines())
        if k.strip()
    )
    if post.name not in SKIP_POSTS:
        for key in ("layout", "title", "category"):
            if not front.get(key):
                errors.append(f"{post}: missing '{key}' in front matter")
        category = front.get("category")
        if category and category not in ALLOWED_CATEGORIES:
            errors.append(
                f"{post}: category '{category}' not in {sorted(ALLOWED_CATEGORIES)} "
                "(post would be missing from the Articles page)"
            )
    for ref in set(m.group(0) for m in IMAGE_REF.finditer(text)):
        if not Path(ref).is_file():
            errors.append(f"{post}: image not found: {ref}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("Front matter and image references OK")
