"""Single source of truth for project categories: emoji label + accent color.

Used by:
- generate_cards.py (svg label + accent border/shadow)
- round_logos.py (logo shadow color)
- add_shadows.py (card shadow color, via SVG stroke probe)

Each entry: category_key → (emoji_label, accent_hex).
Logo file naming convention: `<category_key>_<project_id>.{png,gif}` (e.g. `gen_ai_gan.png`).
"""

CATEGORIES: dict[str, tuple[str, str]] = {
    'research': ('📄 RESEARCH PAPER',    '#d4af37'),
    'gen_ai':   ('🤖 GENERATIVE AI',     '#6e40c9'),
    'neural':   ('🧠 NEURAL NETWORKS',   '#2563eb'),
    'rl_dt':    ('🌳 DECISION TREE',     '#22c55e'),
    'rl_ga':    ('🧬 GENETIC ALGORITHM', '#16a34a'),
    'rl_ql':    ('📈 Q-LEARNING',        '#10b981'),
    'rl_ppo':   ('🎯 PPO',               '#059669'),
    'rl_unity': ('🎮 UNITY ML-AGENTS',   '#0f766e'),
    'speech':   ('🎙 SPEECH RECOGNITION', '#ea580c'),
    'robotics': ('🦾 ROBOTICS',          '#dc2626'),
    'games':    ('🕹 GAMES',             '#0891b2'),
    'physics':  ('⚙ PHYSICS SIMULATION', '#0d9488'),
    'n8n':      ('⚡ APPLIED AI WORKFLOWS', '#db2777'),
    'data':     ('📊 DATA ANALYSIS',      '#d97706'),
    'group':    ('👥 GROUP PROJECT',      '#00b4c2'),
}


# Filename-prefix → accent mapping for round_logos.py
# (some logos don't match the category key directly: e.g. `rl_snake_genetic` belongs to `rl_ga`.)
# Order matters: most-specific first.
ACCENT_BY_PREFIX: dict[str, str] = {
    'research':          CATEGORIES['research'][1],
    'gen_ai':            CATEGORIES['gen_ai'][1],
    'neural':            CATEGORIES['neural'][1],
    'rl_snake_decision': CATEGORIES['rl_dt'][1],
    'rl_snake_ppo':      CATEGORIES['rl_ppo'][1],
    'rl_snake_dql':      CATEGORIES['rl_ql'][1],
    'rl_snake_genetic':  CATEGORIES['rl_ga'][1],
    'rl_snake':          CATEGORIES['rl_ql'][1],
    'rl_driving_dql':    CATEGORIES['rl_ql'][1],
    'rl_driving':        CATEGORIES['rl_ga'][1],
    'rl_walking':        CATEGORIES['rl_ga'][1],
    'rl_q_learning':     CATEGORIES['rl_ql'][1],
    'rl_starcraft':      CATEGORIES['rl_ppo'][1],
    'rl_sc2':            CATEGORIES['rl_ppo'][1],
    'rl_unity':          CATEGORIES['rl_unity'][1],
    'speech':            CATEGORIES['speech'][1],
    'robotics':          CATEGORIES['robotics'][1],
    'game':              CATEGORIES['games'][1],
    'physics':           CATEGORIES['physics'][1],
    'n8n':               CATEGORIES['n8n'][1],
    'data':              CATEGORIES['data'][1],
    'group':             CATEGORIES['group'][1],
}


def get_accent_by_prefix(stem: str, default: str = '#888888') -> str:
    """Resolve accent color from a logo filename stem (e.g. 'rl_snake_genetic')."""
    stem = stem.lower()
    for prefix, color in ACCENT_BY_PREFIX.items():
        if stem.startswith(prefix):
            return color
    return default
