"""Generate dark-mode SVG cards (titre + description) for each project.

Output: `badges/cards/<name>.svg`. Run `generate_light_cards.py` afterwards to derive
light variants, and `add_shadows.py` to apply drop shadows.

Style note: committed SVGs use `fill="#ffffff"` for the label and `font-size="12"` for
description (see CLAUDE.md §"Bugs et désynchronisations connus"). This script matches
that style; do NOT revert without updating all existing cards.
"""
import os

from categories import CATEGORIES as CATS

os.makedirs('badges/cards', exist_ok=True)

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
EFONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI Emoji', 'Segoe UI', sans-serif"
BG = "#0d1117"
WHITE = "#f0f6fc"
GREY = "#8b949e"
W = 200

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def wrap(text, max_chars):
    lines, cur = [], ''
    for word in text.split():
        if len(cur) + len(word) + (1 if cur else 0) <= max_chars:
            cur += (' ' if cur else '') + word
        else:
            if cur: lines.append(cur)
            cur = word
    if cur: lines.append(cur)
    return lines

def svg(cat_key, title, desc, link_labels, members=None, min_h=140):
    color, label = CATS[cat_key][1], CATS[cat_key][0]
    title_lines = wrap(title, 21)
    desc_lines  = wrap(desc,  29)

    # Calcul hauteur
    h = 14 + 4 + len(title_lines)*16 + 6 + len(desc_lines)*13 + 10
    if members:
        h += 10 + len(members) * 12
    h += len(link_labels) * 14 + 14
    h = max(min_h, h)

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}">')
    out.append(f'  <rect width="{W}" height="{h}" rx="12" fill="{BG}"/>')
    out.append(f'  <rect width="{W}" height="{h}" rx="12" fill="none" stroke="{color}" stroke-width="1" opacity="0.35"/>')
    out.append(f'  <rect width="4" height="{h}" rx="2" fill="{color}"/>')

    y = 22
    bw = min(len(label) * 6 + 14, W - 20)
    out.append(f'  <rect x="14" y="{y-13}" width="{bw}" height="15" rx="7" fill="{color}" opacity="0.2"/>')
    # Label rendered in white over the tinted badge background (matches committed SVGs).
    out.append(f'  <text x="20" y="{y}" font-family="{EFONT}" font-size="9" fill="#ffffff">{esc(label)}</text>')

    y += 18
    for tl in title_lines:
        out.append(f'  <text x="14" y="{y}" font-family="{FONT}" font-size="13" font-weight="700" fill="{WHITE}">{esc(tl)}</text>')
        y += 16

    y += 6
    for dl in desc_lines:
        # Description at font-size 12 (committed style); the wrap() limit of 29 chars is tuned for this.
        out.append(f'  <text x="14" y="{y}" font-family="{FONT}" font-size="12" fill="{GREY}">{esc(dl)}</text>')
        y += 13

    if members:
        y += 10
        out.append(f'  <text x="14" y="{y}" font-family="{FONT}" font-size="9" font-weight="600" fill="{color}" opacity="0.9">Team :</text>')
        y += 13
        for m in members:
            out.append(f'  <text x="14" y="{y}" font-family="{FONT}" font-size="9" fill="{GREY}">{esc(m)}</text>')
            y += 12

    y += 10
    for lbl in link_labels:
        out.append(f'  <text x="14" y="{y}" font-family="{FONT}" font-size="10" fill="{color}">→ {esc(lbl)}</text>')
        y += 14

    out.append('</svg>')
    return '\n'.join(out)

GH = 'https://github.com/Thibault-GAREL/'

projects = [
    # (filename, cat, title, desc, [link_labels], members)
    # Research paper: the three cards of the OPENER section. Their logo tiles are
    # not plain images, so they are built by make_research_thumbs.py, which reads
    # these very entries to stay the single source of truth.
    ('research_opener_paper', 'research', 'OPENER Paper',  'Open NER from pre-trained bricks. 40.1 AMI e2e, 39.5 zero-shot.',        ['Google Scholar'], None),
    ('research_opener_model', 'research', 'OPENER Models', 'opener-zs and opener-sup, ready to use from the HF Hub.',                ['Hugging Face'],   None),
    ('research_opener_code',  'research', 'OPENER Code',   'Full pipeline and the 13-dataset benchmark on quality, latency, energy.', ['GitHub'],        None),

    ('gen_ai_gan',           'gen_ai',   'Image Generator GAN',           'Generate realistic images using a GAN trained from scratch.',                    ['GitHub'],  None),
    ('gen_ai_lm',            'gen_ai',   'Language Models',               'Bigram & Transformer language models built from scratch (GPT-style).',            ['GitHub'],  None),
    ('gen_ai_rag',           'gen_ai',   'RAG — PDF Chatbot',             'Chatbot that reads and answers questions from any PDF using RAG.',                ['GitHub'],  None),
    ('gen_ai_finetune_sd',   'gen_ai',   'SD 1.5 LoRA Fine-tune',         'Fine-tuned SD 1.5 with LoRA on 15 chibi self-portraits. Trained on RunPod for <1€.', ['GitHub'],  None),
    ('gen_ai_clip',          'gen_ai',   'CLIP Embedding Tools',          'Opposite embedding finder and arithmetic operations using CLIP.',                  ['GitHub'],  None),

    ('neural_scratch',       'neural',   'Neural Networks from Scratch',  'Full neural network library built from scratch in C and Excel.',                  ['GitHub'],  None),
    ('neural_asr',           'neural',   'Automatic Speech Recognition',  'School project — ASR system built from scratch.',                                 ['GitHub'],  None),

    ('rl_snake_dt',          'rl_dt',    'Snake AI — Decision Tree',      'Snake agent using a decision tree to choose its next move.',                      ['GitHub'],  None),
    ('rl_snake_ga',          'rl_ga',    'Snake AI — Genetic Algorithm',  'Snake agent evolved through generations with a genetic algorithm.',               ['GitHub'],  None),
    ('rl_driving_ga',        'rl_ga',    'Driving AI — Genetic Algorithm','Self-driving car trained with a genetic algorithm.',                              ['GitHub'],  None),
    ('rl_walking_ga',        'rl_ga',    'Walking AI — Genetic Algorithm','AI learning to walk using Box2D physics engine and genetic algorithm.',           ['GitHub'],  None),
    ('rl_q_learning',        'rl_ql',    'Q-Learning',                    'Agent finding the optimal path in a grid world using Q-Learning.',                ['GitHub'],  None),
    ('rl_snake_dql',         'rl_ql',    'Snake AI — Deep Q-Learning',    'Snake agent trained with a Deep Q-Network (DQN).',                               ['GitHub'],  None),
    ('rl_driving_dql',       'rl_ql',    'Driving AI — Deep Q-Learning',  'Self-driving car trained with a Deep Q-Network (DQN).',                          ['GitHub'],  None),
    ('rl_snake_ppo',         'rl_ppo',   'Snake AI — PPO',                'Snake agent trained with Proximal Policy Optimization.',                          ['GitHub'],  None),
    ('rl_sc2',               'rl_ppo',   'StarCraft 2 AI — PPO + VLM',   'SC2 AI combining Vision-Language Model with PPO reinforcement learning.',         ['GitHub'],  None),
    ('rl_snake_wm',          'rl_wm',    'Snake AI — World Model',        'JEPA world model built from scratch. Plans in latent space, no learned policy.',  ['GitHub'],  None),
    ('rl_unity_move',        'rl_unity', 'Unity AI — Move',               'Unity agent learning to move towards a target using ML-Agents.',                  ['GitHub'],  None),
    ('rl_unity_greedy',      'rl_unity', 'Unity AI — Greedy',             'Unity agent learning to collect rewards greedily using ML-Agents.',               ['GitHub'],  None),
    ('rl_unity_drive',       'rl_unity', 'Unity AI — Drive',              'Unity agent learning to drive through a maze using ML-Agents.',                   ['GitHub'],  None),

    ('robotics_bot',         'robotics', 'Bot Controlled by ChatBot RAG', 'Raspberry Pi robot controlled by a RAG-based chatbot via voice commands.',        ['GitHub'],  None),

    ('game_snake',           'games',    'Snake Game',                    'Classic Snake game built in Python with Pygame.',                                 ['GitHub'],  None),
    ('game_driving',         'games',    'Driving Game',                  'Top-down driving game built as training environment for RL agents.',               ['GitHub'],  None),
    ('game_sandbox',         'games',    'Human Sandbox',                 'Natural selection simulation engine with evolving agents.',                        ['GitHub'],  None),
    ('game_starwars',        'games',    'Star Wars Park (C)',             'School project — Star Wars themed park with mini-games in C.',                    ['GitHub'],  None),
    ('game_maze',            'games',    'Asterix & Obelix Maze (C)',     'School project — Maze game featuring Asterix & Obelix in C.',                     ['GitHub'],  None),

    ('physics_gravity',      'physics',  'Gravity Simulation 2D',         '2D gravity simulation with multiple bodies interacting.',                         ['GitHub'],  None),
    ('physics_attraction',   'physics',  'Attraction / Repulsion',         'Particle simulation with attraction and repulsion forces.',                       ['GitHub'],  None),
    ('physics_muscular',     'physics',  '2D Muscular Simulation',         '2D simulation of muscles and tendons with a physics engine.',                    ['GitHub'],  None),
    ('physics_general_relativity', 'physics', 'Gravity & Relativity',         'Newton vs General Relativity (Schwarzschild): Mercury precession, light deflection.', ['GitHub'],  None),

    ('n8n_whatsapp',         'n8n',      'WhatsApp AI Assistant',         'Local LLM accessible via WhatsApp using n8n automation.',                         ['GitHub'],  None),
    ('n8n_mail',             'n8n',      'Smart Mail Labeling',           'Automatic and intelligent mail sorting with AI labeling via n8n.',                 ['GitHub'],  None),

    ('data_iss',             'data',     'ISS Real-Time Analysis',        'School project — Real-time ISS data analysis with Apache Spark.',                  ['GitHub'],  None),
]

group_projects = [
    ('group_cnd', 'group', 'Hackathon with the CND',
     'Detects anomalies & breakdowns in French army logs. Phase 1: ranked 3rd out of 11 engineering schools. Phase 2: ranked 1st at finals — hybrid AI cyberattack detection.',
     ['Frontend', 'Backend', 'Phase 2 — Cyberattack Detection'],
     ['T. Garel · A. de Vulpian · A. Brons', 'R. Querieaux · Z. Amzil']),

    ('group_ppe', 'group', 'PPE — Smart Contract LLM',
     'LLM benchmarking & LoRA fine-tuning of TinyLlama on Solidity smart contracts.',
     ['LLM Test', 'LoRA Fine-tune', 'Graphs'],
     ['T. Garel · A. Brons · V. Kocijancic', 'H. Riviere · A. Goudedranche · O. El Alami']),

    ('group_resilient', 'group', 'Resilient AI Challenge',
     'Compressing Gemma 4 to make it more efficient and resilient.',
     ['Tests', 'Dataset & Benchmark'],
     ['T. Garel · A. Brons · M. Lacombe', 'J. Houngbadji · D. Sow Achta · D. Laouedj', '⭐ B. P. Bhuyan (researcher)']),
]

if __name__ == '__main__':
    for fname, cat, title, desc, links, members in projects:
        content = svg(cat, title, desc, links, members, min_h=140)
        with open(f'badges/cards/{fname}.svg', 'w', encoding='utf-8') as f:
            f.write(content)

    for fname, cat, title, desc, links, members in group_projects:
        content = svg(cat, title, desc, links, members, min_h=180)
        with open(f'badges/cards/{fname}.svg', 'w', encoding='utf-8') as f:
            f.write(content)

    print(f'OK — {len(projects)} cartes projets + {len(group_projects)} cartes groupe générées')
