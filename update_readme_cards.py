import re

with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

GH = 'https://github.com/Thibault-GAREL/'
CARD_W = 250
IMG_H_FEATURED = 140  # = hauteur SVG featured (min_h=140)
IMG_H_GROUP    = 180  # = hauteur SVG group    (min_h=180)

def pair_html(projects, img_folder, img_h):
    parts = []
    for card, img, link, alt in projects:
        # height uniquement → largeur calculée automatiquement depuis le ratio source (3:2)
        # → aucune distorsion. Exemple : h=140 → w=210, h=180 → w=270
        parts.append(
            f'<a href="{link}"><img src="{img_folder}/{img}" height="{img_h}" alt="{alt}"/></a>'
            f'<a href="{link}"><img src="badges/cards/{card}.svg" width="{CARD_W}"/></a>'
        )
    return '&emsp;&emsp;'.join(parts)

def section_html(projects, img_folder, img_h):
    rows = []
    for i in range(0, len(projects), 2):
        pair = projects[i:i+2]
        rows.append(pair_html(pair, img_folder, img_h))
    return '<p>\n' + '<br><br>\n'.join(rows) + '\n</p>\n'

CATEGORIES = [
    ('### 🤖 Generative AI', [
        ('gen_ai_gan',  'gen_ai_gan.png',           GH + 'Image_generator_GAN',         'GAN'),
        ('gen_ai_lm',   'gen_ai_language_models.png',GH + 'Language_Models',             'LMs'),
        ('gen_ai_rag',  'gen_ai_rag.gif',            GH + 'RAG_pdf',                    'RAG'),
        ('gen_ai_clip', 'gen_ai_clip_embedding.png', GH + 'CLIP_Embedding_Tools',        'CLIP'),
    ]),
    ('### 🧠 Neural Networks', [
        ('neural_scratch', 'neural_net_from_scratch.gif', GH + 'Neural_Network_from_Scratch', 'Neural Networks'),
    ]),
    ('### 🎮 Reinforcement Learning\n\n#### 🌳 Decision Tree', [
        ('rl_snake_dt',     'rl_snake_decision_tree.gif', GH + 'AI_snake_decision_tree_version', 'Snake DT'),
    ]),
    ('#### 🧬 Genetic Algorithm', [
        ('rl_snake_ga',     'rl_snake_genetic.gif',   GH + 'AI_snake_genetic_version',   'Snake GA'),
        ('rl_driving_ga',   'rl_driving_genetic.gif', GH + 'AI_driving_genetic_version',  'Driving GA'),
        ('rl_walking_ga',   'rl_walking_genetic.png', GH + 'test_box2D_pygame',           'Walking GA'),
    ]),
    ('#### 📈 Q-Learning', [
        ('rl_q_learning',  'rl_q_learning.gif',  GH + 'Q-Learning',           'Q-Learning'),
        ('rl_snake_dql',   'rl_snake_dql.gif',   GH + 'AI_snake_DQN_version', 'Snake DQL'),
        ('rl_driving_dql', 'rl_driving_dql.gif', GH + 'AI_driving_DQN_version','Driving DQL'),
    ]),
    ('#### 🎯 PPO', [
        ('rl_snake_ppo', 'rl_snake_ppo.gif',   GH + 'AI_snake_PPO_version', 'Snake PPO'),
        ('rl_sc2',       'rl_starcraft2.gif',   GH + 'AI-StarCraft2-VLM-RL', 'SC2 AI'),
    ]),
    ('#### 🎮 Unity ML-Agents', [
        ('rl_unity_move',   'rl_unity_move.gif',   GH + 'Unity_move',   'Unity Move'),
        ('rl_unity_greedy', 'rl_unity_greedy.gif', GH + 'Unity_greedy', 'Unity Greedy'),
        ('rl_unity_drive',  'rl_unity_drive.gif',  GH + 'Unity_drive',  'Unity Drive'),
    ]),
    ('### 🎙️ Speech Recognition', [
        ('speech_asr', 'speech_asr.png', GH + 'Speech_recognition', 'ASR'),
    ]),
    ('### 🦾 Robotics', [
        ('robotics_bot', 'robotics_chatbot_bot.gif', GH + 'Bot_controlled_by_a_Chatbot_RAG', 'Robotics RAG'),
    ]),
]

ANNEXE_CATEGORIES = [
    ('### 🕹️ Games', [
        ('game_snake',    'game_snake.gif',          GH + 'snake_game',               'Snake Game'),
        ('game_driving',  'game_driving.gif',        GH + 'driving_game',             'Driving Game'),
        ('game_sandbox',  'game_human_sandbox.gif',  GH + 'human_sandbox',            'Human Sandbox'),
        ('game_starwars', 'game_star_wars.png',      GH + 'Game_ECE_World_Minigame',  'Star Wars'),
        ('game_maze',     'game_maze_asterix.png',   GH + 'Game_maze_Asterix-Obelix','Asterix Maze'),
    ]),
    ('### ⚙️ Physics Simulation', [
        ('physics_gravity',    'physics_gravity.gif',             GH + 'gravity_simulation',    'Gravity'),
        ('physics_attraction', 'physics_attraction_repulsion.gif',GH + 'Attraction_repulsion',  'Attraction'),
        ('physics_muscular',   'physics_muscular_simulation.png', GH + '2D-Muscular-Simulation','Muscular'),
    ]),
    ('### ⚡ n8n Automation', [
        ('n8n_whatsapp', 'n8n_whatsapp_ai.png',  GH + 'n8n_Whatsapp_LLM',        'WhatsApp AI'),
        ('n8n_mail',     'n8n_mail_sorting.png', GH + 'n8n_smart_mail_labeling', 'Mail Sorting'),
    ]),
    ('### 📊 Data Analysis', [
        ('data_iss', 'data_iss_analysis.jpg', GH + 'ISS_Analysis_Spark', 'ISS Analysis'),
    ]),
]

GROUP_PROJECTS = [
    ('group_cnd',      'group_hackathon_cnd.png',      'https://www.linkedin.com/feed/update/urn:li:activity:7397600929350336512/', 'Hackathon CND'),
    ('group_ppe',      'group_ppe_smart_contract.jpg', 'https://www.ece.fr/la-pedagogie-par-projets/', 'PPE Smart Contract'),
    ('group_resilient','group_resilient_ai.jpg',       'https://www.sustainableaicoalition.org/resilient-ai-challenge/', 'Resilient AI'),
]

GROUP_LINKS = {
    'group_cnd': (
        '<sub>'
        '<a href="https://github.com/Rqbln/dirisi25-hackathon-frontend">Frontend</a> · '
        '<a href="https://github.com/Rqbln/dirisi25-hackathon-backend">Backend</a> · '
        '<a href="https://github.com/Thibault-GAREL/ILab-Hackaton_CND-Phase2-Cyberattack_AI_detection">Phase 2 — Cyberattack Detection</a>'
        '</sub>'
    ),
    'group_ppe': (
        '<sub>'
        '<a href="https://github.com/Thibault-GAREL/PPE_LLM_test_Smart_contract">LLM Test</a> · '
        '<a href="https://github.com/Thibault-GAREL/PPE_LoRa_Smart_contract">LoRA Fine-tune</a> · '
        '<a href="https://github.com/axelbrons/graphs-ppe">Graphs</a>'
        '</sub>'
    ),
    'group_resilient': (
        '<sub>'
        '<a href="https://github.com/Thibault-GAREL">Repo (WIP)</a>'
        '</sub>'
    ),
}

# Build Featured Projects section
new_featured = '## ✨ Featured Projects\n\n'
for header, projects in CATEGORIES:
    new_featured += header + '\n\n'
    new_featured += section_html(projects, 'Logo_Featured_Projects', IMG_H_FEATURED) + '\n'

# Annexe : Games, Physics, n8n, Data
new_featured += '<details>\n<summary><h3>🗂️ Projets Annexes (click me)</h3></summary>\n\n'
for header, projects in ANNEXE_CATEGORIES:
    new_featured += header + '\n\n'
    new_featured += section_html(projects, 'Logo_Featured_Projects', IMG_H_FEATURED) + '\n'
new_featured += '</details>'

new_featured = new_featured.rstrip('\n')

# Build Group Projects section
new_group = '## 👥 Group Projects\n\n'
new_group += section_html(GROUP_PROJECTS, 'Logo_Group_Projects', IMG_H_GROUP)
for card, img, link, alt in GROUP_PROJECTS:
    if card in GROUP_LINKS:
        new_group += GROUP_LINKS[card] + '\n\n'
new_group = new_group.rstrip('\n')

# Patterns — \n## suivi d'un espace (h2 uniquement, pas h3 qui commence par ###)
featured_pattern = re.compile(
    r'## ✨ Featured Projects\n.*?(?=\n## )',
    re.DOTALL
)
group_pattern = re.compile(
    r'## 👥 Group Projects\n.*?(?=\n## )',
    re.DOTALL
)

new_content = featured_pattern.sub(new_featured, content)
new_content = group_pattern.sub(new_group, new_content)

if new_content == content:
    print("ERREUR : aucune section remplacée, vérifier les patterns")
else:
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("README mis à jour avec succès !")
