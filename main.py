"""
Kraiiv Agentic Grant Research Bot
----------------------------------
Powered by Gemini 4 Argon (gemini-4-argon).

Given a project description (or URL), this bot autonomously:
1. Understands the project — mission, audience, geography, stage
2. Searches for relevant grants, accelerators, fellowships & impact funds
3. Scores each opportunity for fit
4. Produces a structured, actionable report

Usage:
    python main.py
    python main.py --url https://kraiiv.xyz
    python main.py --desc "My project description here"
"""

import os
import sys
import argparse
import requests
from bs4 import BeautifulSoup
import textwrap
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
MODEL = "gemini-2.0-flash-thinking-exp-01-21"

KRAIIV_CONTEXT = """
Kraiiv (kraiiv.xyz) is a healthy-eating habit tracker and wellness rewards platform 
built for African food culture — specifically Nigerian and West African food. 

Core facts:
- Product: Mobile/web app (PWA) — pre-launch, waitlist stage (~200+ members in Lagos)
- Mission: Make preventive health rewarding and culturally relevant for Africa
- How it works: Users log African meals (jollof, egusi, eba, waakye, millet), 
  get AI coaching from "Klia", and earn real rewards — airtime, data, groceries, 
  and Bitcoin sats (via KTC token on Lightning Network)
- Founded: Lagos, Nigeria — targets Nigeria, Ghana, Kenya, South Africa and pan-Africa
- Business model: Free to start; potential small commitment fee; brand partnerships 
  for reward inventory; Bitcoin/Lightning integration
- Key tech: AI health coach (Klia), African food database, habit-stacking engine, 
  Bitcoin Lightning rewards
- Stage: Pre-seed / pre-revenue, building community
- Social impact: Preventive health, food sovereignty, financial inclusion (Bitcoin), 
  reducing chronic disease burden in Africa
- Team: Based in Lagos, Nigeria
"""


# ──────────────────────────────────────────────
# Argon client
# ──────────────────────────────────────────────
def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n❌  GEMINI_API_KEY environment variable not set.")
        print("    Get your key at: https://aistudio.google.com/")
        print("    Then run:  $env:GEMINI_API_KEY='your-key-here'  (PowerShell)")
        sys.exit(1)
    return genai.Client(api_key=api_key)


# ──────────────────────────────────────────────
# Agent steps
# ──────────────────────────────────────────────

def step_understand_project(client: genai.Client, project_context: str) -> str:
    """Step 1 — Deep-understand the project and extract grant-relevant attributes."""
    print("\n🔍  [Step 1/4] Analysing project profile...")

    prompt = f"""
You are an expert grant analyst and startup advisor specialised in African tech, 
health-tech, and impact investing.

Analyse this project and extract the key attributes that grant makers and impact 
investors care about. Be thorough and specific.

PROJECT CONTEXT:
{project_context}

Extract and structure the following:
1. **Mission & Impact Thesis** — 1-2 sentence elevator pitch for grant applications
2. **SDG Alignment** — which UN Sustainable Development Goals this project touches, and how
3. **Target Beneficiaries** — who directly benefits and the scale potential
4. **Geography & Market** — primary and expansion markets
5. **Stage & Traction** — current stage, metrics, milestones
6. **Technology & Innovation** — what makes this technically novel
7. **Financial Inclusion Angle** — how Bitcoin/Lightning rewards create economic empowerment
8. **Health Impact** — preventive health metrics and disease burden it addresses
9. **Key Grant Narratives** — 3-5 compelling story angles this project can tell to funders
10. **Potential Weaknesses** — honest gaps that grant applications should address

Be concise but precise. This output feeds the grant search and scoring steps.
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="medium"),
                max_output_tokens=4096,
            ),
        )
        return response.text
    except Exception as e:
        print(f"\n❌ Error during project analysis: {e}")
        sys.exit(1)


def step_search_grants(client: genai.Client, project_profile: str) -> str:
    """Step 2 — Identify specific grant opportunities across categories."""
    print("\n🌍  [Step 2/4] Searching for grant opportunities...")

    prompt = f"""
You are a senior grant researcher with deep knowledge of:
- African tech ecosystem funding (hubs, accelerators, VCs, DFIs)
- Global health and nutrition funding (WHO, Gates Foundation, Wellcome Trust, etc.)
- Bitcoin/Web3/financial inclusion grants
- Women's health and community health initiatives
- Food systems and agriculture funding
- Startup accelerators with African focus

PROJECT PROFILE:
{project_profile}

Search your knowledge and identify REAL, SPECIFIC grant opportunities across these categories.
For each, provide exact names, URLs where known, deadlines if recurring, and grant sizes.

Structure your response in these sections:

## 🏥 Global Health & Nutrition Grants
(WHO, Gates Foundation, Wellcome Trust, Rockefeller Foundation, etc.)

## 🌍 African Tech & Impact Funding
(Y Combinator, Techstars, Google for Startups Africa, Tony Elumelu Foundation, 
Ventures Platform, Founders Factory Africa, etc.)

## ⚡ Bitcoin & Financial Inclusion Grants
(Human Rights Foundation, OpenSats, Strike, Spiral/Block, Bitcoin Beach Foundation, etc.)

## 🥗 Food Systems & Nutrition
(GAIN, Access to Nutrition Initiative, EAT Foundation, etc.)

## 🏛️ Government & DFI Programs
(USAID, DFID/FCDO, EU, AfDB, World Bank IFC, etc.)

## 🚀 Startup Accelerators & Fellowships
(Batch programs with funding components relevant to health-tech Africa)

For each opportunity:
- **Name**: [exact name]
- **Funder**: [organization]
- **Amount**: [range or max]
- **Deadline**: [if known / recurring cycle]
- **URL**: [if known]
- **Why it fits Kraiiv**: [1-2 sentences]

List at least 20 specific opportunities total.
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="high"),
                max_output_tokens=8192,
            ),
        )
        return response.text
    except Exception as e:
        print(f"\n❌ Error during grant search: {e}")
        sys.exit(1)


def step_score_and_prioritize(
    client: genai.Client, project_profile: str, grant_list: str
) -> str:
    """Step 3 — Score and prioritise opportunities by fit, effort, and likelihood."""
    print("\n📊  [Step 3/4] Scoring and prioritising opportunities...")

    prompt = f"""
You are a strategic grant advisor. Using the project profile and grant list below, 
score and rank each opportunity. Think deeply about real-world fit.

PROJECT PROFILE:
{project_profile}

GRANT LIST:
{grant_list}

For each grant/opportunity, score on:
- **Fit Score** (1-10): How well does Kraiiv match the funder's stated priorities?
- **Effort Score** (1-10, lower = easier): How much work to apply?
- **Likelihood Score** (1-10): Realistic probability of success at this stage?
- **Strategic Value** (beyond money — network, press, credibility)

Then produce:

## 🎯 TOP 5 — Apply Immediately (High Fit + Achievable Now)
[Detailed action plan for each: what to prepare, who to contact, key messaging]

## ⚡ NEXT 5 — Apply in Next 3 Months (Require Some Building)
[What milestones to hit first, then apply]

## 📅 PIPELINE — 6-12 Month Horizon (Require More Traction)
[What Kraiiv needs to achieve to qualify]

## 💡 Quick Wins — Non-Grant Funding Adjacent
[Competitions, prizes, fellowships, pitch events]

## ⚠️ Application Tips Specific to Kraiiv
[Common mistakes, how to frame the Bitcoin angle, the African food narrative, etc.]
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="high"),
                max_output_tokens=8192,
            ),
        )
        return response.text
    except Exception as e:
        print(f"\n❌ Error during grant scoring: {e}")
        sys.exit(1)


def step_generate_report(
    client: genai.Client,
    project_profile: str,
    grant_list: str,
    scored_grants: str,
    project_context: str,
) -> str:
    """Step 4 — Generate the final polished, actionable grant report."""
    print("\n📝  [Step 4/4] Generating final report...")

    prompt = f"""
You are an expert grant writer and strategic advisor. 
Synthesize everything below into a clean, polished, actionable grant research report 
for the Kraiiv team.

PROJECT CONTEXT:
{project_context}

PROJECT PROFILE ANALYSIS:
{project_profile}

GRANT OPPORTUNITIES FOUND:
{grant_list}

SCORING & PRIORITIZATION:
{scored_grants}

Write the FINAL REPORT in this structure:

---
# 🌱 Kraiiv Grant & Funding Opportunities Report
**Generated**: {datetime.now().strftime('%B %d, %Y')}
**Prepared for**: Kraiiv Team (kraiiv.xyz)
**Powered by**: Gemini 4 Argon

---

## Executive Summary
[3-4 sentences: what we found, total opportunity value, top recommendation]

## Project Funding Narrative
[How to pitch Kraiiv to grant makers — the compelling story, SDG angles, 
 the African food sovereignty angle, the Bitcoin financial inclusion angle]

## Immediate Action Plan (Next 30 Days)
[Numbered list: specific actions, deadlines, contacts]

## Top Grant Opportunities — Full Details
[Clean table + narrative for the best 10 opportunities, including:
 name, funder, amount, fit score, deadline, direct link, application tips]

## Application Templates & Key Messages
[3 reusable paragraphs Kraiiv can paste into applications:
 1. Mission statement
 2. Impact metrics framing  
 3. Technology & innovation pitch]

## 12-Month Funding Roadmap
[Month-by-month plan: what to apply for and when, traction milestones to hit]

## Resources & Community
[Key networks, Slack/Discord communities, grant databases to monitor]

---
Make this report professional, specific, and immediately actionable.
Avoid vague advice. Every recommendation should have a next step the Kraiiv team 
can take today.
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="high"),
                max_output_tokens=16384,
            ),
        )
        return response.text
    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        sys.exit(1)


# ──────────────────────────────────────────────
# Orchestrator
# ──────────────────────────────────────────────

def run_grant_bot(project_context: str) -> None:
    print("\n" + "═" * 60)
    print("  🤖  Kraiiv Agentic Grant Research Bot")
    print("  Powered by Google Gemini 4 Argon")
    print("═" * 60)

    client = get_client()

    # Run the 4-step agentic pipeline
    project_profile = step_understand_project(client, project_context)
    grant_list = step_search_grants(client, project_profile)
    scored_grants = step_score_and_prioritize(client, project_profile, grant_list)
    final_report = step_generate_report(
        client, project_profile, grant_list, scored_grants, project_context
    )

    # ── Save report ──
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(
        os.path.dirname(__file__), "reports", f"grant_report_{timestamp}.md"
    )
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(final_report)

    # ── Print report to console ──
    print("\n" + "═" * 60)
    print(final_report)
    print("═" * 60)
    print(f"\n✅  Report saved to: {report_path}")
    print("    Share this with your team or paste into Notion/Docs.\n")


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Kraiiv Agentic Grant Research Bot — powered by Gemini 4 Argon"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="URL of the project to research (e.g. https://kraiiv.xyz)",
    )
    parser.add_argument(
        "--desc",
        type=str,
        default=None,
        help="Text description of the project",
    )
    args = parser.parse_args()

    if args.desc:
        context = args.desc
    elif args.url:
        print(f"\n🌐 Fetching project context from: {args.url}")
        try:
            response = requests.get(args.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for script_or_style in soup(["script", "style"]):
                script_or_style.extract()
            text = soup.get_text(separator=" ", strip=True)
            context = f"Project extracted from {args.url}:\n\n" + text[:5000]
        except Exception as e:
            print(f"❌ Failed to fetch URL: {e}")
            sys.exit(1)
    else:
        # Default: use Kraiiv's baked-in context
        context = KRAIIV_CONTEXT

    run_grant_bot(context)


if __name__ == "__main__":
    main()
