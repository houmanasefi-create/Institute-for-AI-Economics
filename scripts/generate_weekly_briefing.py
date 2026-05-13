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

            title = clean_text(entry.get("title", "Untitled"))
            link = entry.get("link", "")
            summary = clean_text(entry.get("summary", ""))

            items.append({
                "title": title,
                "link": link,
                "summary": summary[:700],
                "source": source["name"],
                "area": source["area"],
                "published": published,
            })

    items.sort(key=lambda x: x["published"], reverse=True)

    return items[:5]


def mental_models(area):
    return [
        f"{area} shapes economic and institutional power.",
        "Infrastructure bottlenecks matter more than surface-level products.",
        "Distribution controls adoption.",
        "Governance determines scalability.",
        "Scarcity creates leverage.",
    ]


def disagreements():
    return [
        "Open models versus closed platforms",
        "Scarcity versus abundance",
        "National AI versus global infrastructure",
        "Model quality versus distribution power",
        "Regulation versus acceleration",
    ]


def deep_questions():
    return [
        "Who controls the bottleneck?",
        "Which layer captures value?",
        "What becomes commoditized?",
        "Where does dependency form?",
        "What changes institutional power?",
    ]


def shared_header():
    return """
<header class="site-header">
  <div class="container header-inner">
    <a class="logo" href="../index.html">
      INSTITUTE FOR<br />AI ECONOMICS
    </a>

    <a class="button" href="../contact.html">
      Contact
    </a>
  </div>
</header>

<nav class="site-nav">
  <div class="container nav-inner">
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
<footer class="site-footer">
  <div class="container">
    <p>© Institute for AI Economics {year}</p>
  </div>
</footer>
"""


def build_html(items):

    display_date = datetime.now().strftime("%B %d, %Y")
    file_date = datetime.now().strftime("%Y-%m-%d")
    year = datetime.now().strftime("%Y")

    article_blocks = ""

    for i, item in enumerate(items, start=1):

        models = "".join(
            f"<li>{m}</li>"
            for m in mental_models(item["area"])
        )

        debates = "".join(
            f"<li>{d}</li>"
            for d in disagreements()
        )

        questions = "".join(
            f"<li>{q}</li>"
            for q in deep_questions()
        )

        article_blocks += f"""
<article class="card briefing-card">

  <p class="eyebrow">
    Research signal {i}
  </p>

  <h3>
    {item["title"]}
  </h3>

  <p>
    <strong>Source:</strong> {item["source"]}
  </p>

  <p>
    <strong>Area:</strong> {item["area"]}
  </p>

  <p>
    <strong>Published:</strong>
    {item["published"].strftime("%B %d, %Y")}
  </p>

  <p>
    <a href="{item["link"]}" target="_blank">
      Read original source
    </a>
  </p>

  <h4>Summary</h4>

  <p>{item["summary"]}</p>

  <h4>Core mental models</h4>

  <ol>{models}</ol>

  <h4>Expert disagreements</h4>

  <ol>{debates}</ol>

  <h4>Deep understanding questions</h4>

  <ol>{questions}</ol>

</article>
"""

    return f"""
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI Economics Weekly Briefing</title>

  <link rel="stylesheet" href="../assets/site.css" />
</head>

<body>

{shared_header()}

<main>

<section class="hero">
  <div class="container">

    <p class="eyebrow">
      Weekly briefing
    </p>

    <h1>
      AI Economics Weekly Briefing
    </h1>

    <p>
      {display_date}
    </p>

    <p>
      A weekly scan of AI infrastructure,
      compute, energy, governance,
      institutions, chips, and distribution.
    </p>

  </div>
</section>

<section class="section">
  <div class="container">

    <h2>
      Top 5 research signals
    </h2>

    <div class="briefing-grid">

      {article_blocks}

    </div>

  </div>
</section>

</main>

{shared_footer(year)}

</body>
</html>
"""


def build_index():

    briefings_dir = Path("weekly-briefings")

    files = sorted(
        [
            f for f in briefings_dir.glob("*.html")
            if f.name != "index.html"
        ],
        reverse=True
    )

    cards = ""

    for f in files:

        title_date = f.stem

        cards += f"""
<article class="card briefing-card">

  <p class="eyebrow">
    Weekly briefing
  </p>

  <h3>
    <a href="./{f.name}">
      AI Economics Weekly Briefing
    </a>
  </h3>

  <p>
    {title_date}
  </p>

  <p>
    Weekly intelligence across AI infrastructure,
    compute, chips, governance, institutions,
    and distribution.
  </p>

</article>
"""

    year = datetime.now().strftime("%Y")

    return f"""
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>
    Weekly Briefings
  </title>

  <link rel="stylesheet" href="../assets/site.css" />
</head>

<body>

{shared_header()}

<main>

<section class="hero">
  <div class="container">

    <p class="eyebrow">
      Weekly briefings
    </p>

    <h1>
      Weekly AI economics intelligence.
    </h1>

    <p>
      Every week, the Institute scans AI research,
      infrastructure, compute, governance,
      institutions, chips, and distribution.
    </p>

  </div>
</section>

<section class="section">
  <div class="container">

    <h2>
      Briefing archive
    </h2>

    <div class="briefing-grid">

      {cards}

    </div>

  </div>
</section>

</main>

{shared_footer(year)}

</body>
</html>
"""


def main():

    briefings_dir = Path("weekly-briefings")

    briefings_dir.mkdir(exist_ok=True)

    file_date = datetime.now().strftime("%Y-%m-%d")

    items = collect_recent_items()

    briefing_html = build_html(items)

    briefing_path = briefings_dir / f"{file_date}.html"

    briefing_path.write_text(
        briefing_html,
        encoding="utf-8"
    )

    index_html = build_index()

    (briefings_dir / "index.html").write_text(
        index_html,
        encoding="utf-8"
    )

    print(f"Generated briefing: {briefing_path}")


if __name__ == "__main__":
    main()
