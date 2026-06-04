# CLAUDE.md — README projet Thibault GAREL

Ce fichier documente l'architecture du README et la procédure pour ajouter un nouveau projet sans rien oublier.

## Architecture des fichiers

| Fichier | Rôle |
|---------|------|
| `README.md` | Le rendu final (peut être régénéré par `update_readme_cards.py`) |
| `categories.py` | **Source unique** des catégories : emoji label + couleur accent. Importé par les autres scripts. |
| `generate_cards.py` | Génère les SVG de carte (titre + description) pour le mode **dark** |
| `add_shadows.py` | Applique l'ombre portée aux SVG (étend 200×140 → 210×151). **Idempotent** : skip si déjà appliqué. |
| `generate_light_cards.py` | Génère les variantes `_light.svg` à partir des SVG dark + wrap le README en `<picture>`. **Bug regex corrigé** (stateful parser). |
| `round_logos.py` | Applique aux images de logo : resize 140px, coins arrondis, ombre colorée. **Idempotent** : skip si déjà processé (height = DISPLAY_H + PAD_Y). |
| `compress_images.py` | Compresse les images de `Logo_*` vers `Logo_*_compressed/` (préserve la transparence GIF). |
| `update_readme_cards.py` | Régénère les sections Featured + Group du README depuis les listes de projets. **Synchronisé** avec le format actuel (`<h3 align="center">`, `Logo_Featured_Projects_compressed/`, `<picture>` wrap pour GIF + SVG). |

## ✅ Pipeline complet (régénérer tout)

```
1. round_logos.py        → traite Logo_Featured_Projects/* (idempotent)
2. compress_images.py    → produit Logo_Featured_Projects_compressed/*
3. generate_cards.py     → produit badges/cards/*.svg (dark)
4. add_shadows.py        → applique ombre aux SVG (idempotent)
5. generate_light_cards  → produit badges/cards/*_light.svg + wrap README
6. update_readme_cards   → régénère les sections Featured + Group du README
```

## Procédure pour ajouter un nouveau projet

### 1. Recueillir les infos auprès de l'utilisateur

Toujours poser ces questions avant de commencer :

- **URL du repo GitHub** (ex : `https://github.com/Thibault-GAREL/Mon_Projet`)
- **Catégorie** (voir tableau ci-dessous)
- **Titre court** de la carte (max ~21 caractères par ligne, idéalement 1 ligne)
- **Description courte** (max ~29 caractères par ligne, idéalement 3 lignes)
- **Position dans le README** (entre quel projet existant et lequel ?)
- **Logo** : nom du fichier que l'utilisateur va déposer dans `Logo_Featured_Projects/` (format PNG ou GIF)
- **Date du projet** (ex : `2026-04-15`, ou `avril 2026` si le mois précis suffit) — utilisée pour le récap portfolio (le portfolio Vercel trie les projets par catégorie + date)

### 2. Catégories disponibles (avec couleur d'accent)

| Clé | Label SVG | Accent | Préfixe logo |
|-----|-----------|--------|--------------|
| `gen_ai` | 🤖 GENERATIVE AI | `#6e40c9` | `gen_ai_` |
| `neural` | 🧠 NEURAL NETWORKS | `#2563eb` | `neural_` |
| `rl_dt` | 🌳 DECISION TREE | `#22c55e` | `rl_snake_decision_` |
| `rl_ga` | 🧬 GENETIC ALGORITHM | `#16a34a` | `rl_*_genetic`, `rl_walking_` |
| `rl_ql` | 📈 Q-LEARNING | `#10b981` | `rl_q_learning`, `rl_*_dql` |
| `rl_ppo` | 🎯 PPO | `#059669` | `rl_snake_ppo`, `rl_starcraft`, `rl_sc2` |
| `rl_unity` | 🎮 UNITY ML-AGENTS | `#0f766e` | `rl_unity_` |
| `speech` | 🎙 SPEECH RECOGNITION | `#ea580c` | `speech_` |
| `robotics` | 🦾 ROBOTICS | `#dc2626` | `robotics_` |
| `games` | 🕹 GAMES | `#0891b2` | `game_` |
| `physics` | ⚙ PHYSICS SIMULATION | `#0d9488` | `physics_` |
| `n8n` | ⚡ APPLIED AI WORKFLOWS | `#db2777` | `n8n_` |
| `data` | 📊 DATA ANALYSIS | `#d97706` | `data_` |
| `group` | 👥 GROUP PROJECT | `#00b4c2` | `group_` |

### 3. Traiter l'image du logo

Cible : **221×152 RGBA** (image content 210×140 + padding shadow 11×12), même format que tous les autres logos.

Pipeline (à faire dans `pytorch_cuda_env` ou `basic_env` selon dispo) :

1. Si l'image n'est pas en ratio 1.5 (3:2), **cropper** d'abord (demander à l'utilisateur quelle partie garder : haut, centre, etc.)
2. Appliquer le pipeline de `round_logos.py` sur l'image (resize 140px → mask coins arrondis radius 14 → shadow couleur accent avec 3 couches d'opacité)
3. Sauver dans **les deux dossiers** :
   - `Logo_Featured_Projects/<nom>.png`
   - `Logo_Featured_Projects_compressed/<nom>.png`

Pour les **GIF** : `round_logos.py` génère 2 variantes (`<nom>.gif` avec fond blanc baked-in, `<nom>_dark.gif` avec fond sombre baked-in), à compresser avec `compress_images.py` corrigé (qui préserve la transparence des coins).

### 4. Générer les SVG de carte

Façon recommandée — édition manuelle pour éviter de toucher aux autres cartes :

1. Ajouter l'entrée dans le tableau `projects` de `generate_cards.py` (pour traçabilité future)
2. **Ne pas** relancer `generate_cards.py` en entier (il écraserait toutes les autres cartes avec un style légèrement différent)
3. Lancer `generate_cards.py` une seule fois sur un dossier temporaire, OU générer le SVG en inline Python en réutilisant la fonction `svg()` du script
4. Appliquer **manuellement** les corrections de style (sinon incohérence visuelle) :
   - `font-size="9" fill="{accent}"` → `font-size="9" fill="#ffffff"` sur le label
   - `font-size="10" fill="#8b949e"` → `font-size="12" fill="#8b949e"` sur les lignes de description (dark)
   - `font-size="10" fill="#57606a"` → `font-size="12" fill="#57606a"` sur les lignes de description (light)
5. Appliquer le shadow (`add_shadows.py` logic) sur le SVG dark uniquement :
   - dimensions 200×140 → 210×151
   - 3 rects d'ombre avant le bg, opacities (0.30, 0.22, 0.14) pour dark / (0.18, 0.13, 0.08) pour light, offsets (8,9), (5,6), (3,4)
6. Générer la variante `_light.svg` :
   - bg `#0d1117` → tint pastel = `light_tint(accent, white_ratio=0.92)`
   - title `#f0f6fc` → `#24292f`
   - desc `#8b949e` → `#57606a`
   - opacities shadow réduites (0.18, 0.13, 0.08)

Résultat : `badges/cards/<nom>.svg` (dark) + `badges/cards/<nom>_light.svg` (light)

### 5. Mettre à jour le README

Édition **manuelle** (les scripts auto sont désynchronisés). Structure d'une carte (PNG statique) :

```html
<a href="GITHUB_URL"><img src="Logo_Featured_Projects_compressed/NOM.png" height="140" alt="ALT"/><picture><source media="(prefers-color-scheme: light)" srcset="badges/cards/NOM_light.svg"/><img src="badges/cards/NOM.svg" width="200"/></picture></a>
```

Pour un GIF (le logo a sa propre variante `_dark.gif`) :

```html
<a href="GITHUB_URL"><picture><source media="(prefers-color-scheme: dark)" srcset="Logo_Featured_Projects_compressed/NOM_dark.gif"/><img src="Logo_Featured_Projects_compressed/NOM.gif" height="140" alt="ALT"/></picture><picture><source media="(prefers-color-scheme: light)" srcset="badges/cards/NOM_light.svg"/><img src="badges/cards/NOM.svg" width="200"/></picture></a>
```

- Cartes par paires séparées par `&emsp;`
- Lignes séparées par `<br><br>`
- À insérer dans le `<p>` de la catégorie (chaque catégorie a son propre `<p>`)

> ⚠️ **Limite connue** : sur viewport étroit, le logo et le SVG d'un même projet peuvent wrapper sur des lignes séparées (les `<img>`/`<picture>` sont des éléments inline). Tentative d'utiliser `<table align="left">` flotté pour les garder collés → **ÉCHEC** : GitHub applique `display: block` + bordures à tous les `<table>` du markdown, donc chaque carte se retrouvait isolée sur sa propre ligne avec des bordures visibles. **Garder le format inline `<a>...</a>` actuel.** Pour vraiment garantir image+SVG côte-à-côte, il faudrait combiner les deux en une seule image par projet (PNG/SVG composé), au prix de perdre l'animation GIF ou le switch dark/light.

### 6. Synchroniser les scripts (pour le futur)

Même si on n'utilise pas `update_readme_cards.py` aujourd'hui, l'ajouter à `CATEGORIES` dans le script pour cohérence future. Pareil pour `generate_cards.py`.

### 7. Vérification

- `git diff --stat` pour valider la liste des fichiers touchés (typiquement : 2 SVG, 2 images, 2-3 scripts, README)
- Push et vérifier visuellement sur GitHub que :
  - La carte s'affiche dans la bonne section
  - Le logo a bien transparence + coins arrondis + ombre
  - Light mode et dark mode rendent correctement
  - Tous les liens fonctionnent

### 8. Récap pour le Claude Code du portfolio Vercel

**Quand** : seulement APRÈS validation visuelle (étape 7). L'utilisateur doit confirmer "ok ça rend bien sur GitHub" avant de générer ce récap, sinon les infos pourraient changer.

**Format** : un seul bloc markdown copy-pasteable, fenced avec ` ```markdown `, pour que l'utilisateur puisse le coller directement à son Claude portfolio. Le bloc doit être **auto-suffisant** : le Claude portfolio doit pouvoir agir sans questions de suivi.

**Template** (à copier-coller dans la réponse, en remplaçant les placeholders) :

````markdown
## Nouveau projet à ajouter au portfolio Vercel

- **Titre** : <titre tel qu'il apparaît dans la carte SVG>
- **Repo GitHub** : <URL complète>
- **Date** : <YYYY-MM-DD ou Mois YYYY>
- **Catégorie** : <ex : Generative AI, Neural Networks, Reinforcement Learning, …>
- **Description courte** (3 lignes max — celle de la SVG card) :
  > <ligne 1>
  > <ligne 2>
  > <ligne 3>
- **Description longue** (paragraphe pour la page projet) :
  > <2-4 phrases qui détaillent ce que fait le projet, comment, et le résultat clé>
- **Visuel** : <URL absolue du logo/GIF, idéalement la raw GitHub de ce repo
  ex: `https://raw.githubusercontent.com/Thibault-GAREL/Thibault-GAREL/main/Logo_Featured_Projects_compressed/<nom>`>
- **Position dans le README du portfolio Thibault-GAREL** : ajouté entre **<projet précédent>** et **<projet suivant>** dans la section **<catégorie>**
- **Position suggérée dans le portfolio Vercel** : à classer dans la section **<catégorie>**, ordonné par date (le portfolio Vercel trie par catégorie + date desc)
- **Lien README portfolio** : commit `<hash court>` de [Thibault-GAREL/Thibault-GAREL](https://github.com/Thibault-GAREL/Thibault-GAREL)
````

**Règles de rédaction** :

- Si la description longue n'a pas été demandée explicitement à l'utilisateur, déduis-en une à partir du README du repo cible (3-4 phrases max) ou demande à l'utilisateur. Ne pas inventer.
- L'URL du visuel doit être absolue (raw.githubusercontent.com) pour que le Claude portfolio puisse y accéder sans cloner le repo README.
- Mentionner explicitement la section/position dans le récap, même si elle figure aussi dans le README — c'est le seul signal que le Claude portfolio aura pour placer le projet au bon endroit.
- Si le projet a un GIF animé, préciser dans **Visuel** "GIF animé, variante light/dark disponibles" pour que le portfolio choisisse la variante appropriée.

## Checklist condensée

```
[ ] Titre court (≤21 char / ligne)
[ ] Description courte (≤29 char / ligne, ~3 lignes)
[ ] URL GitHub
[ ] Catégorie
[ ] Position dans le README (entre quels projets)
[ ] Date du projet (YYYY-MM-DD ou Mois YYYY) — pour le récap portfolio
[ ] Logo déposé dans Logo_Featured_Projects/
[ ] Logo traité (crop si besoin → 221×152 RGBA avec shadow)
[ ] Logo compressé dans Logo_Featured_Projects_compressed/
[ ] SVG dark généré + style harmonisé (#ffffff label, font-size=12 desc)
[ ] Shadow appliqué (210×151)
[ ] SVG light généré (tint pastel + couleurs adaptées)
[ ] README modifié (entrée HTML insérée au bon endroit)
[ ] generate_cards.py mis à jour
[ ] update_readme_cards.py mis à jour
[ ] git diff vérifié
[ ] ⏳ Validation visuelle utilisateur sur GitHub
[ ] 🎯 Récap portfolio Vercel généré (step 8) — APRÈS validation uniquement
```
