import unittest

from adtech_agent_sim import (
    BID_CAP,
    Product,
    Request,
    check_eligibility,
    demo_catalog,
    final_score,
    organic_score,
    run,
)


def make(**overrides) -> Product:
    base = dict(
        sku="X", merchant="M", name="X", price_usd=50, waterproof=True,
        delivery_day="Friday", relevance=0.5, reviews=0.5, price_score=0.5,
    )
    base.update(overrides)
    return Product(**base)


class ArticleNumbers(unittest.TestCase):
    """The scores quoted in the article must come out of the code."""

    def setUp(self):
        self.catalog = {p.name: p for p in demo_catalog()}

    def test_organic_scores_match_article(self):
        self.assertAlmostEqual(organic_score(self.catalog["TrailPro"]), 0.865)
        self.assertAlmostEqual(organic_score(self.catalog["StormSack"]), 0.815)
        self.assertAlmostEqual(organic_score(self.catalog["RidgeLite"]), 0.800)

    def test_sponsored_score_matches_article(self):
        self.assertAlmostEqual(
            final_score(self.catalog["RidgeLite"], "sponsored"), 0.920
        )

    def test_organic_winner_is_trailpro(self):
        result = run(demo_catalog(), Request(), "organic")
        self.assertEqual(result["top"].product.name, "TrailPro")

    def test_sponsored_flips_winner_to_ridgelite(self):
        result = run(demo_catalog(), Request(), "sponsored")
        self.assertEqual(result["top"].product.name, "RidgeLite")
        self.assertIn("sponsored", result["top"].explanation.lower())


class Mechanics(unittest.TestCase):

    def test_bid_multiplier_is_capped(self):
        p = make(bid_multiplier=2.0)
        self.assertAlmostEqual(
            final_score(p, "sponsored"), round(organic_score(p) * BID_CAP, 3)
        )

    def test_organic_strategy_ignores_bids(self):
        p = make(bid_multiplier=1.5)
        self.assertEqual(final_score(p, "organic"), organic_score(p))

    def test_eligibility_reasons(self):
        req = Request()
        self.assertEqual(check_eligibility(make(waterproof=False), req), "not waterproof")
        self.assertEqual(check_eligibility(make(price_usd=61), req), "over budget")
        self.assertEqual(
            check_eligibility(make(delivery_day="Saturday"), Request(deliver_by="Friday")),
            "arrives too late",
        )
        self.assertIsNone(check_eligibility(make(), req))

    def test_unknown_strategy_raises(self):
        with self.assertRaises(ValueError):
            run([], Request(), "random")


if __name__ == "__main__":
    unittest.main()
