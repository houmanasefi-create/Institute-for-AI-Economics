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
        "name": "Google News - AI Datacenter Power Grid",
        "url": "https://news.google.com/rss/search?q=AI%20datacenter%20power%20grid&hl=en-US&gl=US&ceid=US:en",
        "area": "AI datacenters, electricity demand, and grid infrastructure",
    },
    {
        "name": "Google News - AI Chips Semiconductor",
        "url": "https://news.google.com/rss/search?q=AI%20chips%20semiconductor%20NVIDIA%20TSMC&hl=en-US&gl=US&ceid=US:en",
        "area": "AI chips, GPUs, semiconductor supply chains, and chip manufacturing",
    },
    {
        "name": "Google News - AI Infrastructure Compute",
        "url": "https://news.google.com/rss/search?q=AI%20infrastructure%20compute%20datacenter%20GPU&hl=en-US&gl=US&ceid=US:en",
        "area": "AI infrastructure, compute capacity, datacenters, and GPU supply",
    },
    {
        "name": "Google News - Hyperscaler Energy",
        "url": "https://news.google.com/rss/search?q=hyperscaler%20data%20center%20energy%20nuclear%20power&hl=en-US&gl=US&ceid=US:en",
        "area": "hyperscaler power demand, energy procurement, and datacenter expansion",
    },
    {
        "name": "Google News - Sovereign AI Compute",
        "url": "https://news.google.com/rss/search?q=sovereign%20AI%20compute%20infrastructure%20chips%20datacenter&hl=en-US&gl=US&ceid=US:en",
        "area": "sovereign AI, compute infrastructure, industrial policy, and geopolitics",
    },
    {
        "name": "The Next Platform",
        "url": "https://www.nextplatform.com/feed/",
        "area": "compute infrastructure, HPC, hyperscale datacenters, chips, and AI systems",
    },
    {
        "name": "Data Center Dynamics",
        "url": "https://www.datacenterdynamics.com/en/rss/",
        "area": "datacenters, power, cooling, hyperscale infrastructure, and AI compute",
    },
    {
        "name": "ServeTheHome",
        "url": "https://www.servethehome.com/feed/",
        "area": "server infrastructure, GPUs, accelerators, networking, and datacenter hardware",
    },
    {
        "name": "NVIDIA Blog",
        "url": "https://blogs.nvidia.com/feed/",
        "area": "GPU infrastructure, accelerated computing, AI factories, and inference",
    },
    {
        "name": "Utility Dive",
        "url": "https://www.utilitydive.com/feeds/news/",
        "area": "electricity grids, utilities, power demand, generation, and datacenter load",
    },
    {
        "name": "IEA Reports",
        "url": "https://www.iea.org/rss/reports.xml",
        "area": "energy systems, electricity demand, grids, and industrial power infrastructure",
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

TIER_1_TOPICS = [
    "ai infrastructure",
    "compute",
    "compute allocation",
    "compute economics",
    "gpu",
    "gpu allocation",
    "gpu utilization",
    "chips",
    "chip manufacturing",
    "semiconductor",
    "semiconductor fabrication",
    "fab capacity",
    "tsmc",
    "nvidia",
    "amd",
    "h100",
    "b200",
    "blackwell",
    "mi300",
    "accelerator",
    "training cluster",
    "inference",
    "inference cost",
    "inference serving",
    "latency",
    "datacenter",
    "data center",
    "datacenters",
    "power grid",
    "electricity",
    "energy",
    "power",
    "power plant",
    "electric load",
    "grid stability",
    "power purchase agreement",
    "ppa",
    "nuclear",
    "cooling",
    "liquid cooling",
    "rack density",
    "transformer shortage",
    "hyperscaler",
    "hyperscalers",
    "aws",
    "azure",
    "google cloud",
    "oracle cloud",
    "ai factory",
    "server infrastructure",
    "sovereign ai",
    "export controls",
    "chip export",
    "industrial policy",
    "supply chain",
    "ai supply chain",
    "datacenter financing",
    "capex",
    "capital expenditure",
]

TIER_2_TOPICS = [
    "enterprise adoption",
    "deployment",
    "automation",
    "labor",
    "labor displacement",
    "productivity",
    "capital concentration",
    "market power",
    "distribution",
    "ai governance",
    "regulation",
    "policy",
    "institutions",
    "geopolitics",
    "security",
    "robotics",
    "frontier model",
    "foundation model",
    "open model",
    "closed model",
]

TIER_3_TOPICS = [
    "agent orchestration",
    "orchestration",
    "agentic",
    "multi-agent",
    "prompting",
    "reasoning",
    "memory",
    "alignment",
    "synthetic data",
    "benchmark",
    "framework",
    "workflow",
    "planner",
    "reflection",
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
    "Google News - AI Datacenter Power Grid": 6,
    "Google News - AI Chips Semiconductor": 6,
    "Google News - AI Infrastructure Compute": 6,
    "Google News - Hyperscaler Energy": 6,
    "Google News - Sovereign AI Compute": 6,
    "The Next Platform": 6,
    "Data Center Dynamics": 6,
    "ServeTheHome": 5,
    "NVIDIA Blog": 5,
    "Utility Dive": 5,
    "IEA Reports": 5,
    "Stanford HAI": 3,
    "OECD AI Policy Observatory": 3,
    "arXiv Computers and Society": 2,
    "arXiv Artificial Intelligence": 1,
    "arXiv Machine Learning": 1,
    "BIS Working Papers": 1,
    "BIS Speeches": 0,
}

MAX_ITEMS_PER_SOURCE = 12
MAX_CANDIDATES_FOR_LLM_RANKING = 45
BRIEFING_ITEM_COUNT = 5
CUTOFF_DAYS = 14


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


def topic_match_score(title, summary):
    combined_text = f"{title} {summary}".lower()

    tier_1_hits = sum(1 for term in TIER_1_TOPICS if term in combined_text)
    tier_2_hits = sum(1 for term in TIER_2_TOPICS if term in combined_text)
    tier_3_hits = sum(1 for term in TIER_3_TOPICS if term in combined_text)
    negative_hits = sum(1 for term in NEGATIVE_TERMS if term in combined_text)

    score = 0
    score += tier_1_hits * 8
    score += tier_2_hits * 3
    score += tier_3_hits * 1
    score -= negative_hits * 4

    if tier_1_hits == 0 and tier_3_hits > 0:
        score -= 2

    return max(score, 0), tier_1_hits, tier_2_hits, tier_3_hits


def relevance_score(title, summary, source_name):
    source_score = SOURCE_WEIGHTS.get(source_name, 1)
    topic_score, _, _, _ = topic_match_score(title, summary)
    return max(source_score + topic_score, 0)


def strategic_ai_score(item):
    prompt = f"""
You are ranking research relevance for the Institute for AI Economics.

The Institute's thesis is:

AI is not mainly a software story.
AI is an industrial infrastructure system.

The Institute cares most about:
- compute bottlenecks
- GPU supply
- chip manufacturing
- semiconductor supply chains
- datacenters
- electricity demand
- power grids
- power plants
- cooling
- hyperscaler economics
- AI infrastructure finance
- inference economics
- sovereign AI infrastructure
- AI industrial policy
- export controls
- capital concentration around infrastructure
- AI deployment at economic scale

The Institute cares moderately about:
- labor automation
- enterprise adoption
- productivity
- AI governance
- institutions
- distribution
- market structure

The Institute actively downranks:
- generic agent orchestration
- generic LLM reasoning
- prompting
- benchmark improvements
- abstract model architecture
- synthetic data methods
- legal AI
- generic e-commerce AI
- central banking unrelated to AI infrastructure

A paper about agents, reasoning, prompting, benchmarks, legal AI, or e-commerce should score 1-3 unless it clearly changes deployment economics, compute economics, infrastructure demand, labor markets, industrial organization, or market power.

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
1 = irrelevant
2 = generic finance, central banking, or technical AI paper with no economic infrastructure relevance
3 = generic AI architecture, agent, reasoning, prompting, or benchmark paper
4 = adjacent to AI economy but not central
5 = useful AI economy signal
6 = relevant to deployment, labor, productivity, governance, or institutions
7 = strong AI economy signal
8 = very strong infrastructure, compute, chip, datacenter, power, or hyperscaler signal
9 = critical strategic signal about AI industrial systems
10 = perfect fit: compute, chips, power grid, datacenters, hyperscalers, energy, semiconductor manufacturing, AI infrastructure finance, or sovereign AI infrastructure

Important:
Do not give a high score just because the paper is about AI.
Generic AI agent papers should usually be 1-3 unless they clearly connect to deployment economics, infrastructure economics, labor substitution, market power, or enterprise-scale adoption.
Generic central bank content should score low unless it directly connects to AI infrastructure or AI economic transformation.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You rank strategic relevance for a thesis-driven AI economics research briefing."
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
        return 3


def collect_recent_items():
    cutoff = datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS)
    raw_items = []
    seen_titles = set()

    for source in SOURCES:
        feed = feedparser.parse(source["url"])

        if getattr(feed, "bozo", False):
            print(f"Feed warning for {source['name']}: {getattr(feed, 'bozo_exception', 'Unknown feed issue')}")

        print(f"Source {source['name']} returned {len(feed.entries)} entries")

        for entry in feed.entries[:MAX_ITEMS_PER_SOURCE]:
            published = parse_date(entry)

            if published < cutoff:
                continue

            title = clean_text(entry.get("title", "Untitled"))
            title_key = title.lower().strip()

            if title_key in seen_titles:
                continue

            seen_titles.add(title_key)

            link = entry.get("link", "")
            summary = clean_text(entry.get("summary", entry.get("description", "No summary available.")))[:1200]

            base_score = relevance_score(title, summary, source["name"])
            _, tier_1_hits, tier_2_hits, tier_3_hits = topic_match_score(title, summary)

            source_bonus = SOURCE_WEIGHTS.get(source["name"], 1)

            pre_score = (
                base_score
                + source_bonus
                + (tier_1_hits * 12)
                + (tier_2_hits * 4)
                - (tier_3_hits * 2 if tier_1_hits == 0 else 0)
            )

            raw_items.append({
                "title": title,
                "link": link,
                "summary": summary,
                "source": source["name"],
                "area": source["area"],
                "published": published,
                "pre_score": pre_score,
                "base_score": base_score,
                "tier_1_hits": tier_1_hits,
                "tier_2_hits": tier_2_hits,
                "tier_3_hits": tier_3_hits,
            })

    print(f"Total collected RSS items before LLM ranking: {len(raw_items)}")

    if not raw_items:
        print("No RSS items collected within cutoff window.")
        return []

    raw_items.sort(key=lambda x: (x["pre_score"], x["published"]), reverse=True)

    candidates = raw_items[:MAX_CANDIDATES_FOR_LLM_RANKING]

    print("Top candidates before LLM ranking:")
    for item in candidates[:15]:
        print(
            f"PRE={item['pre_score']} | "
            f"T1={item['tier_1_hits']} | "
            f"T2={item['tier_2_hits']} | "
            f"T3={item['tier_3_hits']} | "
            f"SOURCE={item['source']} | "
            f"TITLE={item['title']}"
        )

    ranked_items = []

    for item in candidates:
        strategic_score = strategic_ai_score(item)

        final_score = (
            item["pre_score"]
            + (strategic_score * 8)
            + (item["tier_1_hits"] * 15)
            + (item["tier_2_hits"] * 5)
            - (item["tier_3_hits"] * 3 if item["tier_1_hits"] == 0 else 0)
        )

        item["strategic_score"] = strategic_score
        item["score"] = final_score
        ranked_items.append(item)

    ranked_items.sort(key=lambda x: (x["score"], x["published"]), reverse=True)

    print("Top ranked candidates after LLM ranking:")
    for item in ranked_items[:15]:
        print(
            f"SCORE={item['score']} | "
            f"STRATEGIC={item['strategic_score']} | "
            f"T1={item['tier_1_hits']} | "
            f"T2={item['tier_2_hits']} | "
            f"T3={item['tier_3_hits']} | "
            f"SOURCE={item['source']} | "
            f"TITLE={item['title']}"
        )

    selected = []

    for item in ranked_items:
        if item["tier_1_hits"] >= 1 and item["strategic_score"] >= 5:
            selected.append(item)

        if len(selected) >= 4:
            break

    for item in ranked_items:
        if item in selected:
            continue

        is_generic_ai_only = item["tier_1_hits"] == 0 and item["tier_3_hits"] > 0 and item["strategic_score"] <= 3

        if not is_generic_ai_only and item["strategic_score"] >= 5:
            selected.append(item)

        if len(selected) >= BRIEFING_ITEM_COUNT:
            break

    for item in ranked_items:
        if len(selected) >= BRIEFING_ITEM_COUNT:
            break

        if item not in selected and not (item["tier_1_hits"] == 0 and item["tier_3_hits"] > 0):
            selected.append(item)

    for item in ranked_items:
        if len(selected) >= BRIEFING_ITEM_COUNT:
            break

        if item not in selected:
            selected.append(item)

    return selected[:BRIEFING_ITEM_COUNT]


def generate_deep_research_sections(item):
    prompt = f"""
You are writing for the Institute for AI Economics.

Your job is to turn one research signal into specific intellectual raw material for future essays, briefings, debates, and content systems.

The Institute's lens:
AI is an industrial infrastructure system made of compute, energy, chips, datacenters, distribution, institutions, capital, and power.

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
- Include at least one question about second-order economic consequences.
- Include at least one question about who gains power and who loses power if the research direction scales.
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
