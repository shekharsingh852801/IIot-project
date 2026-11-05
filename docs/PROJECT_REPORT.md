# Online Learning Engagement Analysis

**Project ID:** DA-015  
**Domain:** EdTech Analytics  
**Project type:** Descriptive analytics and learning-experience design

## 1. Problem statement

An online learning provider needs to understand how course engagement and
completion vary across modules and broad learner groups. Completion alone does
not explain where learners may be spending time, how they perform on module
quizzes, or whether activity tracking is complete.

This project summarizes activity minutes, session counts, quiz performance,
completion, and missing activity records. It is designed to help course teams
identify modules worth reviewing—not to score or identify individual learners.

## 2. Questions

1. How does completion rate differ by module?
2. How do average quiz score and recorded activity vary across modules?
3. What relationship is visible between activity minutes and quiz scores?
4. How does completion vary by learner group?
5. Are missing activity records concentrated in particular modules?

## 3. Data and privacy

The committed demo dataset is deterministic synthetic data: 420 fictional
pseudonymous learners across six modules (2,520 learner-module records). It
includes broad learning-format groups and intentionally missing activity and
quiz fields. It contains no real student data.

For real data, remove direct identifiers before upload, use a consistent
pseudonymous learner key, and ensure the provider is authorized to process the
dataset. The dashboard renders aggregate outputs only and does not display
learner-level rows.

## 4. Definitions and methodology

### Analysis unit

One unique learner-module pair. If source data contains multiple rows for that
pair, activity minutes and sessions are summed, quiz scores are averaged, and
the pair is marked complete if any row indicates completion.

### Engagement

Engagement is represented by two separate observable proxies:

- **Activity minutes:** time recorded in a module.
- **Sessions:** number of recorded module activity sessions.

The project does not combine these into a composite engagement score. They are
not direct measures of motivation, attention, or learning.

### Outcome measures

- **Completion rate:** completed learner-module pairs / all learner-module
  pairs x 100.
- **Average quiz score:** arithmetic mean of available scores on a 0-100 scale.
  Missing scores are excluded, not set to zero.
- **Activity-score correlation:** Pearson correlation for pairs where both
  activity minutes and quiz score are observed. This is descriptive and is not
  evidence of causality.

### Missing activity

A source row is flagged when either minutes or sessions is missing. Blank
activity is not silently converted to zero. Module totals preserve the sum of
observed values; if every value for a metric is missing, its result remains
missing.

## 5. Visual analysis

The static chart exports and interactive dashboard cover:

1. Module completion rate and average quiz score.
2. Average activity minutes by module.
3. Activity minutes versus quiz score, colored by module.
4. Completion rate across learner groups.
5. Missing activity rate by module.

The synthetic data is generated for application/testing purposes. Any patterns
in its charts are artificial and must not be presented as evidence about actual
students or courses.

## 6. Recommendations for a real deployment

- Review module lesson length, prerequisites, clarity, and assessment friction
  when a module shows comparatively low completion.
- Check formative practice and feedback when quiz performance is low; do not
  assume more time alone will improve scores.
- Validate event instrumentation when activity fields are missing, before
  comparing engagement across modules or groups.
- Combine aggregate trends with learner feedback and course context.
- Avoid ranking small learner groups or using these metrics for high-stakes
  individual decisions.
- Reassess comparisons for module order, prior knowledge, accessibility, and
  support differences that can confound group-level patterns.

## 7. Limitations

- Demo data is simulated and does not generalize to a real provider.
- Time-on-task can be affected by playback, idle sessions, accessibility
  requirements, and learning outside the platform.
- A recorded completion flag may not represent durable knowledge.
- Group differences are descriptive and may reflect confounding factors.
- Missing tracking may be systematic rather than random.

## 8. Reproducibility

```bash
python data/generate_dataset.py
python src/visualize.py
pytest -q
streamlit run app.py
```

The generator uses a fixed random seed; reruns reproduce the same dataset.
