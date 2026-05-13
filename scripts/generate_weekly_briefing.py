import feedparser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from email.utils import parsedate_to_datetime
import html

SOURCES = [
    {
        "name": "arXiv Artificial Intelligence",
        "url": "https://export.arxiv.org/rss/cs.AI",
        "area": "AI research",
    },
    {
        "name": "arXiv Machine Learning",
        "url": "https://export.arxiv.org/rss/cs.LG",
        "area": "Machine learning research",
    },
    {
        "name": "Stanford HAI",
        "url": "https://hai.stanford.edu/news/rss.xml",
        "area": "AI policy and institutions",
    },
    {
        "name": "OECD AI Policy Observatory",
        "url": "https://oecd.ai/en/wonk/rss.xml",
        "area": "AI governance and policy",
    },
]


def parse_date(entry):
    for key in ["published", "updated", "created"]:
        if key in entry:
            try:
                dt = parsedate_to_datetime(entry[key])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                pass

    return datetime.now(timezone.utc)


def clean_text(value):
    if not value:
        return ""
    return html.escape(value.replace("\n", " ").strip())


def collect_recent_items():
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    items = []

    for source in SOURCES:
        feed = feedparser.parse(source["url"])

        for entry in feed.entries[:10]:
            published = parse_date(entry)

            if published < cutoff:
                continue

            items.append({
                "title": clean_text(entry.get("title", "Untitled")),
                "link": entry.get("link", ""),
                "summary": clean_text(entry.get("summary", "No summary available."))[:900],
                "source": source["name"],
                "area": source["area"],
                "published": published,
            })

    items.sort(key=lambda x: x["published"], reverse=True)
    return items[:5]


def page_styles():
    return """
<style>
.weekly-shell * {
  box-sizing: border-box;
}

.weekly-top {
  background: #ffffff;
  border-bottom: 1px solid #e8edf3;
}

.weekly-container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 28px;
}

.weekly-header-row {
  min-height: 96px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.weekly-logo {
  color: #082b57;
  font-weight: 900;
  text-decoration: none;
  line-height: 1.05;
  font-size: 20px;
  letter-spacing: 0.02em;
}

.weekly-contact {
  background: #55aee6;
  color: #ffffff;
  text-decoration: none;
  padding: 18px 28px;
  border-radius: 8px;
  font-weight: 800;
}

.weekly-nav {
  background: #eef3f8;
}

.weekly-nav-inner {
  min-height: 64px;
  display: flex;
  align-items: center;
  gap: 32px;
  flex-wrap: wrap;
}

.weekly-nav a {
  color: #13213a;
  text-decoration: none;
  font-size: 16px;
}

.weekly-hero {
  background: #142f56;
  color: #ffffff;
  padding: 92px 0 96px;
}

.weekly-eyebrow {
  display: inline-block;
  background: #55aee6;
  color: #ffffff;
  border-radius: 999px;
  padding: 10px 18px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 14px;
}

.weekly-hero h1 {
  max-width: 980px;
  margin: 28px 0 22px;
  font-size: clamp(48px, 7vw, 86px);
  line-height: 0.95;
  color: #ffffff;
}

.weekly-hero p {
  max-width: 900px;
  font-size: 21px;
  line-height: 1.55;
  color: #ffffff;
}

.weekly-section {
  padding: 80px 0;
  background: #ffffff;
}

.weekly-section h2 {
  font-size: 42px;
  margin: 0 0 32px;
  color: #0f172a;
}

.weekly-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 28px;
}

.weekly-card {
  border: 1px solid #d9e3ef;
  border-radius: 18px;
  background: #ffffff;
  padding: 32px;
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.06);
}

.weekly-card h3 {
  color: #082b57;
  font-size: 26px;
  line-height: 1.25;
  margin: 18px 0;
}

.weekly-card h4 {
  color: #0f172a;
  font-size: 20px;
  margin-top: 28px;
}

.weekly-card p,
.weekly-card li {
  color: #475569;
  font-size: 17px;
  line-height: 1.65;
}

.weekly-card a {
  color: #0b5cab;
  font-weight: 800;
}

.weekly-footer {
  background: #f4f7fb;
  border-top: 1px solid #e2e8f0;
  padding: 42px 0;
  color: #0f172a;
}

@media (max-width: 760px) {
  .weekly-header-row {
    align-items: flex-start;
    flex-direction: column;
    gap: 18px;
    padding: 22px 0;
  }

  .weekly-nav-inner {
    gap: 16px;
    padding: 18px 28px;
  }

  .weekly-contact {
    padding: 12px 18px;
  }

  .weekly-hero {
    padding: 64px 0;
  }

  .weekly-card {
    padding: 24px;
  }
}
</style>
"""


def shared_header():
    return """
<header class="weekly-top">
  <div class="weekly-container weekly-header-row">
    <a class="weekly-logo" href="../index.html">
      INSTITUTE FOR<br />AI ECONOMICS
    </a>
    <a class="weekly-contact" href="../contact.html">Contact</a>
  </div>
</header>

<nav class="weekly-nav">
  <div class="weekly-container weekly-nav-inner">
    <a href="../index.html">Home</a>
    <a href="../research.html">Research</a>
    <a href="./index.html">Weekly Briefings</a>
    <a href="../infrastructure.html">Infrastructure</a>
    <a href="../institutions.html">Institutions</a>
    <a href="../distribution.html">Distribution</a>
    <a href="../contact.html">Contact</a>
  </div>
</nav>
"""


def shared_footer(year):
    return f"""
<footer class="weekly-footer">
  <div class="weekly-container">
    <p>© Institute for AI Economics {year}</p>
  </div>
</footer>
"""


def mental_models(area):
    return [
        f"{area} is not just technical progress. It changes who controls economic capacity.",
        "The scarce layer matters more than the visible product layer.",
        "Infrastructure determines who can scale.",
        "Institutions decide whether capability becomes real adoption.",
        "Distribution decides who captures value.",
    ]


def disagreements():
    return [
        "Scarcity versus abundance: whether AI capability becomes cheap and universal or remains concentrated through compute, chips, energy, and deployment channels.",
        "Open versus closed systems: whether open models commoditize intelligence or closed platforms win through integration, safety, trust, and distribution.",
        "Model quality versus infrastructure power: whether the best model wins or the owner of the hardest-to-route-around layer wins.",
        "National sovereignty versus market procurement: whether countries need domestic AI infrastructure or reliable access to allied commercial infrastructure.",
        "Acceleration versus governance: whether institutions should move faster or slow down to manage systemic risk.",
    ]


def deep_questions():
    return [
        "What is the real bottleneck?",
        "Who controls the scarce layer?",
        "Who becomes dependent on whom?",
        "Where does value move if models become cheaper?",
        "Which layer is hardest to route around?",
        "What would make this trend accelerate?",
        "What would make this trend fail?",
        "Which institutions gain power from this shift?",
        "Which actors lose power if this continues?",
        "What would a shallow analyst completely miss?",
    ]


def build_article_blocks(items):
    if not items:
        return """
<article class="weekly-card">
  <p class="weekly-eyebrow">No items found</p>
  <h3>No recent source items found this week</h3>
  <p>The generator ran successfully, but no recent items were detected from the current source list.</p>
</article>
"""

    article_blocks = ""

    for i, item in enumerate(items, start=1):
        models = "".join(f"<li>{m}</li>" for m in mental_models(item["area"]))
        debates = "".join(f"<li>{d}</li>" for d in disagreements())
        questions = "".join(f"<li>{q}</li>" for q in deep_questions())

        article_blocks += f"""
<article class="weekly-card">
  <p class="weekly-eyebrow">Research signal {i}</p>

  <h3>{item["title"]}</h3>

  <p><strong>Source:</strong> {item["source"]}</p>
  <p><strong>Area:</strong> {item["area"]}</p>
  <p><strong>Published:</strong> {item["published"].strftime("%B %d, %Y")}</p>
  <p><a href="{item["link"]}" target="_blank" rel="noopener">Read original source</a></p>

  <h4>Summary</h4>
  <p>{item["summary"]}</p>

  <h4>Five core mental models</h4>
  <ol>{models}</ol>

  <h4>Five places experts disagree</h4>
  <ol>{debates}</ol>

  <h4>Ten questions that test deep understanding</h4>
  <ol>{questions}</ol>
</article>
"""

    return article_blocks


def build_html(items):
    display_date = datetime.now().strftime("%B %d, %Y")
    year = datetime.now().strftime("%Y")
    article_blocks = build_article_blocks(items)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI Economics Weekly Briefing - {display_date}</title>
  <link rel="stylesheet" href="../assets/site.css" />
  {page_styles()}
</head>

<body class="weekly-shell">
  {shared_header()}

  <main>
    <section class="weekly-hero">
      <div class="weekly-container">
        <p class="weekly-eyebrow">Weekly briefing</p>
        <h1>AI Economics Weekly Briefing</h1>
        <p>{display_date}</p>
        <p>
          A weekly scan of AI infrastructure, compute, energy, governance,
          institutions, chips, and distribution.
        </p>
      </div>
    </section>

    <section class="weekly-section">
      <div class="weekly-container">
        <h2>Top 5 research signals</h2>
        <div class="weekly-grid">
          {article_blocks}
        </div>
      </div>
    </section>
  </main>

  {shared_footer(year)}
</body>
</html>"""


def build_index():
    briefings_dir = Path("weekly-briefings")
    files = sorted(
        [f for f in briefings_dir.glob("*.html") if f.name != "index.html"],
        reverse=True
    )

    cards = ""

    for f in files:
        title_date = f.stem
        cards += f"""
<article class="weekly-card">
  <p class="weekly-eyebrow">Weekly briefing</p>
  <h3><a href="./{f.name}">AI Economics Weekly Briefing</a></h3>
  <p>{title_date}</p>
  <p>
    Weekly intelligence across AI infrastructure, compute, chips,
    governance, institutions, energy, and distribution.
  </p>
</article>
"""

    year = datetime.now().strftime("%Y")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Weekly Briefings - Institute for AI Economics</title>
  <link rel="stylesheet" href="../assets/site.css" />
  {page_styles()}
</head>

<body class="weekly-shell">
  {shared_header()}

  <main>
    <section class="weekly-hero">
      <div class="weekly-container">
        <p class="weekly-eyebrow">Weekly briefings</p>
        <h1>Weekly AI economics intelligence.</h1>
        <p>
          Every week, the Institute scans AI research, infrastructure,
          compute, governance, institutions, chips, energy, and distribution.
        </p>
      </div>
    </section>

    <section class="weekly-section">
      <div class="weekly-container">
        <h2>Briefing archive</h2>
        <div class="weekly-grid">
          {cards}
        </div>
      </div>
    </section>
  </main>

  {shared_footer(year)}
</body>
</html>"""


def main():
    briefings_dir = Path("weekly-briefings")
    briefings_dir.mkdir(exist_ok=True)

    file_date = datetime.now().strftime("%Y-%m-%d")

    items = collect_recent_items()

    briefing_html = build_html(items)
    briefing_path = briefings_dir / f"{file_date}.html"
    briefing_path.write_text(briefing_html, encoding="utf-8")

    index_html = build_index()
    (briefings_dir / "index.html").write_text(index_html, encoding="utf-8")

    print(f"Generated briefing: {briefing_path}")
    print(f"Found {len(items)} items")


if __name__ == "__main__":
    main()
