# Agentic Commerce Ranking Simulator

A small, dependency-free simulator that shows how a sponsored signal can change which product an AI shopping assistant recommends.

It is companion code for the article *From Clicks to Decisions*. All data is synthetic, and the weights are illustrative. This is a teaching model, not a description of any real platform.

## What it models

One request: *waterproof backpack, under $60, delivered by Sunday.*

The simulator runs the same catalog through two strategies:

1. **Eligibility filter.** Hard constraints remove products that are not waterproof, are over budget, or arrive too late.
2. **Organic ranking.** Each eligible product is scored:

   ```
   organic = 0.5 × relevance + 0.3 × reviews + 0.2 × price_score
   ```

3. **Sponsored ranking.** The organic score is multiplied by the merchant's bid multiplier, capped at 1.20:

   ```
   final = organic × min(bid_multiplier, 1.20)
   ```

The cap limits how far commercial weight can override relevance. It does not stop a sponsored product from winning.

## Run it

Requires Python 3.9 or later. No packages to install.

```bash
python3 adtech_agent_sim.py                     # both strategies, default seed
python3 adtech_agent_sim.py --strategy sponsored
python3 adtech_agent_sim.py --seed 7           # a different synthetic catalog
```

Expected output with the default seed for the three named products:

| Strategy | Recommendation | Score | Why |
|---|---|---|---|
| Organic | TrailPro (Merchant A) | 0.865 | Best match on relevance, reviews and price |
| Sponsored | RidgeLite (Merchant C) | 0.920 | Ranked with a sponsored placement (×1.15) |

## Test it

```bash
python3 -m unittest -v test_adtech_agent_sim
```

The tests check the article's numbers directly, along with the bid cap, eligibility reasons and input validation.

## Files

- `adtech_agent_sim.py` — the simulator: data model, eligibility, scoring, ranking and a command-line runner
- `test_adtech_agent_sim.py` — unit tests, including the article's numbers
- `web/template.html` — the interactive page's source
- `build_web.py` — builds `docs/index.html` from the Python catalog, so the web and command-line versions match
- `docs/index.html` — the built page, served by GitHub Pages
- `README.md` — this file

## Limitations

- Scores are normalized inputs, supplied directly. A real system would derive them from data.
- The catalog is generated, not drawn from real merchant feeds.
- There is no model of user preferences, learning or feedback loops.
- The sponsored strategy is one design. Other auction and placement mechanisms exist.

## Extending it

Good places to start:

- Replace `demo_catalog()` with products loaded from a CSV or JSON feed.
- Add a third strategy, such as a second-price auction or a per-merchant budget cap.
- Log every excluded and ranked product so the output can be audited, which is the transparency point the article makes.


