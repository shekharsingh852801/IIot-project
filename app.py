from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.engagement_analysis import (
    aggregate_learner_modules,
    cohort_summary,
    module_summary,
    prepare_data,
)


st.set_page_config(
    page_title="Online Learning Engagement",
    page_icon="📚",
    layout="wide",
)

CHART_COLORS = ["#2563eb", "#0f766e", "#d97706", "#7c3aed", "#db2777", "#0891b2"]


def show_empty_chart(message: str) -> None:
    st.info(message)


@st.cache_data
def sample_data() -> pd.DataFrame:
    data_path = Path(__file__).resolve().parent / "data" / "online_learning_engagement.csv"
    return pd.read_csv(data_path)


st.title("📚 Online Learning Engagement")
st.caption(
    "Course activity aur learning outcomes ka aggregate analysis — "
    "kisi individual learner ka record dashboard par nahi dikhaya jata."
)

with st.sidebar:
    st.header("Data source")
    data_source = st.radio(
        "Choose dataset",
        ("Synthetic demo", "Upload CSV"),
        help="Demo data fictional hai. Apni file upload karne se pehle identifiers anonymize karein.",
    )
    uploaded_file = None
    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Anonymized learner data (.csv)", type=["csv"])
        st.caption(
            "Required: learner_id, module, activity_minutes, sessions, "
            "quiz_score, completed. Optional: learner_group."
        )

if data_source == "Upload CSV" and uploaded_file is None:
    st.info("Dashboard dekhne ke liye anonymized CSV upload karein, ya Synthetic demo select karein.")
    st.stop()

try:
    if data_source == "Upload CSV":
        assert uploaded_file is not None
        raw_data = pd.read_csv(BytesIO(uploaded_file.getvalue()))
        normalized_data = prepare_data(raw_data)
    else:
        normalized_data = prepare_data(sample_data())
except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as error:
    st.error(f"CSV load nahi ho saka: {error}")
    st.stop()

learner_modules = aggregate_learner_modules(normalized_data)
with st.sidebar:
    st.header("Filters")
    module_options = sorted(learner_modules["module"].unique().tolist())
    selected_modules = st.multiselect("Modules", module_options, default=module_options)
    group_options = sorted(learner_modules["learner_group"].unique().tolist())
    selected_groups = st.multiselect("Learner groups", group_options, default=group_options)

filtered = learner_modules.loc[
    learner_modules["module"].isin(selected_modules)
    & learner_modules["learner_group"].isin(selected_groups)
].copy()

if filtered.empty:
    st.warning("In filters ke liye koi learner-module records nahi mile.")
    st.stop()

source_rows = normalized_data.merge(
    filtered[["learner_id", "module"]].drop_duplicates(),
    on=["learner_id", "module"],
    how="inner",
)
missing_activity_rows = int(source_rows["activity_missing"].sum())
module_data = module_summary(filtered)
group_data = cohort_summary(filtered)

completed_rate = float(filtered["completed"].mean() * 100)
mean_quiz = filtered["quiz_score"].mean()
mean_activity = filtered["activity_minutes"].mean()
missing_activity_pct = (
    missing_activity_rows / len(source_rows) * 100 if len(source_rows) else 0
)

metric_columns = st.columns(4)
metric_columns[0].metric("Completion rate", f"{completed_rate:.1f}%")
metric_columns[1].metric(
    "Average quiz score",
    f"{mean_quiz:.1f}/100" if pd.notna(mean_quiz) else "N/A",
)
metric_columns[2].metric(
    "Activity minutes / learner-module",
    f"{mean_activity:.0f}" if pd.notna(mean_activity) else "N/A",
)
metric_columns[3].metric(
    "Rows with missing activity",
    f"{missing_activity_rows:,} ({missing_activity_pct:.1f}%)",
)

st.caption(
    f"Analysis unit: one unique learner-module pair · "
    f"{filtered['learner_id'].nunique():,} learners · {len(filtered):,} learner-module records"
)

st.subheader("Module comparison")
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    if module_data.empty:
        show_empty_chart("Module completion data available nahi hai.")
    else:
        completion_chart = px.bar(
            module_data,
            x="module",
            y="completion_rate",
            color="module",
            color_discrete_sequence=CHART_COLORS,
            text_auto=".1f",
            labels={"module": "Module", "completion_rate": "Completion rate (%)"},
            title="Completion rate by module",
        )
        completion_chart.update_layout(
            showlegend=False, yaxis_range=[0, 100], yaxis_title="Completion (%)"
        )
        st.plotly_chart(completion_chart, use_container_width=True)

with chart_col2:
    quiz_data = module_data.dropna(subset=["average_quiz_score"])
    if quiz_data.empty:
        show_empty_chart("Selected records mein quiz scores available nahi hain.")
    else:
        quiz_chart = px.bar(
            quiz_data,
            x="module",
            y="average_quiz_score",
            color="module",
            color_discrete_sequence=CHART_COLORS,
            text_auto=".1f",
            labels={"module": "Module", "average_quiz_score": "Average quiz score"},
            title="Average quiz score by module",
        )
        quiz_chart.update_layout(
            showlegend=False, yaxis_range=[0, 100], yaxis_title="Quiz score (0-100)"
        )
        st.plotly_chart(quiz_chart, use_container_width=True)

st.subheader("Engagement, outcomes aur learner groups")
chart_col3, chart_col4 = st.columns(2)
with chart_col3:
    scatter_data = filtered.dropna(subset=["activity_minutes", "quiz_score"])
    if scatter_data.empty:
        show_empty_chart("Activity aur quiz score dono wale records nahi hain.")
    else:
        scatter_chart = px.scatter(
            scatter_data,
            x="activity_minutes",
            y="quiz_score",
            color="module",
            color_discrete_sequence=CHART_COLORS,
            opacity=0.55,
            labels={
                "activity_minutes": "Activity minutes per learner-module",
                "quiz_score": "Quiz score (0-100)",
                "module": "Module",
            },
            title="Activity time vs. quiz performance",
        )
        scatter_chart.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(scatter_chart, use_container_width=True)

with chart_col4:
    if group_data.empty:
        show_empty_chart("Learner group comparison available nahi hai.")
    else:
        group_chart = px.bar(
            group_data,
            x="learner_group",
            y="completion_rate",
            color="learner_group",
            color_discrete_sequence=CHART_COLORS,
            text_auto=".1f",
            labels={
                "learner_group": "Learner group",
                "completion_rate": "Completion rate (%)",
            },
            title="Completion rate by learner group",
        )
        group_chart.update_layout(
            showlegend=False, yaxis_range=[0, 100], yaxis_title="Completion (%)"
        )
        st.plotly_chart(group_chart, use_container_width=True)

with st.expander("Missing activity by module"):
    missing_by_module = (
        source_rows.groupby("module", as_index=False)
        .agg(
            records=("learner_id", "size"),
            missing_activity_rows=("activity_missing", "sum"),
        )
    )
    missing_by_module["missing_rate"] = (
        missing_by_module["missing_activity_rows"] / missing_by_module["records"] * 100
    )
    missing_chart = px.bar(
        missing_by_module,
        x="module",
        y="missing_rate",
        color="module",
        color_discrete_sequence=CHART_COLORS,
        text_auto=".1f",
        labels={"module": "Module", "missing_rate": "Rows with missing activity (%)"},
        title="Activity-data completeness by module",
    )
    missing_chart.update_layout(showlegend=False, yaxis_title="Missing activity (%)")
    st.plotly_chart(missing_chart, use_container_width=True)

st.subheader("Aggregate module metrics")
display_metrics = module_data.rename(
    columns={
        "module": "Module",
        "learner_count": "Learners",
        "completion_rate": "Completion (%)",
        "average_quiz_score": "Avg quiz score",
        "average_activity_minutes": "Avg activity minutes",
        "average_sessions": "Avg sessions",
    }
)
st.dataframe(
    display_metrics.round(1),
    use_container_width=True,
    hide_index=True,
)
download = display_metrics.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download aggregate module summary (CSV)",
    data=download,
    file_name="module_engagement_summary.csv",
    mime="text/csv",
)

st.subheader("What the data suggests")
recommendations: list[str] = []
if not module_data.empty:
    lowest_completion = module_data.loc[module_data["completion_rate"].idxmin()]
    highest_completion = module_data.loc[module_data["completion_rate"].idxmax()]
    if highest_completion["module"] != lowest_completion["module"]:
        recommendations.append(
            f"'{lowest_completion['module']}' ki completion "
            f"'{highest_completion['module']}' se "
            f"{highest_completion['completion_rate'] - lowest_completion['completion_rate']:.1f} "
            "percentage points kam hai. Is module ke lesson length, prerequisites aur "
            "assessment friction ko review karein."
        )
    if pd.notna(lowest_completion["average_quiz_score"]):
        recommendations.append(
            f"'{lowest_completion['module']}' ke liye practice questions aur formative feedback "
            "ko review karein; quiz score ko completion ke saath dekhkar support points identify karein."
        )
if missing_activity_pct > 5:
    recommendations.append(
        f"{missing_activity_pct:.1f}% source rows mein activity field missing hai. "
        "Tracking instrumentation aur event delivery ko validate karein; missing values ko zero na samjhein."
    )
if not recommendations:
    recommendations.append(
        "Metrics mein koi ek clear outlier nahi mila. Module-level trends monitor karein aur "
        "learner feedback ke saath interpretation validate karein."
    )
for recommendation in recommendations:
    st.markdown(f"- {recommendation}")

st.caption(
    "Engagement ko activity minutes aur sessions ke observable proxies se dikhaya gaya hai; "
    "ye learner motivation ka direct measure nahi hain. Correlation causation prove nahi karti. "
    "Quiz score available submissions ka average hai; missing score ko zero nahi maana gaya."
)
