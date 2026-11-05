"""Generate static, shareable charts from the synthetic demo dataset."""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.clean_data import aggregate_learner_modules, load_and_clean_data
from src.metrics import activity_score_correlation, module_summary


DATA_PATH = ROOT / "data" / "online_learning_engagement.csv"
CHART_DIR = ROOT / "charts"
PALETTE = "viridis"


def _save(fig: plt.Figure, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(CHART_DIR / filename, dpi=160, bbox_inches="tight")
    plt.close(fig)


def create_charts(data: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    learner_modules = aggregate_learner_modules(data)
    summary = module_summary(learner_modules)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig, axis = plt.subplots(figsize=(11, 6))
    plot_data = summary.melt(
        id_vars="module",
        value_vars=["completion_rate", "average_quiz_score"],
        var_name="metric",
        value_name="percent",
    )
    plot_data["metric"] = plot_data["metric"].map(
        {
            "completion_rate": "Completion rate",
            "average_quiz_score": "Average quiz score",
        }
    )
    sns.barplot(
        data=plot_data,
        x="module",
        y="percent",
        hue="metric",
        palette=["#2563eb", "#0f766e"],
        ax=axis,
    )
    axis.set(title="Module Completion and Quiz Performance", xlabel="", ylabel="Percent")
    axis.set_ylim(0, 100)
    axis.tick_params(axis="x", rotation=20)
    _save(fig, "01_module_completion_quiz.png")

    fig, axis = plt.subplots(figsize=(11, 6))
    sns.barplot(
        data=summary,
        x="module",
        y="average_activity_minutes",
        hue="module",
        palette=PALETTE,
        legend=False,
        ax=axis,
    )
    axis.set(
        title="Average Recorded Activity by Module",
        xlabel="",
        ylabel="Minutes per learner-module",
    )
    axis.tick_params(axis="x", rotation=20)
    _save(fig, "02_module_activity.png")

    fig, axis = plt.subplots(figsize=(10, 6))
    score_data = learner_modules.dropna(subset=["activity_minutes", "quiz_score"])
    sns.scatterplot(
        data=score_data,
        x="activity_minutes",
        y="quiz_score",
        hue="module",
        palette=PALETTE,
        alpha=0.55,
        s=24,
        ax=axis,
    )
    correlation = activity_score_correlation(learner_modules)
    axis.set(
        title=f"Activity Time vs Quiz Score (Pearson r = {correlation:.2f})",
        xlabel="Activity minutes per learner-module",
        ylabel="Quiz score (0-100)",
    )
    axis.set_ylim(0, 100)
    _save(fig, "03_activity_vs_quiz.png")

    group_summary = (
        learner_modules.groupby("learner_group", as_index=False)
        .agg(
            learner_count=("learner_id", "nunique"),
            completion_rate=("completed", "mean"),
        )
    )
    group_summary["completion_rate"] *= 100
    fig, axis = plt.subplots(figsize=(9, 6))
    sns.barplot(
        data=group_summary,
        x="learner_group",
        y="completion_rate",
        hue="learner_group",
        palette=PALETTE,
        legend=False,
        ax=axis,
    )
    axis.set(title="Completion by Learner Group", xlabel="", ylabel="Completion rate (%)")
    axis.set_ylim(0, 100)
    axis.tick_params(axis="x", rotation=15)
    _save(fig, "04_group_completion.png")

    missing_by_module = (
        data.groupby("module", as_index=False)
        .agg(
            records=("learner_id", "size"),
            missing_records=("activity_missing", "sum"),
        )
    )
    missing_by_module["missing_rate"] = (
        missing_by_module["missing_records"] / missing_by_module["records"] * 100
    )
    fig, axis = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=missing_by_module,
        x="module",
        y="missing_rate",
        hue="module",
        palette=PALETTE,
        legend=False,
        ax=axis,
    )
    axis.set(
        title="Missing Activity Records by Module",
        xlabel="",
        ylabel="Rows missing minutes or sessions (%)",
    )
    axis.tick_params(axis="x", rotation=20)
    _save(fig, "05_missing_activity.png")
    print(f"Created 5 charts in {CHART_DIR}")


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Demo CSV not found at {DATA_PATH}. Run `python data/generate_dataset.py` first."
        )
    create_charts(load_and_clean_data(str(DATA_PATH)))


if __name__ == "__main__":
    main()
