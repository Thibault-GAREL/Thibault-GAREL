"""Régénère les sections Featured Projects et Group Projects du README.md.

Le format produit doit correspondre exactement à la version actuelle :
- Conteneur : `<p align="center">` (pas `<p>`)
- Logos : `Logo_Featured_Projects_compressed/` (pas `Logo_Featured_Projects/`)
- GIFs : wrap `<picture>` avec variante `_dark.gif` pour dark mode
- SVG cards : wrap `<picture>` avec variante `_light.svg` pour light mode
- Séparateurs : `&emsp;` entre paires de projets, `<br><br>` entre rangées
- Sous-headers : `<h3 align="center">` pour catégories, `#### **...**` pour sous-catégories de RL

Synchronisé manuellement avec README.md. Si tu changes la structure du README, mets aussi ce
script à jour, sinon il écrasera la mise en forme.
"""
import re
from pathlib import Path

GH = 'https://github.com/Thibault-GAREL/'
LOGO_DIR = 'Logo_Featured_Projects_compressed'
GROUP_LOGO_DIR = 'Logo_Group_Projects_compressed'
CARD_W = 200
GROUP_CARD_W = 400
IMG_H = 140


def card_html(card_name: str, logo_name: str, link: str, alt: str, card_w: int) -> str:
    """One project anchor (logo + svg description). Wraps GIFs and SVG cards in <picture>."""
    if logo_name.lower().endswith('.gif'):
        stem = logo_name.rsplit('.', 1)[0]
        logo_block = (
            f'<picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="{LOGO_DIR}/{stem}_dark.gif"/>'
            f'<img src="{LOGO_DIR}/{logo_name}" height="{IMG_H}" alt="{alt}"/>'
            f'</picture>'
        )
    else:
        logo_block = f'<img src="{LOGO_DIR}/{logo_name}" height="{IMG_H}" alt="{alt}"/>'

    svg_block = (
        f'<picture>'
        f'<source media="(prefers-color-scheme: light)" srcset="badges/cards/{card_name}_light.svg"/>'
        f'<img src="badges/cards/{card_name}.svg" width="{card_w}"/>'
        f'</picture>'
    )
    return f'<a href="{link}">{logo_block}{svg_block}</a>'


def section_html(projects, header: str, card_w: int = CARD_W) -> str:
    """Build one section: header + <p align="center"> with 2 projects per row."""
    rows = []
    for i in range(0, len(projects), 2):
        pair = projects[i:i + 2]
        rows.append('&emsp;'.join(card_html(*proj, card_w) for proj in pair))
    body = '<br><br>\n'.join(rows)
    return f'{header}\n\n---\n\n<p align="center">\n{body}\n</p>\n'


# ────────────────────────────────────────────────────────────────────────────────
# Featured projects (in display order)
# ────────────────────────────────────────────────────────────────────────────────

FEATURED_SECTIONS = [
    ('<h3 align="center">🤖 Generative AI</h3>', [
        ('gen_ai_gan',          'gen_ai_gan.png',            GH + 'Image_generator_GAN',                   'GAN'),
        ('gen_ai_lm',           'gen_ai_language_models.png', GH + 'Language_Models',                       'LMs'),
        ('gen_ai_rag',          'gen_ai_rag.gif',            GH + 'RAG_pdf',                               'RAG'),
        ('gen_ai_finetune_sd',  'gen_ai_lora.png',           GH + 'ILab_Formation_Fine-tuning',            'SD LoRA'),
        ('gen_ai_clip',         'gen_ai_clip_embedding.png', GH + 'CLIP_Embedding_Tools',                  'CLIP'),
    ]),
    ('<h3 align="center">🧠 Neural Networks</h3>', [
        ('neural_scratch', 'neural_net_from_scratch.gif', GH + 'Neural_Network_from_Scratch', 'Neural Networks'),
        ('neural_asr',     'neural_asr.png',              GH + 'Speech_recognition',          'ASR'),
    ]),
    ('<h3 align="center">🎮 Reinforcement Learning</h3>\n\n---\n\n#### **🌳 Decision Tree**', [
        ('rl_snake_dt', 'rl_snake_decision_tree.gif', GH + 'AI_snake_decision_tree_version', 'Snake DT'),
    ]),
    ('#### **🧬 Genetic Algorithm**', [
        ('rl_snake_ga',   'rl_snake_genetic.gif',   GH + 'AI_snake_genetic_version',    'Snake GA'),
        ('rl_driving_ga', 'rl_driving_genetic.gif', GH + 'AI_driving_genetic_version',  'Driving GA'),
        ('rl_walking_ga', 'rl_walking_genetic.png', GH + 'test_box2D_pygame',           'Walking GA'),
    ]),
    ('#### **📈 Q-Learning**', [
        ('rl_q_learning',  'rl_q_learning.gif',  GH + 'Q-Learning',            'Q-Learning'),
        ('rl_snake_dql',   'rl_snake_dql.gif',   GH + 'AI_snake_DQN_version',  'Snake DQL'),
        ('rl_driving_dql', 'rl_driving_dql.gif', GH + 'AI_driving_DQN_version', 'Driving DQL'),
    ]),
    ('#### **🎯 PPO**', [
        ('rl_snake_ppo', 'rl_snake_ppo.gif', GH + 'AI_snake_PPO_version', 'Snake PPO'),
        ('rl_sc2',       'rl_starcraft2.gif', GH + 'AI-StarCraft2-VLM-RL', 'SC2 AI'),
    ]),
    ('#### **🎮 Unity ML-Agents**', [
        ('rl_unity_move',   'rl_unity_move.gif',   GH + 'Unity_move',   'Unity Move'),
        ('rl_unity_greedy', 'rl_unity_greedy.gif', GH + 'Unity_greedy', 'Unity Greedy'),
        ('rl_unity_drive',  'rl_unity_drive.gif',  GH + 'Unity_drive',  'Unity Drive'),
    ]),
    ('<h3 align="center">🦾 Robotics</h3>', [
        ('robotics_bot', 'robotics_chatbot_bot.gif', GH + 'Bot_controlled_by_a_Chatbot_RAG', 'Robotics RAG'),
    ]),
    ('<h3 align="center">🕹️ Games</h3>', [
        ('game_snake',    'game_snake.gif',         GH + 'snake_game',              'Snake Game'),
        ('game_driving',  'game_driving.gif',       GH + 'driving_game',            'Driving Game'),
        ('game_sandbox',  'game_human_sandbox.gif', GH + 'human_sandbox',           'Human Sandbox'),
        ('game_starwars', 'game_star_wars.png',     GH + 'Game_ECE_World_Minigame', 'Star Wars'),
        ('game_maze',     'game_maze_asterix.png',  GH + 'Game_maze_Asterix-Obelix', 'Asterix Maze'),
    ]),
    ('<h3 align="center">⚙️ Physics Simulation</h3>', [
        ('physics_gravity',            'physics_gravity.gif',              GH + 'gravity_simulation',                  'Gravity'),
        ('physics_attraction',         'physics_attraction_repulsion.gif', GH + 'Attraction_repulsion',                'Attraction'),
        ('physics_muscular',           'physics_muscular_simulation.png',  GH + '2D-Muscular-Simulation',              'Muscular'),
        ('physics_general_relativity', 'physics_general_relativity.gif',   GH + 'simulation_gravity-general_relativity', 'Gravity & Relativity'),
    ]),
    ('<h3 align="center">⚡ n8n Automation</h3>', [
        ('n8n_whatsapp', 'n8n_whatsapp_ai.png',  GH + 'n8n_Whatsapp_LLM',        'WhatsApp AI'),
        ('n8n_mail',     'n8n_mail_sorting.png', GH + 'n8n_smart_mail_labeling', 'Mail Sorting'),
    ]),
    ('<h3 align="center">📊 Data Analysis</h3>', [
        ('data_iss', 'data_iss_analysis.png', GH + 'ISS_Analysis_Spark', 'ISS Analysis'),
    ]),
]


# ────────────────────────────────────────────────────────────────────────────────
# Group projects (cards + member badges + link badges all in one <p>)
# ────────────────────────────────────────────────────────────────────────────────

def gh_badge(name: str, user: str) -> str:
    """GitHub-style flat-square badge linking to a user profile."""
    return (
        f'<a href="https://github.com/{user}">'
        f'<img src="https://img.shields.io/badge/{name}-181717?style=flat-square&logo=github&logoColor=white"/>'
        f'</a>'
    )


def li_badge(name: str, profile: str) -> str:
    """LinkedIn-style flat-square badge linking to a profile."""
    return (
        f'<a href="https://www.linkedin.com/in/{profile}/">'
        f'<img src="https://img.shields.io/badge/{name}-0A66C2?style=flat-square&logo=linkedin&logoColor=white"/>'
        f'</a>'
    )


def link_badge(label: str, url: str, color: str = '00b4c2', logo: str = 'github') -> str:
    return (
        f'<a href="{url}">'
        f'<img src="https://img.shields.io/badge/{label}-{color}?style=flat-square&logo={logo}&logoColor=white"/>'
        f'</a>'
    )


def group_card_html(card: str, logo: str, link: str, alt: str) -> str:
    """Group project card: square logo + big SVG card (width=400)."""
    logo_block = f'<img src="{GROUP_LOGO_DIR}/{logo}" height="{IMG_H}" alt="{alt}"/>'
    svg_block = (
        f'<picture>'
        f'<source media="(prefers-color-scheme: light)" srcset="badges/cards/{card}_light.svg"/>'
        f'<img src="badges/cards/{card}.svg" width="{GROUP_CARD_W}"/>'
        f'</picture>'
    )
    return f'<a href="{link}">{logo_block}{svg_block}</a>'


GROUP_BLOCKS = [
    # CND Hackathon
    '<p align="center">\n' +
    group_card_html('group_cnd', 'group_hackathon_cnd_sq.png',
                    'https://www.linkedin.com/feed/update/urn:li:activity:7457567844990382080/',
                    'Hackathon CND') + '<br>\n' +
    '&nbsp;'.join([
        gh_badge('Thibault_Garel',     'Thibault-GAREL'),
        gh_badge('Alfred_de_Vulpian',  'Alfred0404'),
        gh_badge('Axel_Br%C3%B6ns',    'axelbrons'),
        gh_badge('Robin_Qu%C3%A9riaux', 'Rqbln'),
        gh_badge('Ziyad_Amzil',        'ziyadamzil2'),
    ]) + '<br>\n' +
    '&nbsp;'.join([
        link_badge('Phase_1-Frontend', 'https://github.com/Thibault-GAREL/ILab-Hackaton_CND-Phase1-frontend'),
        link_badge('Phase_1-Backend',  'https://github.com/Thibault-GAREL/ILab-Hackaton_CND-Phase1-backend'),
        link_badge('Phase_2-Cyberattack_AI', 'https://github.com/Thibault-GAREL/ILab-Hackaton_CND-Phase2-Cyberattack_AI_detection'),
    ]) + '\n</p>',

    # PPE Smart Contract
    '<p align="center">\n' +
    group_card_html('group_ppe', 'group_ppe_smart_contract_sq.png',
                    'https://www.ece.fr/la-pedagogie-par-projets/',
                    'PPE Smart Contract') + '<br>\n' +
    '&nbsp;'.join([
        gh_badge('Thibault_Garel',       'Thibault-GAREL'),
        gh_badge('Axel_Br%C3%B6ns',      'axelbrons'),
        gh_badge('Valentin_Kocijancic',  'valentinkocijancic'),
        gh_badge('Hugo_Rivi%C3%A8re',    'hugoriviere'),
        gh_badge('Antoine_Goudedranche', 'Antoine31G'),
        gh_badge('Omar_El_Alami',        'omarelalamielfellousse'),
    ]) + '<br>\n' +
    '&nbsp;'.join([
        link_badge('LLM_Benchmark-Thibault',     'https://github.com/Thibault-GAREL/PPE_LLM_test_Smart_contract'),
        link_badge('LoRA_Fine--tune-Thibault',   'https://github.com/Thibault-GAREL/PPE_LoRa_Smart_contract'),
        link_badge('CodeBERT_Graphs-Axel',       'https://github.com/axelbrons/graphs-ppe'),
    ]) + '\n</p>',

    # Resilient AI
    '<p align="center">\n' +
    group_card_html('group_resilient', 'group_resilient_sq.png',
                    'https://www.sustainableaicoalition.org/resilient-ai-challenge/',
                    'Resilient AI') + '<br>\n' +
    '&nbsp;'.join([
        li_badge('Thibault_Garel',   'thibaultgarel'),
        li_badge('Axel_Br%C3%B6ns',  'axelbrons'),
        li_badge('Mathis_Lacombe',   'mathis-lacombe34'),
        li_badge('Jarfino_Houngbadji', 'jarfino-houngbadji'),
        li_badge('Achta_Sow_Demba',  'demba-sow-achta'),
        li_badge('Djebril_Laouedj',  'djebril-laouedj-9684b4219'),
    ]) + '&nbsp;&nbsp;' +
    li_badge('Bikram_Bhuyan', 'bikram-pratim-bhuyan-01887589') + '* <br>\n' +
    '&nbsp;'.join([
        link_badge('Tests',             'https://github.com/Thibault-GAREL/ILab_Hackathon-Resiliant_AI-test'),
        link_badge('Dataset_Benchmark', 'https://github.com/Thibault-GAREL/ILab_Hackathon-Resiliant_AI-Dataset_unifi-Benchmark'),
    ]) +
    '\n</p>',
]


# ────────────────────────────────────────────────────────────────────────────────
# Assemble & write
# ────────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    readme_path = Path('README.md')
    content = readme_path.read_text(encoding='utf-8')

    new_featured = '## **✨ Featured Projects**\n\n'
    new_featured += '\n'.join(section_html(projects, header) for header, projects in FEATURED_SECTIONS)
    new_featured = new_featured.rstrip('\n')

    new_group = '## **👥 Group Projects**\n\n'
    new_group += '\n\n'.join(GROUP_BLOCKS)

    featured_pattern = re.compile(r'## \*\*✨ Featured Projects\*\*\n.*?(?=\n## \*\*)', re.DOTALL)
    group_pattern    = re.compile(r'## \*\*👥 Group Projects\*\*\n.*?(?=\n## \*\*)', re.DOTALL)

    new_content = featured_pattern.sub(new_featured, content)
    new_content = group_pattern.sub(new_group, new_content)

    if new_content == content:
        print("ERREUR : aucune section remplacée, vérifier les patterns")
    else:
        readme_path.write_text(new_content, encoding='utf-8')
        print("README mis à jour avec succès !")
