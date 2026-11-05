import pandas as pd
import pytest

from src.engagement_analysis import (
    aggregate_learner_modules,
    cohort_summary,
    module_summary,
    prepare_data,
)


@pytest.fixture
def example_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "learner_id": ["a", "a", "b"],
            "learner_group": ["Group 1", "Group 1", "Group 2"],
            "module": ["Module 1", "Module 1", "Module 1"],
            "activity_minutes": [10, None, 20],
            "sessions": [1, 2, 1],
            "quiz_score": [80, 90, None],
            "completed": ["yes", "no", "true"],
        }
    )


def test_prepare_data_keeps_missing_activity_and_normalizes_completion(
    example_data: pd.DataFrame,
) -> None:
    prepared = prepare_data(example_data)

    assert prepared["completed"].tolist() == [True, False, True]
    assert prepared["activity_missing"].tolist() == [False, True, False]


def test_aggregation_uses_one_learner_module_and_preserves_partial_activity(
    example_data: pd.DataFrame,
) -> None:
    result = aggregate_learner_modules(prepare_data(example_data))

    learner_a = result.loc[result["learner_id"].eq("a")].iloc[0]
    assert len(result) == 2
    assert learner_a["activity_minutes"] == 10
    assert learner_a["sessions"] == 3
    assert learner_a["quiz_score"] == 85
    assert learner_a["completed"]
    assert learner_a["activity_missing_records"] == 1


def test_module_and_group_summaries_use_percentage_completion(
    example_data: pd.DataFrame,
) -> None:
    aggregated = aggregate_learner_modules(prepare_data(example_data))

    module = module_summary(aggregated).iloc[0]
    groups = cohort_summary(aggregated)
    assert module["learner_count"] == 2
    assert module["completion_rate"] == 100
    assert set(groups["completion_rate"]) == {100}


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [
        ("activity_minutes", -1, "cannot be negative"),
        ("sessions", -1, "cannot be negative"),
        ("quiz_score", 101, "between 0 and 100"),
        ("completed", "maybe", "must contain"),
        ("learner_id", "", "cannot be empty"),
    ],
)
def test_invalid_values_are_reported(
    example_data: pd.DataFrame, column: str, value: object, message: str
) -> None:
    example_data.loc[0, column] = value

    with pytest.raises(ValueError, match=message):
        prepare_data(example_data)


def test_missing_required_column_is_reported(example_data: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="Missing required columns"):
        prepare_data(example_data.drop(columns="module"))


def test_learner_cannot_have_multiple_groups(example_data: pd.DataFrame) -> None:
    example_data.loc[1, "learner_group"] = "Group 2"

    with pytest.raises(ValueError, match="only one learner_group"):
        prepare_data(example_data)
