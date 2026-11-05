from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

REQUIRED_COLUMNS = {
    "learner_id",
    "module",
    "activity_minutes",
    "sessions",
    "quiz_score",
    "completed",
}
OPTIONAL_COLUMNS = {"learner_group"}
COMPLETION_VALUES = {
    "true": True,
    "false": False,
    "1": True,
    "0": False,
    "yes": True,
    "no": False,
    "y": True,
    "n": False,
    "completed": True,
    "incomplete": False,
}


def _numeric_column(data: pd.DataFrame, column: str) -> pd.Series:
    original = data[column]
    numeric = pd.to_numeric(original, errors="coerce")
    invalid = original.notna() & numeric.isna() & original.astype(str).str.strip().ne("")
    if invalid.any():
        examples = original.loc[invalid].astype(str).drop_duplicates().head(3).tolist()
        raise ValueError(f"'{column}' contains non-numeric values: {examples}")
    return numeric


def _completion_column(values: pd.Series) -> pd.Series:
    normalized = values.astype("string").str.strip().str.lower()
    parsed = normalized.map(COMPLETION_VALUES)
    invalid = values.isna() | parsed.isna()
    if invalid.any():
        examples = values.loc[invalid].astype(str).drop_duplicates().head(3).tolist()
        raise ValueError(
            "'completed' must contain true/false, yes/no, 1/0, "
            f"completed/incomplete values; invalid examples: {examples}"
        )
    return parsed.astype(bool)


def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
    """Validate input and normalize it without dropping missing activity observations."""
    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing_columns))}")

    normalized = data.copy()
    if "learner_group" not in normalized:
        normalized["learner_group"] = "Not specified"

    for column in ("learner_id", "module", "learner_group"):
        normalized[column] = normalized[column].astype("string").str.strip()
    if normalized["learner_id"].isna().any() or normalized["learner_id"].eq("").any():
        raise ValueError("'learner_id' cannot be empty.")
    if normalized["module"].isna().any() or normalized["module"].eq("").any():
        raise ValueError("'module' cannot be empty.")
    normalized["learner_group"] = normalized["learner_group"].fillna("Not specified")
    normalized.loc[normalized["learner_group"].eq(""), "learner_group"] = "Not specified"

    for column in ("activity_minutes", "sessions", "quiz_score"):
        normalized[column] = _numeric_column(normalized, column)
    if (normalized["activity_minutes"].dropna() < 0).any():
        raise ValueError("'activity_minutes' cannot be negative.")
    if (normalized["sessions"].dropna() < 0).any():
        raise ValueError("'sessions' cannot be negative.")
    quiz_scores = normalized["quiz_score"].dropna()
    if ((quiz_scores < 0) | (quiz_scores > 100)).any():
        raise ValueError("'quiz_score' must be between 0 and 100.")
    normalized["completed"] = _completion_column(normalized["completed"])

    groups_per_learner = normalized.groupby("learner_id")["learner_group"].nunique()
    if (groups_per_learner > 1).any():
        raise ValueError("Each learner must belong to only one learner_group.")

    normalized["activity_missing"] = normalized[
        ["activity_minutes", "sessions"]
    ].isna().any(axis=1)
    return normalized


def _sum_observed(values: Iterable[float]) -> float:
    return values.sum(min_count=1)


def aggregate_learner_modules(data: pd.DataFrame) -> pd.DataFrame:
    """Return one row per learner-module; keep entirely missing activity as missing."""
    return (
        data.groupby(["learner_id", "module"], as_index=False, dropna=False)
        .agg(
            learner_group=("learner_group", "first"),
            activity_minutes=("activity_minutes", _sum_observed),
            sessions=("sessions", _sum_observed),
            quiz_score=("quiz_score", "mean"),
            completed=("completed", "max"),
            activity_missing_records=("activity_missing", "sum"),
        )
    )


def module_summary(learner_modules: pd.DataFrame) -> pd.DataFrame:
    """Summarize learner-module records by course module."""
    if learner_modules.empty:
        return pd.DataFrame(
            columns=[
                "module",
                "learner_count",
                "completion_rate",
                "average_quiz_score",
                "average_activity_minutes",
                "average_sessions",
            ]
        )
    return (
        learner_modules.groupby("module", as_index=False)
        .agg(
            learner_count=("learner_id", "nunique"),
            completion_rate=("completed", "mean"),
            average_quiz_score=("quiz_score", "mean"),
            average_activity_minutes=("activity_minutes", "mean"),
            average_sessions=("sessions", "mean"),
        )
        .assign(
            completion_rate=lambda frame: frame["completion_rate"] * 100,
        )
        .sort_values("module")
        .reset_index(drop=True)
    )


def cohort_summary(learner_modules: pd.DataFrame) -> pd.DataFrame:
    """Summarize completion by learner group across the selected modules."""
    if learner_modules.empty:
        return pd.DataFrame(columns=["learner_group", "learner_count", "completion_rate"])
    return (
        learner_modules.groupby("learner_group", as_index=False)
        .agg(
            learner_count=("learner_id", "nunique"),
            completion_rate=("completed", "mean"),
        )
        .assign(completion_rate=lambda frame: frame["completion_rate"] * 100)
        .sort_values("learner_group")
        .reset_index(drop=True)
    )
