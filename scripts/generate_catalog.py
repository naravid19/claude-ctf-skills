#!/usr/bin/env python3
"""Generate a modern, responsive static HTML skill catalog for GitHub Pages.

Enforces Terminal Cyber Dark aesthetic, interactive instant search,
category filtering, and showcases both technique docs and exploit scripts.
"""

import html
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "_site"

_DEFAULT_REPO_URL = "https://github.com/naravid19/claude-ctf-skills"


def _detect_repo_url() -> str:
    """Derive the GitHub repo URL from the git remote, with fallback."""
    try:
        url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if url.startswith("ssh://"):
            url = url.replace("ssh://", "https://", 1).replace("git@", "")
        elif url.startswith("git@"):
            url = url.replace("git@", "https://", 1).replace(":", "/", 1)
        url = url.removesuffix(".git")
        return url
    except (subprocess.CalledProcessError, FileNotFoundError):
        return _DEFAULT_REPO_URL


_repo_url: str | None = None


def _get_repo_url() -> str:
    global _repo_url
    if _repo_url is None:
        _repo_url = _detect_repo_url()
    return _repo_url


CATEGORY_COLORS = {
    "ctf-web": "#0ea5e9",  # Sky Cyan
    "ctf-pwn": "#f97316",  # Orange Red
    "ctf-crypto": "#10b981",  # Emerald
    "ctf-reverse": "#8b5cf6",  # Violet
    "ctf-forensics": "#06b6d4",  # Cyan
    "ctf-osint": "#eab308",  # Amber
    "ctf-malware": "#ef4444",  # Crimson
    "ctf-misc": "#6366f1",  # Indigo
    "ctf-ai-ml": "#ec4899",  # Rose Pink
    "ctf-writeup": "#94a3b8",  # Slate
    "solve-challenge": "#14b8a6",  # Teal
}

CATEGORY_ICONS = {
    "ctf-web": "🌐",
    "ctf-pwn": "💣",
    "ctf-crypto": "🔐",
    "ctf-reverse": "🔬",
    "ctf-forensics": "🔍",
    "ctf-osint": "🌍",
    "ctf-malware": "🦠",
    "ctf-misc": "🧩",
    "ctf-ai-ml": "🤖",
    "ctf-writeup": "📝",
    "solve-challenge": "🎯",
}


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse YAML frontmatter into a flat dict."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return {}
    result: dict[str, str] = {}
    block: str | None = None
    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.endswith(":") and ":" not in stripped[:-1]:
            block = stripped[:-1]
            continue
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip().strip('"')
        if block:
            result[f"{block}.{key}"] = value
        else:
            result[key] = value
    return result


def discover_skills() -> list[Path]:
    """Find all directories containing a SKILL.md."""
    skills_dir = REPO_ROOT / "skills"
    if skills_dir.is_dir():
        skills = sorted(p.parent for p in skills_dir.glob("*/SKILL.md"))
        if skills:
            return skills
    return sorted(p.parent for p in REPO_ROOT.glob("*/SKILL.md"))


def count_techniques(skill_dir: Path) -> list[dict[str, str]]:
    """List technique files in a skill directory."""
    techniques = []
    for md in sorted(skill_dir.glob("*.md")):
        if md.name == "SKILL.md":
            continue
        name = md.stem.replace("-", " ").replace("_", " ").title()
        techniques.append({"name": name, "file": md.name})
    return techniques


def count_scripts(skill_dir: Path) -> list[dict[str, str]]:
    """List executable python scripts in a skill's scripts/ directory."""
    scripts_dir = skill_dir / "scripts"
    scripts = []
    if scripts_dir.is_dir():
        for py in sorted(scripts_dir.glob("*.py")):
            scripts.append({"name": py.name, "file": f"scripts/{py.name}"})
    return scripts


def build_html(skills: list[dict]) -> str:
    """Build the modern Terminal Cyber Dark HTML catalog page."""
    total_techniques = sum(len(s.get("techniques", [])) for s in skills)
    total_scripts = sum(len(s.get("scripts", [])) for s in skills)
    total_categories = len(skills)
    repo = _get_repo_url()

    cards = []
    for s in skills:
        color = CATEGORY_COLORS.get(s["dir_name"], "#64748b")
        icon = html.escape(CATEGORY_ICONS.get(s["dir_name"], "📄"))
        techs = s.get("techniques", [])
        scripts = s.get("scripts", [])
        tech_count = len(techs)
        script_count = len(scripts)
        desc = html.escape(s.get("description", ""))
        rel_path = s.get("rel_path", s["dir_name"])
        skill_link = f"{repo}/blob/main/{rel_path}/SKILL.md"

        # Technique badges
        tech_items = []
        for t in techs:
            gh_link = f"{repo}/blob/main/{rel_path}/{t['file']}"
            label = html.escape(t["name"])
            tech_items.append(
                f'<li class="tech-item"><a href="{gh_link}" target="_blank" '
                f'rel="noopener noreferrer">{label}</a></li>'
            )
        tech_list = (
            f'<ul class="technique-list">{"".join(tech_items)}</ul>'
            if tech_items
            else ""
        )

        # Script badges (Exploit & Automation Suite)
        script_block = ""
        if scripts:
            script_items = []
            for sc in scripts:
                gh_link = f"{repo}/blob/main/{rel_path}/{sc['file']}"
                label = html.escape(sc["name"])
                script_items.append(
                    f'<li class="script-item"><a href="{gh_link}" '
                    f'target="_blank" rel="noopener noreferrer">⚡ {label}</a></li>'
                )
            script_block = f"""
            <div class="scripts-section">
              <div class="scripts-label">Exploit & Tool Scripts</div>
              <ul class="scripts-list">{"".join(script_items)}</ul>
            </div>"""

        badge_scripts = (
            f'<span class="badge badge-script">{script_count} '
            f"script{'s' if script_count != 1 else ''}</span>"
            if script_count
            else ""
        )

        cat_escaped = html.escape(s["dir_name"])
        doc_count_lbl = f"{tech_count} doc{'s' if tech_count != 1 else ''}"
        badge_style = (
            f"background:{color}22; color:{color}; border: 1px solid {color}55;"
        )
        cards.append(f"""
    <div class="card" data-category="{cat_escaped}" style="--card-accent: {color}">
      <div class="card-accent-bar" style="background: {color};"></div>
      <div class="card-body">
        <a class="card-link" href="{skill_link}"
           target="_blank" rel="noopener noreferrer">
          <div class="card-header">
            <span class="icon">{icon}</span>
            <h2>{cat_escaped}</h2>
            <div class="badges">
              <span class="badge" style="{badge_style}">{doc_count_lbl}</span>
              {badge_scripts}
            </div>
          </div>
          <p class="description">{desc}</p>
        </a>
        {script_block}
        <div class="tech-section">
          {tech_list}
        </div>
      </div>
    </div>""")

    # Category filter pills
    category_pills = [
        '<button class="filter-pill active" data-filter="all">All Skills</button>'
    ]
    for s in skills:
        p_name = html.escape(s["dir_name"])
        category_pills.append(
            f'<button class="filter-pill" data-filter="{p_name}">{p_name}</button>'
        )

    meta_desc = (
        "Agent Skills & autonomous solver for CTF competitions: "
        "Web, Pwn, Crypto, Reverse, Forensics, OSINT, AI/ML, Malware, and Misc."
    )
    search_placeholder = "Search techniques, vulnerabilities, or scripts..."

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CTF Skills Catalog — Claude Code Plugin</title>
  <meta name="description" content="{meta_desc}">
  <style>
    :root {{
      --bg: #09090b;
      --surface: #121215;
      --surface-elevated: #18181b;
      --border: #27272a;
      --border-focus: #3f3f46;
      --text: #f4f4f5;
      --text-muted: #a1a1aa;
      --text-subtle: #71717a;
      --accent: #06b6d4;
      --accent-glow: rgba(6, 182, 212, 0.15);
      --emerald: #10b981;
      --font-mono: ui-monospace, "SF Mono", "JetBrains Mono", Menlo,\
 Consolas, monospace;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,\
 Inter, Helvetica, Arial, sans-serif;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: var(--font-sans);
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 2.5rem 1rem 4rem;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
    }}
    .container {{
      max-width: 1280px;
      margin: 0 auto;
    }}
    /* Header */
    header {{
      text-align: center;
      margin-bottom: 2.5rem;
      padding-bottom: 2rem;
      border-bottom: 1px solid var(--border);
      position: relative;
    }}
    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.25);
      color: var(--emerald);
      font-family: var(--font-mono);
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      margin-bottom: 1rem;
      letter-spacing: 0.05em;
    }}
    .pulse-dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--emerald);
      box-shadow: 0 0 8px var(--emerald);
    }}
    header h1 {{
      font-size: clamp(2rem, 4vw, 2.75rem);
      font-weight: 800;
      letter-spacing: -0.03em;
      margin-bottom: 0.5rem;
      background: linear-gradient(180deg, #ffffff 0%, #a1a1aa 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    header p {{
      color: var(--text-muted);
      font-size: 1.1rem;
      max-width: 700px;
      margin: 0 auto;
    }}
    /* Stats bar */
    .stats-bar {{
      display: flex;
      justify-content: center;
      gap: 1rem;
      margin: 1.75rem 0 1.25rem;
      flex-wrap: wrap;
    }}
    .stat-pill {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.6rem 1.25rem;
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
    }}
    .stat-val {{
      font-family: var(--font-mono);
      font-size: 1.35rem;
      font-weight: 700;
      color: var(--accent);
    }}
    .stat-lbl {{
      font-size: 0.85rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 600;
    }}
    /* Installation Box */
    .install-box {{
      max-width: 680px;
      margin: 1.5rem auto 0;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 0.75rem 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }}
    .install-code {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      overflow-x: auto;
      font-family: var(--font-mono);
      font-size: 0.88rem;
      color: #38bdf8;
      white-space: nowrap;
    }}
    .install-code .prompt {{
      color: var(--text-subtle);
      user-select: none;
    }}
    .copy-btn {{
      background: var(--surface-elevated);
      border: 1px solid var(--border);
      color: var(--text-muted);
      border-radius: 6px;
      padding: 0.4rem 0.8rem;
      font-size: 0.8rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.2s ease;
      white-space: nowrap;
      font-family: var(--font-mono);
    }}
    .copy-btn:hover {{
      background: #27272a;
      color: var(--text);
      border-color: #52525b;
    }}
    .copy-btn.copied {{
      background: rgba(16, 185, 129, 0.2);
      border-color: var(--emerald);
      color: var(--emerald);
    }}
    /* Controls Bar (Search + Filters) */
    .controls-wrapper {{
      margin: 2rem 0;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }}
    .search-row {{
      display: flex;
      align-items: center;
      gap: 1rem;
      justify-content: space-between;
      flex-wrap: wrap;
    }}
    .search-input-wrap {{
      position: relative;
      flex: 1;
      min-width: 280px;
    }}
    .search-icon {{
      position: absolute;
      left: 1rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-subtle);
      pointer-events: none;
    }}
    .search-input {{
      width: 100%;
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text);
      border-radius: 8px;
      padding: 0.75rem 1rem 0.75rem 2.6rem;
      font-size: 0.95rem;
      font-family: inherit;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }}
    .search-input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-glow);
    }}
    .search-counter {{
      font-family: var(--font-mono);
      font-size: 0.85rem;
      color: var(--text-muted);
      white-space: nowrap;
    }}
    /* Category Filter Pills */
    .filter-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}
    .filter-pill {{
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-muted);
      border-radius: 9999px;
      padding: 0.35rem 0.85rem;
      font-size: 0.82rem;
      cursor: pointer;
      transition: all 0.15s ease;
      font-family: var(--font-mono);
    }}
    .filter-pill:hover {{
      color: var(--text);
      background: var(--surface-elevated);
      border-color: #3f3f46;
    }}
    .filter-pill.active {{
      background: var(--text);
      color: var(--bg);
      border-color: var(--text);
      font-weight: 600;
    }}
    /* Grid & Cards */
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 1.5rem;
      margin-top: 1rem;
    }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    .card:hover {{
      transform: translateY(-2px);
      border-color: rgba(255, 255, 255, 0.15);
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
    }}
    .card-accent-bar {{
      height: 3px;
      width: 100%;
    }}
    .card-body {{
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      flex: 1;
    }}
    .card-link {{
      display: block;
      color: inherit;
      text-decoration: none;
      margin-bottom: 0.75rem;
    }}
    .card-header {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      margin-bottom: 0.5rem;
    }}
    .card-header h2 {{
      font-size: 1.15rem;
      font-weight: 700;
      flex: 1;
      letter-spacing: -0.01em;
      transition: color 0.15s;
    }}
    .card-link:hover h2 {{
      color: var(--accent);
    }}
    .icon {{
      font-size: 1.35rem;
      line-height: 1;
    }}
    .badges {{
      display: flex;
      gap: 0.35rem;
    }}
    .badge {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      padding: 0.15rem 0.5rem;
      border-radius: 6px;
      font-weight: 600;
      letter-spacing: 0.02em;
    }}
    .badge-script {{
      background: rgba(16, 185, 129, 0.15);
      color: var(--emerald);
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .description {{
      color: var(--text-muted);
      font-size: 0.88rem;
      line-height: 1.5;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
      min-height: 3.8rem;
    }}
    /* Exploit Scripts Section in Card */
    .scripts-section {{
      margin: 0.75rem 0;
      padding: 0.6rem 0.75rem;
      background: rgba(16, 185, 129, 0.05);
      border: 1px solid rgba(16, 185, 129, 0.2);
      border-radius: 6px;
    }}
    .scripts-label {{
      font-family: var(--font-mono);
      font-size: 0.7rem;
      text-transform: uppercase;
      color: var(--emerald);
      letter-spacing: 0.05em;
      margin-bottom: 0.4rem;
      font-weight: 700;
    }}
    .scripts-list {{
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
    }}
    .script-item a {{
      display: inline-block;
      font-family: var(--font-mono);
      font-size: 0.78rem;
      background: rgba(16, 185, 129, 0.15);
      color: #6ee7b7;
      border: 1px solid rgba(16, 185, 129, 0.25);
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
      text-decoration: none;
      transition: background 0.15s, color 0.15s;
    }}
    .script-item a:hover {{
      background: rgba(16, 185, 129, 0.3);
      color: #a7f3d0;
    }}
    /* Techniques List in Card */
    .tech-section {{
      margin-top: auto;
      padding-top: 0.75rem;
      border-top: 1px dashed var(--border);
    }}
    .technique-list {{
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
    }}
    .tech-item a {{
      display: inline-block;
      font-size: 0.8rem;
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
      text-decoration: none;
      transition: all 0.15s ease;
    }}
    .tech-item a:hover {{
      color: var(--text);
      border-color: #52525b;
      background: var(--surface-elevated);
    }}
    /* Empty state */
    .no-results {{
      grid-column: 1 / -1;
      text-align: center;
      padding: 4rem 1rem;
      color: var(--text-subtle);
      font-family: var(--font-mono);
      display: none;
    }}
    .no-results.visible {{
      display: block;
    }}
    /* Footer */
    footer {{
      text-align: center;
      margin-top: 4rem;
      padding-top: 2rem;
      border-top: 1px solid var(--border);
      color: var(--text-subtle);
      font-size: 0.85rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      align-items: center;
    }}
    footer .links {{
      display: flex;
      gap: 1.25rem;
      flex-wrap: wrap;
      justify-content: center;
    }}
    footer a {{
      color: var(--text-muted);
      text-decoration: none;
      transition: color 0.15s;
    }}
    footer a:hover {{
      color: var(--text);
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="status-badge">
        <span class="pulse-dot"></span>
        <span>CLAUDE CODE PLUGIN CATALOG v1.1.0</span>
      </div>
      <h1>CTF Skills Catalog</h1>
      <p>Battle-tested Agent Skills, technique documentation, and automated \
exploit templates for Capture The Flag competitions.</p>
      <div class="stats-bar">
        <div class="stat-pill">
          <span class="stat-val">{total_categories}</span>
          <span class="stat-lbl">Categories</span>
        </div>
        <div class="stat-pill">
          <span class="stat-val">{total_techniques}</span>
          <span class="stat-lbl">Techniques</span>
        </div>
        <div class="stat-pill">
          <span class="stat-val">{total_scripts}</span>
          <span class="stat-lbl">Exploit Scripts</span>
        </div>
      </div>

      <div class="install-box">
        <div class="install-code">
          <span class="prompt">$</span>
          <span id="cmdText">/plugin marketplace add naravid19/claude-ctf-skills</span>
        </div>
        <button class="copy-btn" id="copyBtn" onclick="copyInstallCmd()">
          <span id="copyIcon">📋</span>
          <span id="copyLabel">Copy</span>
        </button>
      </div>
    </header>

    <div class="controls-wrapper">
      <div class="search-row">
        <div class="search-input-wrap">
          <span class="search-icon">🔍</span>
          <input type="text" id="searchInput" class="search-input" \
placeholder="{search_placeholder}" autocomplete="off">
        </div>
        <div class="search-counter" id="searchCounter">\
Showing {total_categories} categories</div>
      </div>

      <div class="filter-pills" id="filterPills">
        {"".join(category_pills)}
      </div>
    </div>

    <div class="grid" id="skillsGrid">
      {"".join(cards)}
      <div class="no-results" id="noResults">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
        <div>No matching skills, techniques, or scripts found.</div>
      </div>
    </div>

    <footer>
      <div class="links">
        <a href="{repo}" target="_blank" rel="noopener noreferrer">\
GitHub Repository</a>
        &middot;
        <a href="https://github.com/ljagiello/ctf-skills" target="_blank" \
rel="noopener noreferrer">Upstream Base (ljagiello)</a>
        &middot;
        <a href="https://agentskills.io" target="_blank" \
rel="noopener noreferrer">Agent Skills Spec</a>
        &middot;
        <span>MIT License</span>
      </div>
      <div>Designed for autonomous AI agents and cybersecurity research.</div>
    </footer>
  </div>

  <script>
    function copyInstallCmd() {{
      const text = document.getElementById('cmdText').innerText;
      navigator.clipboard.writeText(text).then(() => {{
        const btn = document.getElementById('copyBtn');
        const lbl = document.getElementById('copyLabel');
        const ico = document.getElementById('copyIcon');
        btn.classList.add('copied');
        lbl.innerText = 'Copied!';
        ico.innerText = '✓';
        setTimeout(() => {{
          btn.classList.remove('copied');
          lbl.innerText = 'Copy';
          ico.innerText = '📋';
        }}, 2000);
      }});
    }}

    // Real-time Search and Filter
    const searchInput = document.getElementById('searchInput');
    const filterPills = document.querySelectorAll('.filter-pill');
    const cards = document.querySelectorAll('.card');
    const searchCounter = document.getElementById('searchCounter');
    const noResults = document.getElementById('noResults');

    let activeFilter = 'all';

    function filterGrid() {{
      const query = searchInput.value.toLowerCase().trim();
      let visibleCount = 0;

      cards.forEach(card => {{
        const cat = card.getAttribute('data-category');
        const text = card.innerText.toLowerCase();
        const matchesCategory = (activeFilter === 'all' || cat === activeFilter);
        const matchesQuery = (!query || text.includes(query));

        if (matchesCategory && matchesQuery) {{
          card.style.display = 'flex';
          visibleCount++;
        }} else {{
          card.style.display = 'none';
        }}
      }});

      searchCounter.innerText = `Showing ${{visibleCount}} of ` +
        `${{cards.length}} categories`;
      noResults.classList.toggle('visible', visibleCount === 0);
    }}

    searchInput.addEventListener('input', filterGrid);

    filterPills.forEach(pill => {{
      pill.addEventListener('click', () => {{
        filterPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        activeFilter = pill.getAttribute('data-filter');
        filterGrid();
      }});
    }});
  </script>
</body>
</html>"""


def main() -> None:
    skills = []
    for skill_dir in discover_skills():
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        techniques = count_techniques(skill_dir)
        scripts = count_scripts(skill_dir)
        skills.append(
            {
                "dir_name": skill_dir.name,
                "rel_path": skill_dir.relative_to(REPO_ROOT).as_posix(),
                "description": fm.get("description", ""),
                "techniques": techniques,
                "scripts": scripts,
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog_html = build_html(skills)
    (OUT_DIR / "index.html").write_text(catalog_html, encoding="utf-8")
    print(f"Catalog generated: {OUT_DIR / 'index.html'}")
    total_tech = sum(len(s["techniques"]) for s in skills)
    total_sc = sum(len(s["scripts"]) for s in skills)
    print(
        f"  {len(skills)} skills, {total_tech} technique files, "
        f"{total_sc} exploit scripts"
    )


if __name__ == "__main__":
    main()
