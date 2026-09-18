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
        "date": "Apr - Aug 2026",
        "icon": "🔬",
        "title": "AI Research Intern",
        "tag": "LyRIDS · ECE",
        "desc": ["Improving NLP models on low-resource domains · Paris"],
        "accent": "#6e40c9",
    },
    {
        "date": "2025 - 2027",
        "icon": "🧠",
        "title": "AI Maker",
        "tag": "Intelligence Lab · ECE",
        "desc": [
            "R&D in the AI lab of ECE Paris",
            "CND Hackathon (French defence): 1st place, AI detecting cyberattacks on the army",
            "Resilient AI Hackathon (France, India, UNESCO): compressing Google's Gemma 4",
            "Created technical training courses on how AI works",
        ],
        "accent": "#2563eb",
    },
    {
        "date": "Jan 2025",
        "icon": "🏭",
        "title": "AI Engineer Intern",
        "tag": "Toray Films Europe",
        "desc": ["Studied, mapped & tested AI tools to optimize their use in the company · Lyon"],
        "accent": "#ea580c",
    },
    {
        "date": "Jan 2024",
        "icon": "⚙️",
        "title": "Embedded Software Intern",
        "tag": "Dakatech",
        "desc": ["Reorganized & optimized their embedded code: +20-30% battery life · Lyon"],
        "accent": "#0d9488",
    },
    {
        "date": "Summer 2023",
        "icon": "📅",
        "title": "Summer Job",
        "tag": "Solvay",
        "desc": ["Programmed an automatic scheduling tool on my own · Lyon"],
        "accent": "#6b7280",
    },
    {
        "date": "Summer 2022",
        "icon": "📊",
        "title": "Summer Job",
        "tag": "Solvay",
        "desc": ["Data reorganization · Lyon"],
        "accent": "#6b7280",
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
