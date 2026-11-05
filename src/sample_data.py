from __future__ import annotations

import numpy as np
import pandas as pd


def make_sample_data(seed: int = 2026, learner_count: int = 420) -> pd.DataFrame:
    """Create reproducible fictional learner-module activity and outcomes."""
    rng = np.random.default_rng(seed)
    modules = [
        "Getting Started",
        "Core Concepts",
        "Data Skills",
        "Applied Practice",
        "Knowledge Check",
        "Capstone",
    ]
    groups = ["Self-paced", "Instructor-led", "Returning learners"]
    module_difficulty = np.array([0.0, 0.15, 0.25, 0.35, 0.45, 0.55])
    learner_aptitude = rng.normal(0, 1, learner_count)
    learner_engagement = rng.normal(0, 1, learner_count)
    learner_groups = rng.choice(groups, size=learner_count, p=[0.52, 0.31, 0.17])

    records: list[dict[str, object]] = []
    for learner_index in range(learner_count):
        for module_index, module in enumerate(modules):
            minutes = float(
                np.clip(
                    rng.lognormal(mean=3.45, sigma=0.42)
                    * (1 + 0.10 * learner_engagement[learner_index])
                    * (1 + module_difficulty[module_index] * 0.35),
                    5,
                    240,
                )
            )
            sessions = int(
                np.clip(
                    rng.poisson(
                        2.2
                        + module_difficulty[module_index]
                        + max(learner_engagement[learner_index], -1) * 0.35
                    ),
                    1,
                    12,
                )
            )
            quiz_score = float(
                np.clip(
                    66
                    + 7 * learner_aptitude[learner_index]
                    + 4.5 * np.log1p(minutes / 10)
                    - 13 * module_difficulty[module_index]
                    + rng.normal(0, 10),
                    0,
                    100,
                )
            )
            completion_probability = 1 / (
                1
                + np.exp(
                    -(
                        1.65
                        + 0.018 * (minutes - 35)
                        + 0.025 * (quiz_score - 60)
                        - 0.75 * module_difficulty[module_index]
                    )
                )
            )

            if rng.random() < 0.055:
                minutes_value: float | None = None
            else:
                minutes_value = round(minutes, 1)
            sessions_value: int | None = (
                None if rng.random() < 0.035 else sessions
            )
            score_value: float | None = (
                None if rng.random() < 0.07 else round(quiz_score, 1)
            )
            records.append(
                {
                    "learner_id": f"L{learner_index + 1:04d}",
                    "learner_group": learner_groups[learner_index],
                    "module": module,
                    "activity_minutes": minutes_value,
                    "sessions": sessions_value,
                    "quiz_score": score_value,
                    "completed": bool(rng.random() < completion_probability),
                }
            )
    return pd.DataFrame.from_records(records)
