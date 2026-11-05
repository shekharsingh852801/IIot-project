# Online Learning Engagement Analysis (DA-015)

Streamlit dashboard and reproducible analysis project for exploring how course
activity, quiz performance, and completion vary by module and learner group.
The included dataset is synthetic; uploads are analyzed in memory and are not
written to disk.

## What this project answers

- Which modules have relatively low completion or quiz performance?
- How do activity minutes and session counts vary across modules?
- How are activity time and quiz scores associated?
- How do completion rates differ across broad learner groups?
- Where are activity-tracking records missing?

These are descriptive questions. The charts do not establish that activity
causes improved learning or completion.

## Metrics and data rules

**Analysis unit:** one unique learner-module pair. If a CSV has multiple
activity rows for a pair, activity minutes and sessions are summed, quiz scores
are averaged, and completion is true if any row marks the pair complete.

**Engagement:** observable activity minutes and session counts. They are
reported as separate proxies, not combined into a score and not interpreted as
motivation.

**Completion rate:** completed learner-module pairs divided by all learner-module
pairs, shown as a percentage. A row is complete when its `completed` value is
true/yes/1/completed; false/no/0/incomplete means not complete.

**Quiz performance:** arithmetic mean of available quiz scores (0-100).
Missing scores are excluded, not treated as zero.

**Missing activity:** an input row is marked missing when either
`activity_minutes` or `sessions` is blank. Missing values are preserved rather
than silently converted to zero. The module aggregates sum known values; if all
values for a metric are missing, its aggregate remains missing.

## CSV schema

Required columns:

| Column | Meaning | Rules |
|---|---|---|
| `learner_id` | Pseudonymous key used only to count/deduplicate learners | Required, non-empty; never shown in dashboard tables |
| `module` | Course module name | Required, non-empty |
| `activity_minutes` | Time spent in the module | Non-negative number or blank |
| `sessions` | Activity sessions in the module | Non-negative number or blank |
| `quiz_score` | Score for the module quiz | Number from 0 to 100 or blank |
| `completed` | Module completion status | true/false, yes/no, 1/0, completed/incomplete |

Optional: `learner_group`, such as cohort or learning format. If omitted or
blank, records are assigned to `Not specified`. Each learner must belong to one
group in a file. Column names are case-sensitive.

Before uploading, remove direct identifiers and use a consistent, pseudonymous
`learner_id`. The app shows only aggregate measures, not individual rows or
identifiers. The aggregate CSV download contains module summaries only.

## Dashboard

The app includes:

1. Completion rate by module.
2. Average quiz score by module.
3. Activity minutes versus quiz score scatter plot.
4. Completion rate by learner group.
5. Missing-activity rate by module.

Module and learner-group filters update the KPIs, charts, missingness view, and
aggregate module table. Suggested design actions are generated from observed
patterns and should be validated with learner feedback and course context.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Choose **Synthetic demo** to explore the dashboard without a file, or choose
**Upload CSV** to analyze an anonymized CSV.

Run the analysis tests:

```bash
pytest -q
```

## Generate data and static charts

```bash
python data/generate_dataset.py
python src/visualize.py
```

Static charts are written to `charts/`. The interactive dashboard reads the
checked-in synthetic CSV by default; regenerate it with the fixed seed when
needed.

## Project plan and implementation map

| Phase | Deliverable | Status |
|---|---|---|
| 1. Define scope and measures | Analysis unit, engagement proxies, completion, missing-data policy, privacy boundary | Complete |
| 2. Prepare data | Deterministic fictional learner-module CSV and validation/normalization | Complete |
| 3. Analyze outcomes | Learner-module aggregation, module/group summaries, quiz and activity metrics | Complete |
| 4. Build visualizations | Five static PNG charts and five interactive dashboard charts | Complete |
| 5. Document and verify | Analysis notebook, project report, and automated tests | Complete |
| 6. Extend with real data | Validate tracking definitions, cohort policy, and interpretation with the provider | Next step |

### Repository layout

```text
app.py                              Streamlit UI and chart/filter wiring
data/
  generate_dataset.py               Reproducible synthetic data generator
  online_learning_engagement.csv    420 fictional learners x 6 modules
src/
  clean_data.py                     CSV loading and cleaning interface
  engagement_analysis.py            Validation and learner-module aggregation
  metrics.py                        Summary and association metrics
  sample_data.py                    Synthetic data generation logic
  visualize.py                      Static PNG chart generation
charts/                             Five generated chart images
docs/
  PROJECT_REPORT.md                 Detailed methodology and recommendations
notebooks/
  engagement_analysis.ipynb         Reproducible exploratory analysis
tests/
  test_engagement_analysis.py       Validation and aggregation tests
requirements.txt
```

## Interpretation cautions

- The demo is fictional; its patterns are for exercising the dashboard, not
  evidence about real learners.
- Activity volume may reflect course length, accessibility needs, or offline
  learning, so more activity is not automatically better.
- Group differences can be confounded by prior knowledge, module order, or
  learner support. Avoid ranking small groups without appropriate safeguards.
- Missing tracking data can bias every comparison. Check instrumentation before
  drawing conclusions.
- This dashboard reports descriptive aggregates and must not be used to make
  high-stakes decisions about individual students.
