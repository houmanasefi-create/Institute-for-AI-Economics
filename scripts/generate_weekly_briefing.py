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
    {
        "name": "NIST AI",
        "url": "https://www.nist.gov/news-events/news/rss.xml",
        "area": "AI risk and governance",
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
            summary = clean_text(entry.get("summary", "No summary available."))

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
        f"{area} is not just a technical category. It shapes economic power.",
        "The bottleneck is often institutional adoption, not just invention.",
        "Control points matter more than surface-level product features.",
        "Infrastructure, governance, and distribution decide who captures value.",
        "Scarcity creates leverage where others assume abundance.",
    ]


def disagreements(area):
    return [
        {
            "debate": "Scarcity versus abundance",
            "side_a": "One side argues AI capability will become broadly available as models and tools get cheaper.",
            "side_b": "The other side argues scarce compute, data centers, energy, chips, and deployment channels will keep power concentrated.",
        },
        {
            "debate": "Open systems versus closed platforms",
            "side_a": "One side believes open models will commoditize the model layer.",
            "side_b": "The other side believes closed platforms will win through integration, trust, safety, and enterprise distribution.",
        },
        {
            "debate": "Technology versus institutions",
            "side_a": "One side sees technical progress as the main driver.",
            "side_b": "The other side sees organizational change, incentives, governance, and adoption speed as the real constraint.",
        },
        {
            "debate": "National capacity versus market access",
            "side_a": "One side argues nations need sovereign AI infrastructure.",
            "side_b": "The other side argues trusted access to allied commercial infrastructure is more realistic.",
        },
        {
            "debate": "Model quality versus deployment power",
            "side_a": "One side thinks the best models will capture most of the value.",
            "side_b": "The other side thinks value will flow to those who control workflows, customers, interfaces, and distribution.",
        },
    ]


def deep_questions():
    return [
        "What is the real bottleneck in this area?",
        "Who controls the scarce resource?",
        "Who becomes dependent on whom?",
        "Where does value move if the technology becomes cheaper?",
        "Which layer is hardest for competitors to route around?",
        "What would make this trend accelerate?",
        "What would make this trend fail?",
        "Which institutions benefit from this shift?",
        "Which actors lose power if this trend continues?",
        "What would a superficial analyst miss here?",
    ]


def build_html(items):
    now = datetime.now()
    file_date = now.strftime("%Y-%m-%d")
    display_date = now.strftime("%B %d, %Y")
    year = now.strftime("%Y")

    article_blocks = ""

    if not items:
        article_blocks = """
        <article>
          <h3>No recent source items found this week</h3>
          <p>The briefing generator ran successfully, but no recent items were detected from the current source list.</p>
        </article>
        """

    for i, item in enumerate(items, start=1):
        models = "".join(f"<li>{m}</li>" for m in mental_models(item["area"]))

        debates = ""
        for d in disagreements(item["area"]):
            debates += f"""
            <li>
              <strong>{d["debate"]}</strong><br />
              <em>Side A:</em> {d["side_a"]}<br />
              <em>Side B:</em> {d["side_b"]}
            </li>
            """

        questions = "".join(f"<li>{q}</li>" for q in deep_questions())

        article_blocks += f"""
        <article>
          <h3>{i}. {item["title"]}</h3>
          <p><strong>Source:</strong> {item["source"]}</p>
          <p><strong>Area:</strong> {item["area"]}</p>
          <p><strong>Published:</strong> {item["published"].strftime("%B %d, %Y")}</p>
          <p><a href="{item["link"]}">Read original source</a></p>

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

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Weekly AI Economics Briefing - {display_date}</title>
  <link rel="stylesheet" href="../assets/site.css" />
</head>
<body>
  <nav>
    <a href="../index.html">Home</a>
    <a href="../research.html">Research</a>
    <a href="./index.html">Weekly Briefings</a>
    <a href="../infrastructure.html">Infrastructure</a>
    <a href="../institutions.html">Institutions</a>
    <a href="../distribution.html">Distribution</a>
    <a href="../contact.html">Contact</a>
  </nav>

  <main>
    <section>
      <p>Weekly briefing</p>
      <h1>AI Economics Weekly Briefing</h1>
      <p>{display_date}</p>
      <p>
        A weekly scan of AI infrastructure, institutions, compute, energy, chips,
        governance, distribution, and economic power.
      </p>
    </section>

    <section>
      <h2>Top 5 research signals</h2>
      {article_blocks}
    </section>

    <section>
      <p><a href="./index.html">Back to all weekly briefings</a></p>
    </section>
  </main>

  <footer>
    <p>© Institute for AI Economics {year}</p>
  </footer>
</body>
</html>"""


def build_index():
    briefings_dir = Path("weekly-briefings")
    files = sorted(
        [f for f in briefings_dir.glob("*.html") if f.name != "index.html"],
        reverse=True
    )

    links = ""
    for f in files:
        title_date = f.stem
        links += f'<li><a href="./{f.name}">AI Economics Weekly Briefing - {title_date}</a></li>\n'

    year = datetime.now().strftime("%Y")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Weekly Briefings - Institute for AI Economics</title>
  <link rel="stylesheet" href="../assets/site.css" />
</head>
<body>
  <nav>
    <a href="../index.html">Home</a>
    <a href="../research.html">Research</a>
    <a href="./index.html">Weekly Briefings</a>
    <a href="../infrastructure.html">Infrastructure</a>
    <a href="../institutions.html">Institutions</a>
    <a href="../distribution.html">Distribution</a>
    <a href="../contact.html">Contact</a>
  </nav>

  <main>
    <section>
      <h1>Weekly Briefings</h1>
      <p>
        Weekly research briefings on AI infrastructure, institutions, compute,
        energy, distribution, governance, and economic power.
      </p>
    </section>

    <section>
      <h2>Archive</h2>
      <ul>
        {links}
      </ul>
    </section>
  </main>

  <footer>
    <p>© Institute for AI Economics {year}</p>
  </footer>
</body>
</html>"""


def main():
    briefings_dir = Path("weekly-briefings")
    briefings_dir.mkdir(exist_ok=True)

    now = datetime.now()
    file_date = now.strftime("%Y-%m-%d")

    items = collect_recent_items()
    briefing_html = build_html(items)

    briefing_path = briefings_dir / f"{file_date}.html"
    briefing_path.write_text(briefing_html, encoding="utf-8")

    index_html = build_index()
    (briefings_dir / "index.html").write_text(index_html, encoding="utf-8")

    print(f"Generated briefing: {briefing_path}")
    print(f"Found {len(items)} recent items")


if __name__ == "__main__":
    main()
