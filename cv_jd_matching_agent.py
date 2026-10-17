"""
CV / Job Description Matching Agent
====================================
Built by Saksham Kapahi — October 2026

This agent:
1. Accepts a Job Description (JD) as text input
2. Extracts structured requirements (skills, experience, qualifications)
3. Scores a candidate CV profile against those requirements
4. Outputs a structured gap analysis report

No API key required — runs entirely with local logic and pattern matching.
Designed to demonstrate business analysis methodology applied to talent matching.
"""

import json
import re
from datetime import datetime

# ── Candidate Profile (Saksham Kapahi) ───────────────────────────────────────
CANDIDATE_PROFILE = {
    "name": "Saksham Kapahi",
    "location": "Dublin, Ireland",
    "years_experience": 6,
    "education": [
        {"degree": "MSc Business Management", "institution": "Dublin City University", "year": 2024},
        {"degree": "PGDM Marketing", "institution": "NMIMS India", "year": 2023},
        {"degree": "BEng Electrical Engineering", "institution": "DAVIET India", "year": 2018},
    ],
    "skills": [
        "business analysis", "requirements gathering", "process mapping", "stakeholder management",
        "power bi", "advanced excel", "sql", "salesforce", "sap", "jira",
        "project management", "prince2", "change management", "agile",
        "data analysis", "reporting", "dashboards", "kpi", "crm",
        "customer success", "account management", "onboarding", "b2b",
        "uml", "bpmn", "brd", "uat", "user stories", "gap analysis",
        "vendor management", "cross-functional teams", "ai tools", "automation",
        "operations", "order management", "supply chain", "sla",
    ],
    "certifications": [
        "PRINCE2 Practitioner", "Salesforce Administrator",
        "Business Analysis Foundation", "Change Management Foundation",
        "Project Management Foundation",
    ],
    "tools": [
        "Power BI", "Advanced Excel", "SQL", "Salesforce", "SAP", "Jira",
        "Microsoft Project", "WebERP", "Google Workspace",
    ],
    "industries": [
        "technology", "telecommunications", "operations", "logistics",
        "manufacturing", "consulting", "saas", "fintech",
    ],
    "experience_highlights": [
        "Managed 20-25 Meta Verified accounts daily with 90%+ quality score",
        "Reduced escalations by ~20% through process improvement and agent coaching",
        "Managed 300+ B2B accounts across UK and Ireland at Three Ireland",
        "Delivered 500+ projects annually with 100% SLA at JK Technocrats",
        "Reduced delivery delays by ~30% through SAP-driven process optimisation",
        "Built Power BI dashboards for operational reporting",
        "Facilitated stakeholder workshops across 10+ groups",
        "Led UAT and business requirement documentation (BRDs)",
    ],
}

# ── Requirement Extraction Engine ─────────────────────────────────────────────
SKILL_KEYWORDS = {
    "technical": [
        "sql", "power bi", "tableau", "excel", "python", "r", "java", "sap",
        "salesforce", "jira", "confluence", "azure", "aws", "powerpoint",
        "visio", "ms project", "sharepoint", "erp", "crm", "api",
    ],
    "business_analysis": [
        "requirements", "brd", "user stories", "use cases", "process mapping",
        "gap analysis", "uml", "bpmn", "stakeholder", "workshops", "uat",
        "acceptance criteria", "business case", "feasibility",
    ],
    "project_management": [
        "prince2", "pmp", "agile", "scrum", "waterfall", "kanban", "pmbok",
        "project plan", "milestone", "risk management", "raid", "governance",
        "change management", "delivery",
    ],
    "soft_skills": [
        "communication", "collaboration", "leadership", "analytical",
        "problem solving", "attention to detail", "stakeholder management",
        "presentation", "interpersonal", "adaptable", "proactive",
    ],
}

EXPERIENCE_PATTERNS = [
    r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
    r'minimum\s+(?:of\s+)?(\d+)\s*years?',
    r'at\s+least\s+(\d+)\s*years?',
    r'(\d+)[-–](\d+)\s*years?',
]

EDUCATION_KEYWORDS = [
    "bachelor", "master", "msc", "bsc", "mba", "degree", "phd",
    "postgraduate", "qualification", "pgdm", "honours",
]


def extract_requirements(jd_text: str) -> dict:
    """Extract structured requirements from a job description."""
    jd_lower = jd_text.lower()
    requirements = {
        "required_skills": [],
        "preferred_skills": [],
        "years_experience_min": 0,
        "education_required": False,
        "certifications_mentioned": [],
        "raw_keywords_found": [],
    }

    # Detect required vs preferred sections
    required_section = ""
    preferred_section = ""

    req_match = re.search(
        r'(required|must\s+have|essential)[:\s]*(.*?)(?=preferred|desirable|nice\s+to\s+have|$)',
        jd_lower, re.DOTALL
    )
    pref_match = re.search(
        r'(preferred|desirable|nice\s+to\s+have)[:\s]*(.*?)(?=required|must\s+have|$)',
        jd_lower, re.DOTALL
    )

    required_section = req_match.group(2) if req_match else jd_lower
    preferred_section = pref_match.group(2) if pref_match else ""

    # Extract skills
    for category, keywords in SKILL_KEYWORDS.items():
        for kw in keywords:
            if kw in required_section:
                requirements["required_skills"].append({"skill": kw, "category": category})
                requirements["raw_keywords_found"].append(kw)
            elif kw in preferred_section:
                requirements["preferred_skills"].append({"skill": kw, "category": category})

    # Extract years of experience
    for pattern in EXPERIENCE_PATTERNS:
        match = re.search(pattern, jd_lower)
        if match:
            try:
                requirements["years_experience_min"] = int(match.group(1))
                break
            except (IndexError, ValueError):
                pass

    # Education check
    for kw in EDUCATION_KEYWORDS:
        if kw in jd_lower:
            requirements["education_required"] = True
            break

    # Certification mentions
    cert_keywords = ["prince2", "pmp", "salesforce", "aws", "azure", "cpa", "acca", "iiba"]
    for ck in cert_keywords:
        if ck in jd_lower:
            requirements["certifications_mentioned"].append(ck.upper())

    return requirements


def score_candidate(requirements: dict, profile: dict) -> dict:
    """Score candidate profile against extracted requirements."""
    scores = {
        "required_skills_match": [],
        "required_skills_gap": [],
        "preferred_skills_match": [],
        "preferred_skills_gap": [],
        "experience_score": 0,
        "education_score": 0,
        "certifications_score": 0,
        "overall_score": 0,
        "overall_pct": 0,
    }

    candidate_skills_lower = [s.lower() for s in profile["skills"]]
    candidate_tools_lower  = [t.lower() for t in profile["tools"]]
    all_candidate = candidate_skills_lower + candidate_tools_lower

    # Required skills
    for item in requirements["required_skills"]:
        skill = item["skill"].lower()
        matched = any(skill in cs or cs in skill for cs in all_candidate)
        if matched:
            scores["required_skills_match"].append(item["skill"])
        else:
            scores["required_skills_gap"].append(item["skill"])

    # Preferred skills
    for item in requirements["preferred_skills"]:
        skill = item["skill"].lower()
        matched = any(skill in cs or cs in skill for cs in all_candidate)
        if matched:
            scores["preferred_skills_match"].append(item["skill"])
        else:
            scores["preferred_skills_gap"].append(item["skill"])

    # Experience score (0–30)
    if requirements["years_experience_min"] > 0:
        ratio = min(profile["years_experience"] / requirements["years_experience_min"], 1.5)
        scores["experience_score"] = round(min(ratio * 30, 30))
    else:
        scores["experience_score"] = 25  # default if not specified

    # Education score (0–20)
    scores["education_score"] = 20 if requirements["education_required"] and profile["education"] else 15

    # Certification score (0–10)
    certs_lower = [c.lower() for c in profile["certifications"]]
    certs_matched = [
        c for c in requirements["certifications_mentioned"]
        if any(c.lower() in cl for cl in certs_lower)
    ]
    if requirements["certifications_mentioned"]:
        scores["certifications_score"] = round(
            (len(certs_matched) / len(requirements["certifications_mentioned"])) * 10
        )
    else:
        scores["certifications_score"] = 8

    # Required skills score (0–40)
    total_req = len(requirements["required_skills"])
    if total_req > 0:
        req_score = round((len(scores["required_skills_match"]) / total_req) * 40)
    else:
        req_score = 30

    scores["overall_score"] = (
        req_score +
        scores["experience_score"] +
        scores["education_score"] +
        scores["certifications_score"]
    )
    scores["overall_pct"] = min(scores["overall_score"], 100)

    return scores


def generate_report(jd_text: str, role_title: str = "Role") -> str:
    """Main agent function — run the full pipeline and return a formatted report."""
    print(f"\n{'='*60}")
    print(f"  CV / JD MATCHING AGENT")
    print(f"  Analysing: {role_title}")
    print(f"  Candidate: {CANDIDATE_PROFILE['name']}")
    print(f"  Run date:  {datetime.now().strftime('%d %b %Y %H:%M')}")
    print(f"{'='*60}\n")

    print("→ Step 1: Extracting requirements from JD...")
    requirements = extract_requirements(jd_text)
    print(f"  Found {len(requirements['required_skills'])} required skills, "
          f"{len(requirements['preferred_skills'])} preferred skills")
    print(f"  Min experience detected: {requirements['years_experience_min']} years")

    print("\n→ Step 2: Scoring candidate profile...")
    scores = score_candidate(requirements, CANDIDATE_PROFILE)

    print("\n→ Step 3: Generating gap analysis report...\n")

    # ── Report Output ──────────────────────────────────────────────────────────
    report = []
    report.append("=" * 60)
    report.append("  GAP ANALYSIS REPORT")
    report.append(f"  Role:      {role_title}")
    report.append(f"  Candidate: {CANDIDATE_PROFILE['name']}")
    report.append(f"  Date:      {datetime.now().strftime('%d %b %Y')}")
    report.append("=" * 60)

    report.append(f"\n  OVERALL MATCH SCORE: {scores['overall_pct']}%")
    bar_filled = int(scores['overall_pct'] / 5)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)
    report.append(f"  [{bar}]")

    # Verdict
    if scores['overall_pct'] >= 75:
        verdict = "STRONG FIT — Recommend to apply"
    elif scores['overall_pct'] >= 55:
        verdict = "GOOD FIT — Apply with tailored CV"
    elif scores['overall_pct'] >= 40:
        verdict = "PARTIAL FIT — Address gaps in cover letter"
    else:
        verdict = "WEAK FIT — Consider skipping"
    report.append(f"  Verdict:   {verdict}\n")

    report.append("-" * 60)
    report.append("  REQUIRED SKILLS ANALYSIS")
    report.append("-" * 60)

    if scores["required_skills_match"]:
        report.append("\n  ✓ MATCHED:")
        for s in scores["required_skills_match"]:
            report.append(f"    • {s.title()}")

    if scores["required_skills_gap"]:
        report.append("\n  ✗ GAPS:")
        for s in scores["required_skills_gap"]:
            report.append(f"    • {s.title()}")

    report.append(f"\n  Required skills matched: "
                  f"{len(scores['required_skills_match'])} / "
                  f"{len(requirements['required_skills'])}")

    if scores["preferred_skills_match"] or scores["preferred_skills_gap"]:
        report.append("\n" + "-" * 60)
        report.append("  PREFERRED SKILLS ANALYSIS")
        report.append("-" * 60)
        if scores["preferred_skills_match"]:
            report.append("\n  ✓ MATCHED:")
            for s in scores["preferred_skills_match"]:
                report.append(f"    • {s.title()}")
        if scores["preferred_skills_gap"]:
            report.append("\n  ✗ NOT MATCHED:")
            for s in scores["preferred_skills_gap"]:
                report.append(f"    • {s.title()}")

    report.append("\n" + "-" * 60)
    report.append("  EXPERIENCE & QUALIFICATIONS")
    report.append("-" * 60)
    report.append(f"\n  Candidate experience : {CANDIDATE_PROFILE['years_experience']} years")
    report.append(f"  Role minimum         : {requirements['years_experience_min']} years")
    exp_status = "✓ Meets requirement" if CANDIDATE_PROFILE['years_experience'] >= requirements['years_experience_min'] else "✗ Below requirement"
    report.append(f"  Status               : {exp_status}")
    report.append(f"\n  Education required   : {'Yes' if requirements['education_required'] else 'Not specified'}")
    report.append(f"  Candidate education  : {CANDIDATE_PROFILE['education'][0]['degree']}, {CANDIDATE_PROFILE['education'][0]['institution']}")

    if requirements["certifications_mentioned"]:
        report.append(f"\n  Certifications sought: {', '.join(requirements['certifications_mentioned'])}")
        report.append(f"  Candidate holds      : {', '.join(CANDIDATE_PROFILE['certifications'][:3])}")

    report.append("\n" + "-" * 60)
    report.append("  RECOMMENDED CV TAILORING ACTIONS")
    report.append("-" * 60)

    actions = []
    if scores["required_skills_gap"]:
        gaps = ", ".join(s.title() for s in scores["required_skills_gap"][:3])
        actions.append(f"Address gaps in cover letter: {gaps}")
    if scores["overall_pct"] >= 55:
        actions.append("Lead CV summary with role-specific language from JD")
        actions.append("Quantify metrics aligned to JD priorities")
    if requirements["certifications_mentioned"]:
        for c in requirements["certifications_mentioned"]:
            if any(c.lower() in cert.lower() for cert in CANDIDATE_PROFILE["certifications"]):
                actions.append(f"Highlight {c} certification prominently")
    if not actions:
        actions.append("Standard CV — no critical tailoring needed")

    for i, action in enumerate(actions, 1):
        report.append(f"\n  {i}. {action}")

    report.append("\n" + "=" * 60)
    report.append("  END OF REPORT — CV/JD Matching Agent v1.0")
    report.append("  Built by Saksham Kapahi | October 2026")
    report.append("=" * 60 + "\n")

    full_report = "\n".join(report)
    print(full_report)
    return full_report


# ── Demo: Run against EY Business Transformation JD ───────────────────────────
if __name__ == "__main__":
    SAMPLE_JD = """
    Senior Consultant – Business Transformation
    EY Ireland

    We are looking for a Senior Consultant to join our Business Transformation practice.

    Required Skills:
    - Minimum 3 years of experience in business analysis, process mapping, or transformation
    - Strong stakeholder management and communication skills
    - Experience with requirements gathering and gap analysis
    - Proficiency in Excel and PowerPoint for reporting and presentations
    - Knowledge of project management methodologies (Agile, Waterfall, PRINCE2)
    - Experience with Jira or similar project tracking tools
    - Ability to facilitate workshops and drive consensus

    Preferred Skills:
    - Experience with Power BI, Tableau or similar BI tools
    - SQL knowledge for data querying
    - Salesforce CRM experience
    - Change management certification

    Qualifications:
    - Bachelor's degree or higher in Business, IT, or related field
    - PRINCE2 or PMP certification advantageous

    Key Responsibilities:
    - Gather and document business requirements through interviews and workshops
    - Develop process maps and BRDs to support change initiatives
    - Deliver structured gap analysis and business cases to senior stakeholders
    - Support UAT and solution validation activities
    - Manage project risks and maintain RAID logs
    """

    generate_report(SAMPLE_JD, role_title="Senior Consultant – Business Transformation (EY Ireland)")