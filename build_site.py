import json
import os
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Lesson:
    source_ipynb: Path
    output_html: Path
    title: str
    section: str


ROOT = Path(__file__).resolve().parent
SITE_DIR = ROOT / "site"
LESSONS_DIR = SITE_DIR / "lessons"
ASSETS_DIR = SITE_DIR / "assets"


SECTION_RULES = [
    (re.compile(r"^numpy[\\/]", re.I), "NumPy"),
    (re.compile(r"^pandas[\\/]", re.I), "Pandas"),
    (re.compile(r"^Matplotlib[\\/]", re.I), "Matplotlib"),
    (re.compile(r"^scipy[\\/]", re.I), "SciPy"),
    (re.compile(r"^hands_on_ML[\\/]", re.I), "Hands-On ML"),
    (re.compile(r"^ML by andrew NG[\\/]", re.I), "Andrew Ng (Notes)"),
    (re.compile(r"^lab3[\\/]", re.I), "Experiments"),
]


def discover_ipynb() -> list[Path]:
    ipynbs: list[Path] = []
    for p in ROOT.rglob("*.ipynb"):
        # skip any generated/temporary locations
        if "site" in p.parts:
            continue
        if ".ipynb_checkpoints" in p.parts:
            continue
        ipynbs.append(p)
    return sorted(ipynbs, key=lambda x: str(x).lower())


def classify_section(rel_path: str) -> str:
    for rx, section in SECTION_RULES:
        if rx.search(rel_path):
            return section
    return "Notebooks"


def notebook_title(ipynb_path: Path) -> str:
    # Try to read notebook metadata.title if present, else use filename.
    try:
        data = json.loads(ipynb_path.read_text(encoding="utf-8"))
        md = data.get("metadata", {}) or {}
        title = md.get("title")
        if isinstance(title, str) and title.strip():
            return title.strip()
    except Exception:
        pass
    return ipynb_path.stem


def safe_slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "lesson"


def ensure_dirs() -> None:
    SITE_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)
    LESSONS_DIR.mkdir(exist_ok=True)


def convert_notebook(ipynb: Path, out_html: Path) -> None:
    import nbformat
    from nbconvert import HTMLExporter

    nb = nbformat.read(ipynb, as_version=4)
    exporter = HTMLExporter()
    exporter.template_name = "lab"
    body, _resources = exporter.from_notebook_node(nb)

    # Make relative resources (images) resolve from the notebook's folder.
    # We set <base href> to the notebook's directory relative to site/index.html.
    rel_to_root = ipynb.parent.relative_to(ROOT).as_posix()
    base_href = "../" * (out_html.relative_to(SITE_DIR).parts.__len__() - 1)
    # base to repo root, then to notebook folder
    base_href = (base_href + rel_to_root + "/").replace("//", "/")

    wrapped = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <base href="{base_href}">
  <title>{escape_html(notebook_title(ipynb))}</title>
  <link rel="stylesheet" href="../assets/theme.css" />
</head>
<body class="nb-page">
  <div class="nb-wrap">
    {body}
  </div>
</body>
</html>
"""
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(wrapped, encoding="utf-8")


def escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def build_lessons(ipynbs: list[Path]) -> list[Lesson]:
    lessons: list[Lesson] = []
    for nb in ipynbs:
        rel = nb.relative_to(ROOT).as_posix()
        section = classify_section(rel.replace("/", os.sep).replace("\\", os.sep))
        title = notebook_title(nb)

        out_dir = LESSONS_DIR / safe_slug(section)
        out_file = out_dir / f"{safe_slug(title)}.html"
        lessons.append(Lesson(source_ipynb=nb, output_html=out_file, title=title, section=section))
    return lessons


def write_index(lessons: list[Lesson]) -> None:
    sections: dict[str, list[Lesson]] = {}
    for l in lessons:
        sections.setdefault(l.section, []).append(l)

    section_order = [s for _rx, s in SECTION_RULES] + ["Notebooks"]
    ordered_sections = [s for s in section_order if s in sections] + [s for s in sections.keys() if s not in section_order]

    # default lesson to load
    default_href = None
    for s in ordered_sections:
        if sections[s]:
            default_href = sections[s][0].output_html.relative_to(SITE_DIR).as_posix()
            break

    nav_html = []
    for sec in ordered_sections:
        nav_html.append(f'<div class="nav-section"><div class="nav-caption">{escape_html(sec)}</div>')
        for l in sections[sec]:
            href = l.output_html.relative_to(SITE_DIR).as_posix()
            nav_html.append(
                f'<button class="nav-item" data-href="{escape_html(href)}">{escape_html(l.title)}</button>'
            )
        nav_html.append("</div>")

    default_href = default_href or ""

    index = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Data Science Journey</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/theme.css" />
</head>
<body class="app">
  <div class="scanlines" aria-hidden="true"></div>

  <header class="topbar">
    <div class="brand">
      <div class="brand-title">// DATA_SCIENCE_JOURNEY</div>
      <div class="brand-sub">notebook-first • built from .ipynb • open in browser</div>
    </div>
    <div class="topbar-actions">
      <button class="btn" id="btn-rebuild" title="Re-run build_site.py">rebuild_site</button>
      <a class="btn ghost" href="https://github.com/Manireddy69/Data-science" target="_blank" rel="noopener">repo</a>
    </div>
  </header>

  <main class="layout">
    <aside class="sidebar">
      <div class="sidebar-head">course_index</div>
      <div class="nav">
        {''.join(nav_html)}
      </div>
      <div class="sidebar-foot">
        <div>lessons: <span class="accent">{len(lessons)}</span></div>
        <div class="dim">tip: click a lesson to open</div>
      </div>
    </aside>

    <section class="viewer">
      <div class="viewer-head">
        <div class="viewer-title" id="viewer-title">loading...</div>
        <div class="viewer-path dim" id="viewer-path"></div>
      </div>
      <iframe class="frame" id="frame" src="{escape_html(default_href)}" title="lesson viewer"></iframe>
    </section>
  </main>

  <script>
    const DEFAULT = {json.dumps(default_href)};
    const buttons = Array.from(document.querySelectorAll('.nav-item'));
    const frame = document.getElementById('frame');
    const titleEl = document.getElementById('viewer-title');
    const pathEl = document.getElementById('viewer-path');

    function setActive(btn) {{
      buttons.forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
    }}

    function openLesson(btn) {{
      const href = btn.dataset.href;
      frame.src = href;
      titleEl.textContent = btn.textContent;
      pathEl.textContent = href;
      setActive(btn);
      localStorage.setItem('dsj:last', href);
    }}

    buttons.forEach(btn => btn.addEventListener('click', () => openLesson(btn)));

    // restore last opened lesson
    const last = localStorage.getItem('dsj:last');
    const initial = last || DEFAULT;
    const initialBtn = buttons.find(b => b.dataset.href === initial) || buttons[0];
    if (initialBtn) openLesson(initialBtn);

    // rebuild button: just explains what to run (static site)
    document.getElementById('btn-rebuild').addEventListener('click', () => {{
      alert('To rebuild the site, run:\\n\\n  py build_site.py\\n\\nThen refresh this page.');
    }});
  </script>
</body>
</html>
"""
    (SITE_DIR / "index.html").write_text(index, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    ipynbs = discover_ipynb()
    lessons = build_lessons(ipynbs)

    for l in lessons:
        convert_notebook(l.source_ipynb, l.output_html)

    write_index(lessons)
    print(f"Built {len(lessons)} lessons into: {SITE_DIR}")
    print(f"Open: {SITE_DIR / 'index.html'}")


if __name__ == "__main__":
    main()

