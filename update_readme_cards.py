import re

with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

GH = 'https://github.com/Thibault-GAREL/'
IMG_W = 150
CARD_W = 250

def row(projects, img_folder):
    cells = []
    for p in projects:
        card, img, link, alt = p
        cells.append(
            f'    <td align="center" width="{IMG_W+10}">\n'
            f'      <a href="{link}"><img src="{img_folder}/{img}" width="{IMG_W}" alt="{alt}"/></a>\n'
            f'    </td>'
        )
        cells.append(
            f'    <td width="{CARD_W+10}">\n'
            f'      <a href="{link}"><img src="badges/cards/{card}.svg" width="{CARD_W}"/></a>\n'
            f'    </td>'
        )
    # Pad to 2 items
    while len(projects) < 2:
        cells.append(f'    <td width="{IMG_W+10}"></td>')
        cells.append(f'    <td width="{CARD_W+10}"></td>')
        projects = list(projects) + [None]
    # Insert spacer between pair 1 and pair 2
    cells.insert(2, '    <td width="20"></td>')
    return '  <tr>\n' + '\n'.join(cells) + '\n  </tr>'

def table(projects, img_folder):
    rows = []
    for i in range(0, len(projects), 2):
        pair = [p for p in projects[i:i+2] if p is not None]
        if rows:
            rows.append('  <tr><td colspan="5"><br></td></tr>')
        rows.append(row(pair, img_folder))
    return '<table>\n' + '\n'.join(rows) + '\n</table>\n'

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
    ('### 🎮 Reinforcement Learning', [
        ('rl_snake_dt',     'rl_snake_decision_tree.gif', GH + 'AI_snake_decision_tree_version', 'Snake DT'),
        ('rl_snake_ga',     'rl_snake_genetic.gif',       GH + 'AI_snake_genetic_version',        'Snake GA'),
        ('rl_driving_ga',   'rl_driving_genetic.gif',     GH + 'AI_driving_genetic_version',      'Driving GA'),
        ('rl_walking_ga',   'rl_walking_genetic.png',     GH + 'test_box2D_pygame',               'Walking GA'),
        ('rl_q_learning',   'rl_q_learning.gif',          GH + 'Q-Learning',                     'Q-Learning'),
        ('rl_snake_dql',    'rl_snake_dql.gif',           GH + 'AI_snake_DQN_version',            'Snake DQL'),
        ('rl_driving_dql',  'rl_driving_dql.gif',         GH + 'AI_driving_DQN_version',          'Driving DQL'),
        ('rl_snake_ppo',    'rl_snake_ppo.gif',           GH + 'AI_snake_PPO_version',            'Snake PPO'),
        ('rl_sc2',          'rl_starcraft2.gif',           GH + 'AI-StarCraft2-VLM-RL',            'SC2 AI'),
        ('rl_unity_move',   'rl_unity_move.gif',          GH + 'Unity_move',                      'Unity Move'),
        ('rl_unity_greedy', 'rl_unity_greedy.gif',        GH + 'Unity_greedy',                    'Unity Greedy'),
        ('rl_unity_drive',  'rl_unity_drive.gif',         GH + 'Unity_drive',                     'Unity Drive'),
    ]),
    ('### 🎙️ Speech Recognition', [
        ('speech_asr', 'speech_asr.png', GH + 'Speech_recognition', 'ASR'),
    ]),
    ('### 🦾 Robotics', [
        ('robotics_bot', 'robotics_chatbot_bot.gif', GH + 'Bot_controlled_by_a_Chatbot_RAG', 'Robotics RAG'),
    ]),
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
    ('group_ppe',      'group_ppe_smart_contract.png', 'https://www.ece.fr/la-pedagogie-par-projets/', 'PPE Smart Contract'),
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
featured_lines = [
    '<details>',
    '<summary> <h2> ✨ Featured Projects (click me)</h2> </summary>',
    '',
]
for header, projects in CATEGORIES:
    featured_lines.append(header)
    featured_lines.append('')
    featured_lines.append(table(projects, 'Logo_Featured_Projects'))

featured_lines.append('</details>')
new_featured = '\n'.join(featured_lines)

# Build Group Projects section
group_lines = [
    '<details>',
    '<summary> <h2> 👥 Group Projects (click me)</h2> </summary>',
    '',
    table(GROUP_PROJECTS, 'Logo_Group_Projects'),
]

# Sub-links for each group project
for card, img, link, alt in GROUP_PROJECTS:
    if card in GROUP_LINKS:
        group_lines.append(GROUP_LINKS[card])
        group_lines.append('')

group_lines.append('</details>')
new_group = '\n'.join(group_lines)

# Replace in README
# Find and replace Featured Projects section
featured_pattern = re.compile(
    r'<details>\s*\n<summary>\s*<h2>\s*✨ Featured Projects.*?</details>',
    re.DOTALL
)
group_pattern = re.compile(
    r'<details>\s*\n<summary>\s*<h2>\s*👥 Group Projects.*?</details>',
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
