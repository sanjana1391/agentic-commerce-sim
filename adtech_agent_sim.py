"""Agentic commerce ranking simulator.

Companion code for the article "From Clicks to Decisions".

The simulator models one shopping request ("waterproof backpack, under $60,
delivered by Sunday") and compares two ranking strategies:

  * organic:   score = 0.5*relevance + 0.3*reviews + 0.2*price_score
  * sponsored: score = organic * min(bid_multiplier, BID_CAP)

All data is synthetic. Scores are normalized to 0-1 and the weights are
illustrative, not taken from any real platform.

Standard library only. Run:

    python adtech_agent_sim.py
    python adtech_agent_sim.py --seed 7 --strategy sponsored
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import Iterable

ORGANIC_WEIGHTS = {"relevance": 0.5, "reviews": 0.3, "price": 0.2}
BID_CAP = 1.20
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
STRATEGIES = ("organic", "sponsored")


@dataclass(frozen=True)
class Product:
    sku: str
    merchant: str
    name: str
    price_usd: float
    waterproof: bool
    delivery_day: str
    relevance: float        # 0-1, how well the product matches the request
    reviews: float          # 0-1, normalized review quality
    price_score: float      # 0-1, higher means better value
    bid_multiplier: float = 1.0


@dataclass(frozen=True)
class Request:
    waterproof: bool = True
    max_price_usd: float = 60.0
    deliver_by: str = "Sunday"


@dataclass
class Result:
    product: Product
    organic: float
    final: float
    explanation: str


def organic_score(p: Product) -> float:
    return round(
        ORGANIC_WEIGHTS["relevance"] * p.relevance
        + ORGANIC_WEIGHTS["reviews"] * p.reviews
        + ORGANIC_WEIGHTS["price"] * p.price_score,
        3,
    )


def applied_multiplier(p: Product) -> float:
    return min(p.bid_multiplier, BID_CAP)


def final_score(p: Product, strategy: str) -> float:
    base = organic_score(p)
    if strategy == "sponsored":
        return round(base * applied_multiplier(p), 3)
    return base


def check_eligibility(p: Product, req: Request) -> str | None:
    """Return the reason a product is excluded, or None if it is eligible."""
    if req.waterproof and not p.waterproof:
        return "not waterproof"
    if p.price_usd > req.max_price_usd:
        return "over budget"
    if DAYS.index(p.delivery_day) > DAYS.index(req.deliver_by):
        return "arrives too late"
    return None


def explain(p: Product, strategy: str) -> str:
    if strategy == "sponsored" and p.bid_multiplier > 1.0:
        return (
            f"Ranked with a sponsored placement "
            f"(x{applied_multiplier(p):.2f}, capped at x{BID_CAP:.2f})."
        )
    return "Best match on relevance, reviews and price."


def run(products: Iterable[Product], req: Request, strategy: str) -> dict:
    """Filter, score and rank products for one request under one strategy."""
    if strategy not in STRATEGIES:
        raise ValueError(f"strategy must be one of {STRATEGIES}")

    products = list(products)
    excluded: dict[str, list[str]] = {}
    eligible: list[Product] = []
    for p in products:
        reason = check_eligibility(p, req)
        if reason is None:
            eligible.append(p)
        else:
            excluded.setdefault(reason, []).append(p.sku)

    ranked = sorted(
        (
            Result(
                product=p,
                organic=organic_score(p),
                final=final_score(p, strategy),
                explanation=explain(p, strategy),
            )
            for p in eligible
        ),
        key=lambda r: r.final,
        reverse=True,
    )

    return {
        "strategy": strategy,
        "retrieved": len(products),
        "eligible": len(eligible),
        "excluded": {k: len(v) for k, v in excluded.items()},
        "ranked": ranked,
        "top": ranked[0] if ranked else None,
    }


def demo_catalog(seed: int = 42) -> list[Product]:
    """Three named products from the article plus 47 generated ones.

    The generated products are capped below the named products' scores so the
    named three remain the contest, which keeps the article's example stable.
    Pass a different seed to explore other catalogs.
    """
    named = [
        Product("TB-2291", "Merchant A", "TrailPro", 54, True, "Saturday",
                relevance=0.90, reviews=0.85, price_score=0.80),
        Product("SB-1104", "Merchant B", "StormSack", 48, True, "Friday",
                relevance=0.80, reviews=0.85, price_score=0.80),
        Product("RL-0730", "Merchant C", "RidgeLite", 42, True, "Saturday",
                relevance=0.78, reviews=0.80, price_score=0.85,
                bid_multiplier=1.15),
    ]

    rng = random.Random(seed)
    merchants = ["Merchant A", "Merchant B", "Merchant C"]
    generated = []
    for i in range(47):
        generated.append(
            Product(
                sku=f"GEN-{i:03d}",
                merchant=rng.choice(merchants),
                name=f"Backpack {i:02d}",
                price_usd=round(rng.uniform(25, 120), 2),
                waterproof=rng.random() < 0.3,
                delivery_day=rng.choice(DAYS),
                relevance=round(rng.uniform(0.3, 0.7), 2),
                reviews=round(rng.uniform(0.3, 0.8), 2),
                price_score=round(rng.uniform(0.2, 1.0), 2),
            )
        )
    return named + generated


def print_run(outcome: dict) -> None:
    print(f"\n=== {outcome['strategy'].upper()} RANKING ===")
    print(f"Retrieved: {outcome['retrieved']}   Eligible: {outcome['eligible']}")
    for reason, count in outcome["excluded"].items():
        print(f"  excluded ({reason}): {count}")
    print()
    print(f"{'Rank':<5}{'Product':<12}{'Merchant':<12}{'Organic':>9}{'Final':>8}")
    for i, r in enumerate(outcome["ranked"][:5], start=1):
        print(
            f"{i:<5}{r.product.name:<12}{r.product.merchant:<12}"
            f"{r.organic:>9.3f}{r.final:>8.3f}"
        )
    if outcome["top"]:
        print(f"\nRecommendation: {outcome['top'].product.name}")
        print(f"Explanation:    {outcome['top'].explanation}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[2])
    parser.add_argument("--seed", type=int, default=42, help="catalog seed")
    parser.add_argument(
        "--strategy",
        choices=("both",) + STRATEGIES,
        default="both",
        help="which ranking strategy to run",
    )
    args = parser.parse_args()

    catalog = demo_catalog(args.seed)
    req = Request()
    strategies = STRATEGIES if args.strategy == "both" else (args.strategy,)
    for strategy in strategies:
        print_run(run(catalog, req, strategy))


if __name__ == "__main__":
    main()
