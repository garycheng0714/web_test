#!/usr/bin/env python3
"""Simulate judge validation: splits, TPR/TNR, Rogan-Gladen, bootstrap CI.

    python3 learn/evals/toy/validate.py

The judge is simulated with known TPR/TNR so the lesson can focus on the math.
Change TPR/TNR below and rerun to see how the corrected rate and CI move.
"""

import random
from dataclasses import dataclass

SEED = 42
N_PASS = 50
N_FAIL = 50
TPR = 0.95
TNR = 0.80
PROD_N = 500
TRUE_PROD_RATE = 0.80
BOOTSTRAP = 2000

TRAIN_FRAC = 0.15
DEV_FRAC = 0.45


@dataclass
class Example:
    label: str  # "Pass" or "Fail"
    pred: str  # "Pass" or "Fail"


def make_labeled(n_pass=N_PASS, n_fail=N_FAIL, tpr=TPR, tnr=TNR, seed=SEED):
    rng = random.Random(seed)
    data = []
    for label in ["Pass"] * n_pass + ["Fail"] * n_fail:
        correct = rng.random() < (tpr if label == "Pass" else tnr)
        pred = label if correct else ("Fail" if label == "Pass" else "Pass")
        data.append(Example(label, pred))
    rng.shuffle(data)
    return data


def split(data, seed=SEED + 1):
    rng = random.Random(seed)
    by_label = {"Pass": [], "Fail": []}
    for example in data:
        by_label[example.label].append(example)

    train, dev, test = [], [], []
    for examples in by_label.values():
        rng.shuffle(examples)
        n_train = round(len(examples) * TRAIN_FRAC)
        n_dev = round(len(examples) * DEV_FRAC)
        train += examples[:n_train]
        dev += examples[n_train : n_train + n_dev]
        test += examples[n_train + n_dev :]
    return train, dev, test


def confusion(data):
    tp = sum(1 for e in data if e.label == "Pass" and e.pred == "Pass")
    fn = sum(1 for e in data if e.label == "Pass" and e.pred == "Fail")
    tn = sum(1 for e in data if e.label == "Fail" and e.pred == "Fail")
    fp = sum(1 for e in data if e.label == "Fail" and e.pred == "Pass")
    return tp, fn, tn, fp


def rates(data):
    tp, fn, tn, fp = confusion(data)
    tpr = tp / (tp + fn) if tp + fn else 0.0
    tnr = tn / (tn + fp) if tn + fp else 0.0
    return tpr, tnr


def corrected(p_obs, tpr, tnr):
    denom = tpr + tnr - 1
    if abs(denom) < 1e-9:
        return None
    return max(0.0, min(1.0, (p_obs + tnr - 1) / denom))


def bootstrap_ci(test_data, p_obs, n=BOOTSTRAP, seed=SEED + 2):
    rng = random.Random(seed)
    estimates = []
    for _ in range(n):
        sample = [rng.choice(test_data) for _ in test_data]
        tpr, tnr = rates(sample)
        denom = tpr + tnr - 1
        if abs(denom) < 1e-9:
            continue
        theta = (p_obs + tnr - 1) / denom
        estimates.append(max(0.0, min(1.0, theta)))
    estimates.sort()
    lo = estimates[int(0.025 * len(estimates))]
    hi = estimates[int(0.975 * len(estimates)) - 1]
    return lo, hi


def production(tpr=TPR, tnr=TNR, n=PROD_N, true_rate=TRUE_PROD_RATE, seed=SEED + 3):
    rng = random.Random(seed)
    labels = ["Pass" if rng.random() < true_rate else "Fail" for _ in range(n)]
    preds = []
    for label in labels:
        correct = rng.random() < (tpr if label == "Pass" else tnr)
        preds.append(label if correct else ("Fail" if label == "Pass" else "Pass"))
    p_obs = preds.count("Pass") / n
    return p_obs, labels, preds


def show(name, data):
    tpr, tnr = rates(data)
    tp, fn, tn, fp = confusion(data)
    print(
        f"{name}: n={len(data)} TP={tp} FN={fn} TN={tn} FP={fp} "
        f"TPR={tpr:.2f} TNR={tnr:.2f}"
    )
    return tpr, tnr


def main():
    print(f"simulated judge: TPR={TPR:.2f} TNR={TNR:.2f}")
    train, dev, test = split(make_labeled())
    print(f"splits: train={len(train)} dev={len(dev)} test={len(test)}")

    show("dev", dev)
    tpr, tnr = show("test", test)

    p_obs, labels, preds = production()
    theta = corrected(p_obs, tpr, tnr)
    lo, hi = bootstrap_ci(test, p_obs)
    true_rate = sum(1 for label in labels if label == "Pass") / len(labels)

    print(f"\nproduction: n={len(labels)} raw pass={p_obs:.2f}")
    print(f"corrected={theta:.2f}  95% CI=[{lo:.2f}, {hi:.2f}]")
    print(f"true rate (simulation only)={true_rate:.2f}")


if __name__ == "__main__":
    main()
