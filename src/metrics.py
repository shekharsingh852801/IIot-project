"""Engagement and learning-outcome summary metrics."""

import pandas as pd

from src.engagement_analysis import cohort_summary, module_summary


def activity_score_correlation(learner_modules: pd.DataFrame) -> float:
    """Return descriptive Pearson correlation for available activity and scores."""
    paired = learner_modules[["activity_minutes", "quiz_score"]].dropna()
    if len(paired) < 2:
        return float("nan")
    if paired["activity_minutes"].nunique() < 2 or paired["quiz_score"].nunique() < 2:
        return float("nan")
    return float(paired["activity_minutes"].corr(paired["quiz_score"]))


__all__ = ["activity_score_correlation", "cohort_summary", "module_summary"]
