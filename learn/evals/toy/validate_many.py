#!/usr/bin/env python3
"""Run validate.py across many seeds to show sampling variability.

    python3 learn/evals/toy/validate_many.py

Each seed is a different draw of labeled examples + production traces.
This simulates resampling; it is not a substitute for bootstrap on real labels.
20 trials is small, so the coverage number is noisy.
"""

import statistics

import validate

TRIALS = 20
TPR = validate.TPR
TNR = validate.TNR
CONFIGS = [
    ("200 labels (100 Pass / 100 Fail)", 100, 100),
    ("100 labels (50 Pass / 50 Fail)", 50, 50),
]


def one_trial(seed, n_pass, n_fail):
    data = validate.make_labeled(
        n_pass=n_pass, n_fail=n_fail, tpr=TPR, tnr=TNR, seed=seed
    )
    _, _, test = validate.split(data, seed=seed + 1)
    tpr, tnr = validate.rates(test)

    p_obs, labels, _ = validate.production(tpr=TPR, tnr=TNR, seed=seed + 3)
    theta = validate.corrected(p_obs, tpr, tnr)
    try:
        lo, hi = validate.bootstrap_ci(test, p_obs, seed=seed + 2)
    except IndexError:
        return None

    true_rate = sum(1 for label in labels if label == "Pass") / len(labels)
    return {
        "tpr": tpr,
        "tnr": tnr,
        "theta": theta,
        "true": true_rate,
        "width": hi - lo,
        "covered": lo <= true_rate <= hi,
    }


def summarize(name, n_pass, n_fail):
    rows = [one_trial(1000 + i, n_pass, n_fail) for i in range(TRIALS)]
    rows = [row for row in rows if row]
    if not rows:
        print(f"{name}: no valid trials (check TPR/TNR)")
        return

    def stat(key):
        values = [row[key] for row in rows]
        spread = statistics.stdev(values) if len(values) > 1 else 0.0
        return statistics.mean(values), spread

    widths = [row["width"] for row in rows]
    coverage = sum(row["covered"] for row in rows) / len(rows)

    print(f"\n{name} · {len(rows)} trials · TPR={TPR:.2f} TNR={TNR:.2f}")
    for key, label in [
        ("tpr", "TPR"),
        ("tnr", "TNR"),
        ("theta", "corrected"),
        ("width", "CI width"),
    ]:
        mean, spread = stat(key)
        print(f"  {label:9} {mean:.3f} ± {spread:.3f}")
    print(
        f"  width     min={min(widths):.3f} "
        f"median={statistics.median(widths):.3f} max={max(widths):.3f}"
    )
    print(f"  coverage  {coverage:.2f}  (CI contains the realized true rate)")


def main():
    print(f"TPR={TPR:.2f} TNR={TNR:.2f} · {TRIALS} trials per config")
    for name, n_pass, n_fail in CONFIGS:
        summarize(name, n_pass, n_fail)


if __name__ == "__main__":
    main()
