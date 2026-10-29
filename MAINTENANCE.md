# Maintaining this profile

The SVGs in `assets/` are static snapshots generated from live GitHub data. Regenerate them when numbers change:

```bash
gh auth status            # needs a token with repo scope
python3 tools/gen_cards.py
git add assets/ && git commit -m "refresh cards" && git push
```

`tools/gen_cards.py` fetches repo metadata via `gh api`, renders the featured cards and the stats card, and writes them to `assets/`. No external stats service is used: github-readme-stats' public instance was down (deployment paused), so the cards are generated locally instead.
