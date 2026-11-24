from __future__ import annotations

import random

import pandas as pd

from src.config import get_settings

NOISE_TOKENS = ("zxqv", "qwxz", "foobaz123", "###drift###", "loremtypo")


def simulate_production(reference: pd.DataFrame, random_state: int = 42) -> pd.DataFrame:
    rng = random.Random(random_state)
    drifted = reference.copy()
    n = len(drifted)
    billing_n = int(n * 0.8)
    labels = ["billing"] * billing_n + ["technical"] * (n - billing_n)
    rng.shuffle(labels)
    texts: list[str] = []
    for text in drifted["text"].astype(str):
        inflated = (text + " ") * 4
        noisy = inflated + " " + " ".join(rng.choice(NOISE_TOKENS) for _ in range(8))
        texts.append(noisy)
    drifted["text"] = texts
    drifted["label"] = labels
    return drifted


def write_production_csv() -> pd.DataFrame:
    settings = get_settings()
    reference = pd.read_csv(settings.tickets_csv)
    production = simulate_production(reference)
    settings.production_csv.parent.mkdir(parents=True, exist_ok=True)
    production.to_csv(settings.production_csv, index=False)
    return production
