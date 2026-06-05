"""Generate the vertical 'Professional Experience' timeline SVG (dark + light).

Reuses the shared rendering engine from `generate_timeline.py` (same rounded style,
accent left bar, no drop shadow, dark/light switch). Most recent role on top.

Output:
  badges/experience_timeline.svg        (dark)
  badges/experience_timeline_light.svg  (light)
"""

from generate_timeline import render

# Most recent -> oldest (top -> bottom). Same dict schema as the academic timeline.
EXPERIENCE = [
    {
        "date": "Apr 2026 - Present",
        "icon": "🔬",
        "title": "AI Research Intern",
        "tag": "LyRIDS · ECE",
        "desc": [
            "Greater Paris · On-site · R&D internship",
            "NLP & Named Entity Recognition on low-resource domains",
            "(programming languages, medical corpora, technical docs)",
            "Goal: robust methods aimed at a scientific publication",
        ],
        "accent": "#6e40c9",
    },
    {
        "date": "Sep 2025 - Present",
        "icon": "🧠",
        "title": "AI Maker",
        "tag": "Intelligence Lab · ECE",
        "desc": [
            "Greater Paris",
            "AI hackathons: fast prototyping under time constraints",
            "Authored advanced AI training content",
            "R&D on new AI architectures",
        ],
        "accent": "#2563eb",
    },
    {
        "date": "Jan 2025",
        "icon": "🏭",
        "title": "AI Engineer Intern",
        "tag": "Toray Films Europe",
        "desc": [
            "Lyon, France · On-site",
            "Studied, mapped & experimented with AI tools to optimize",
            "their usage and foster AI knowledge across the company",
        ],
        "accent": "#ea580c",
    },
    {
        "date": "Jan 2024",
        "icon": "⚙️",
        "title": "Embedded Software Engineer Intern",
        "tag": "Dakatech",
        "desc": [
            "Lyon, France · On-site · Autonomous Coding Project",
            "Reorganized & simplified the embedded codebase",
            "→ 20-30% improvement in battery autonomy",
        ],
        "accent": "#0d9488",
    },
]


if __name__ == "__main__":
    import os
    os.makedirs("badges", exist_ok=True)
    with open("badges/experience_timeline.svg", "w", encoding="utf-8") as f:
        f.write(render(EXPERIENCE, "dark"))
    with open("badges/experience_timeline_light.svg", "w", encoding="utf-8") as f:
        f.write(render(EXPERIENCE, "light"))
    print("OK - badges/experience_timeline.svg + _light.svg generated")
