import re
from pathlib import Path

for svg_file in ["static/images/hero5.svg", "static/images/hero6.svg"]:
    try:
        content = Path(svg_file).read_text(encoding="utf-8")
        colors = set(re.findall(r'#[A-Fa-f0-9]{6}', content))
        print(svg_file, [c for c in colors if re.match(r'#([Ff][0-9A-Fa-f]{5}|[Ee][0-9A-Fa-f]{5})', c)])
    except Exception as e:
        print(f"Error reading {svg_file}: {e}")
