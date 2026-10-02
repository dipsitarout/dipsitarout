# Setup guide — Cyberpunk RPG Profile

## File layout (repo must be named exactly your GitHub username, and be public)

```
YOUR_USERNAME/YOUR_USERNAME
├── README.md                      ← the profile page
├── config.json                    ← ALL editable values live here
├── scripts/build_assets.py        ← regenerates every SVG from config.json
├── assets/                        ← generated animated SVGs (commit these)
│   ├── banner.svg  boot.svg  divider.svg
│   ├── player-card.svg  mission.svg
│   ├── stats.svg  attributes.svg  quest.svg
│   ├── build-1..4.svg             (ClinSight, DiseaseRisk AI, KrishiDeep, ThreatShield)
│   ├── achv-1..5.svg  achv-locked.svg
│   ├── experience.svg  skill-tree.svg  side-quests.svg
│   └── player-log.svg  terminal.svg
└── .github/workflows/snake.yml    ← builds the contribution snake
```

The snake files are NOT in `assets/`. The workflow publishes them to a branch called `output`, and the README links to them there.

## First-time setup

1. Create a public repo named `YOUR_USERNAME` (same as your GitHub username). Copy every file above into it, keeping the paths exactly.
2. Find-and-replace these placeholders in `README.md` (they are the only things I could not know):
   - `YOUR_USERNAME` (appears in badges, snake URLs, GitHub link)
   - `YOUR_FLAGSHIP_REPO` (repo whose star count the STARS badge shows, e.g. your ClinSight repo)
   - `YOUR_LINKEDIN_ID`, `YOUR_EMAIL@example.com`, `YOUR_PORTFOLIO_URL` (delete the Portfolio line if you have none)
3. Repo → **Settings → Actions → General → Workflow permissions** → select **Read and write permissions** → Save.
4. Commit and push to `main`.
5. Repo → **Actions** tab → **Generate Contribution Snake** → **Run workflow**. After it finishes (about a minute) an `output` branch exists with `github-snake-dark.svg` and `github-snake.svg`. The snake is empty until then. It refreshes every 12 hours.
6. Open `github.com/YOUR_USERNAME`. If images look stale, hard refresh (GitHub caches images briefly).

## Changing values later

1. Edit `config.json`.
2. Run `python scripts/build_assets.py` (Python 3, no packages needed).
3. Commit the changed files in `assets/`.

## CUSTOMIZATION VARIABLES (all in `config.json`)

| What | Key | Example |
|---|---|---|
| Level percentage | `"level"` | `85` → `86` (updates banner HUD, player card number and the animated bar) |
| Character stats | `"stats"` | each item: `name`, `value` (0–100), `color` (`cyan` `purple` `blue` `green`) |
| Player attributes | `"attributes"` | same shape as stats |
| Quest progress | `"quest"."progress"` | `78` |
| Quest text, tags, reward | `"quest"."tags"`, `"reward_xp"`, `"reward_text"` | |
| Mission status bar | `"mission"."status_pct"`, `"status_label"` | `82`, `"ACTIVE"` |
| XP | `"mission"."xp"` and `"xp_max"` | `4200` of `5000` (bar = xp ÷ xp_max) |
| Current mission list | `"mission"."items"` | up to 5 lines fit |
| Project status / stack / XP | `"projects"` | `status`, `desc`, `tags`, `difficulty` (0–100), `xp` |
| Achievement list | `"achievements"` | `code` (2–3 letters in the hexagon), `title`, `event`, `xp` (visual only) |
| Experience timeline | `"timeline"` | years and items; optional `"sub"` line |
| Skill tree | `"tree"."branches"` | each branch: `name`, `color`, `skills` |
| Side quests | `"side_quests"` | `[name, tagline]` pairs (7 fit the grid) |
| Player log | `"log"` | `[date, tag, message, color]` |
| Terminal rows | `"terminal"."rows"` | `[label, value, color]` |
| Name, class, base, status | `"profile"` | |

Anything on the **README side** (snake colours, badges) lives in `README.md` and `.github/workflows/snake.yml`.

## Things to verify (I did not invent them, but I had to fill gaps)

- **Project descriptions and tech tags**: only ClinSight's stack (RAG, FAISS, FastAPI, Gemini) came from you. The other three descriptions are inferred from the project names and show a generic `AI / ML` tag. Edit `"projects"` with the real stack and wording.
- **Project status / difficulty / XP, attribute values, level, quest %, mission %**: game-style visuals, labelled as such. Only the 7 character-stat values and the ClinSight difficulty/XP came from your examples.
- **Log dates**: only 2024 (TechnoVIT), 2025 (Tata Power) and 2026 (Amazon ML Summer School) are dated. Undated events show `----`. Replace with real dates in `"log"`.
