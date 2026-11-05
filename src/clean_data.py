"""Input cleaning and learner-module aggregation."""

import pandas as pd

from src.engagement_analysis import aggregate_learner_modules, prepare_data


def load_and_clean_data(path: str) -> pd.DataFrame:
    """Load a CSV file and validate its columns and values."""
    return prepare_data(pd.read_csv(path))


__all__ = ["aggregate_learner_modules", "load_and_clean_data", "prepare_data"]
