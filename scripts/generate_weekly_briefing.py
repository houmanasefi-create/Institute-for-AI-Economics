import feedparser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from email.utils import parsedate_to_datetime
import html
import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SOURCES = [
    {
        "name": "arXiv Artificial Intelligence",
        "url": "https://export.arxiv.org/rss/cs.AI",
        "area": "AI research",
    },
    {
        "name": "arXiv Machine Learning",
        "url": "https://export.arxiv.org/rss/cs.LG",
        "area": "machine learning research",
    },
    {
        "name": "arXiv Computers and Society",
        "url": "https://export.arxiv.org/rss/cs.CY",
        "area": "AI society, governance, and digital institutions",
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
        "name": "BIS Speeches",
        "url": "https://www.bis.org/doclist/cbspeeches.rss",
        "area": "central banking, financial systems, and digital money",
    },
    {
        "name": "BIS Working Papers",
        "url": "https://www.bis.org/doclist/workpap.rss",
        "area": "financial systems, macroeconomics, and technology",
    },
]

PRIORITY_TERMS = [
    "ai infrastructure",
    "compute",
    "compute allocation",
    "compute economics",
    "data center",
    "datacenter",
    "datacenters",
    "energy",
    "electricity",
    "power",
    "power grid",
    "grid",
    "grid stability",
    "electric load",
    "power purchase agreement",
    "ppa",
    "power plant",
    "nuclear",
    "renewable",
    "cooling",
    "liquid cooling",
    "rack density",
    "transformer shortage",
    "chips",
    "chip manufacturing",
    "semiconductor",
    "semiconductor fabrication",
    "fab capacity",
    "tsmc",
    "nvidia",
    "amd",
    "gpu",
    "h100",
    "b200",
    "blackwell",
    "mi300",
    "accelerator",
    "training cluster",
    "inference",
    "inference cost",
    "inference serving",
    "gpu utilization",
    "latency",
    "model routing",
    "edge inference",
    "hyperscaler",
    "hyperscalers",
    "aws",
    "azure",
    "google cloud",
    "oracle cloud",
    "cloud",
    "ai factory",
    "server infrastructure",
    "supply chain",
    "chip export",
    "export controls",
    "industrial policy",
    "sovereign ai",
    "sovereign",
    "geopolitics",
    "capital expenditure",
    "capex",
    "datacenter financing",
    "frontier model",
    "foundation model",
    "open model",
    "closed model",
    "enterprise adoption",
    "deployment",
    "automation",
    "productivity",
    "labor",
    "capital concentration",
    "distribution",
    "governance",
    "policy",
    "regulation",
    "security",
]

NEGATIVE_TERMS = [
    "central bank",
    "cash landscape",
    "banknote",
    "monetary policy",
    "inflation",
    "interest rate",
    "financial stability",
    "commercial bank",
    "payment systems",
    "capital requirements",
    "basel",
]

SOURCE_WEIGHTS = {
    "BIS Speeches": 1,
    "BIS Working Papers": 1,
    "OECD AI Policy Observatory": 2,
    "Stanford HAI": 2,
    "arXiv Computers and Society": 2,
    "arXiv Artificial Intelligence": 2,
    "arXiv Machine Learning": 2,
}


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


def relevance_score(title, summary, source_name):
    combined_text = f"{title} {summary}".lower()
    score = SOURCE_WEIGHTS.get(source_name, 1)

    for term in PRIORITY_TERMS:
        if term in combined_text:
            score += 2

    for term in NEGATIVE_TERMS:
        if term in combined_text:
            score -= 2

    return max(score, 0)


def strategic_ai_score(item):
    prompt = f"""
You are ranking research relevance for the Institute for AI Economics.

The Institute mainly cares about:
- AI infrastructure
- compute economics
- power plants
- electricity demand
- power grids
- datacenters
- chip manufacturing
- semiconductor supply chains
- GPU allocation
- hyperscaler economics
- AI industrial policy
- sovereign AI
- AI deployment infrastructure
- inference economics
- capital concentration
- automation and labor displacement
- AI governance only when it connects to infrastructure, compute, markets, or institutions

Research title:
{item["title"]}

Source:
{item["source"]}

Area:
{item["area"]}

Summary:
{item["summary"]}

Return ONLY one integer from 1 to 10.

Scoring:
1 = irrelevant or generic finance/policy item
2 = weak relevance
3 = adjacent but not strong
4 = somewhat relevant
5 = useful but not central
6 = relevant to AI economy
7 = strong AI economy signal
8 = very strong infrastructure/economic signal
9 = critical strategic signal
10 = perfect fit: compute, chips, power, grid, datacenter, hyperscaler, or AI industrial system

Important:
Generic central banking, cash, banknotes, monetary policy, and financial regulation should score low unless directly connected to AI infrastructure or AI economic transformation.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You rank strategic relevance for an AI economics research briefing."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    raw_score = response.choices[0].message.content.strip()

    try:
        score = int(raw_score)
        return max(1, min(score, 10))
    except Exception:
        print(f"Could not parse strategic score for: {item['title']}")
        print(f"Raw score: {raw_score}")
        return 1


def collect_recent_items():
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    items = []

    for source in SOURCES:
        feed = feedparser.parse(source["url"])

        for entry in feed.entries[:20]:
            published = parse_date(entry)

            if published < cutoff:
                continue

            title = clean_text(entry.get("title", "Untitled"))
            link = entry.get("link", "")
            summary = clean_text(entry.get("summary", "No summary available."))[:1200]

            base_score = relevance_score(title, summary, source["name"])

            item_data = {
                "title": title,
                "link": link,
                "summary": summary,
                "source": source["name"],
                "area": source["area"],
                "published": published,
            }

            strategic_score = strategic_ai_score(item_data)
            final_score = base_score + (strategic_score * 5)

            items.append({
                "title": title,
                "link": link,
                "summary": summary,
                "source": source["name"],
                "area": source["area"],
                "published": published,
                "score": final_score,
                "strategic_score": strategic_score,
                "base_score": base_score,
            })

    items.sort(key=lambda x: (x["score"], x["published"]), reverse=True)

    selected = []

    for item in items:
        if item["strategic_score"] >= 6:
            selected.append(item)

        if len(selected) == 5:
            return selected

    for item in items:
        if item not in selected:
            selected.append(item)

        if len(selected) == 5:
            break

    return selected


def generate_deep_research_sections(item):
    prompt = f"""
You are writing for the Institute for AI Economics.

Your job is to turn one research signal into specific intellectual raw material for future essays, briefings, debates, and content systems.

Do NOT produce generic AI commentary.
Do NOT reuse fixed phrases across papers.
Do NOT force every paper into compute, chips, energy, or infrastructure unless the research actually supports it.

Research title:
{item["title"]}

Source:
{item["source"]}

Area:
{item["area"]}

Published:
{item["published"].strftime("%B %d, %Y")}

Strategic score:
{item.get("strategic_score", "N/A")}

Summary:
{item["summary"]}

Return ONLY valid JSON with this exact structure:

{{
  "core_thesis": "",
  "economic_interpretation": "",
  "five_core_mental_models": [
    "",
    "",
    "",
    "",
    ""
  ],
  "five_places_experts_disagree": [
    "",
    "",
    "",
    "",
    ""
  ],
  "ten_questions_that_test_deep_understanding": [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    ""
  ]
}}

Rules:
- Every output must be specific to this research item.
- The core thesis should explain what the research is really saying.
- The economic interpretation should explain why this matters for power, markets, institutions, labor, capital, governance, infrastructure, productivity, or distribution.
- Mental models must explain hidden mechanisms inside the research.
- Expert disagreements must describe real tensions created by the research.
- Questions must be sharp enough to feed a future content engine.
- Avoid vague questions like "What is the bottleneck?"
- Avoid generic statements like "governance matters" or "infrastructure matters."
- Write like an analytical research strategist, not a newsletter writer.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You extract specific research implications for AI economics."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.45,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        return {
            "core_thesis": data.get("core_thesis", ""),
            "economic_interpretation": data.get("economic_interpretation", ""),
            "five_core_mental_models": data.get("five_core_mental_models", [])[:5],
            "five_places_experts_disagree": data.get("five_places_experts_disagree", [])[:5],
            "ten_questions_that_test_deep_understanding": data.get("ten_questions_that_test_deep_understanding", [])[:10],
        }

    except Exception as e:
        print(f"OpenAI generation failed for: {item['title']}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {e}")
        raise


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

.weekly-score {
  display: inline-block;
  background: #eef6ff;
  color: #082b57;
  border: 1px solid #b9dcf5;
  border-radius: 999px;
  padding: 8px 14px;
  font-weight: 800;
  margin: 8px 0 12px;
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


def list_items(values):
    return "".join(f"<li>{html.escape(str(value))}</li>" for value in values)


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
        sections = generate_deep_research_sections(item)

        models = list_items(sections["five_core_mental_models"])
        debates = list_items(sections["five_places_experts_disagree"])
        questions = list_items(sections["ten_questions_that_test_deep_understanding"])

        article_blocks += f"""
<article class="weekly-card">
  <p class="weekly-eyebrow">Research signal {i}</p>

  <h3>{item["title"]}</h3>

  <p><strong>Source:</strong> {item["source"]}</p>
  <p><strong>Area:</strong> {item["area"]}</p>
  <p><strong>Published:</strong> {item["published"].strftime("%B %d, %Y")}</p>
  <p class="weekly-score">Strategic relevance score: {item.get("strategic_score", item["score"])}/10</p>
  <p><a href="{item["link"]}" target="_blank" rel="noopener">Read original source</a></p>

  <h4>Summary</h4>
  <p>{item["summary"]}</p>

  <h4>Core thesis</h4>
  <p>{html.escape(sections["core_thesis"])}</p>

  <h4>Economic interpretation</h4>
  <p>{html.escape(sections["economic_interpretation"])}</p>

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
          institutions, chips, finance, markets, and distribution.
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
    governance, institutions, energy, finance, markets, and distribution.
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
          compute, governance, institutions, chips, energy, finance,
          markets, and distribution.
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
