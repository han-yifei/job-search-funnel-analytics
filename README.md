# Job Search Funnel Analytics

A reproducible data analysis project that turns job application tracking data into funnel metrics, source performance, and weekly activity trends.

This project is designed as a portfolio-ready example for data analyst roles. It shows how to define business questions, clean structured data, calculate KPIs, and communicate insights with charts and a written report.

## Business Questions

- Which application sources create the strongest interview opportunities?
- How healthy is the job search funnel from application to interview to offer?
- How consistent is weekly application activity?
- How long does it take to receive a first response?

## Project Structure

```text
.
├── data/
│   └── job_applications_sample.csv
├── outputs/
│   ├── applications_by_week.svg
│   ├── report.md
│   ├── source_breakdown.svg
│   └── stage_funnel.svg
├── sql/
│   └── job_funnel_queries.sql
└── src/
    └── analyze_job_search.py
```

## How To Run

This project uses only the Python standard library.

```bash
python3 src/analyze_job_search.py
```

The script reads `data/job_applications_sample.csv` and writes the analysis to `outputs/`.

## Key Skills Demonstrated

- Data cleaning and validation with Python
- KPI design for funnel analysis
- Date parsing and time-to-response analysis
- Grouped aggregation by channel, stage, and week
- Reproducible reporting
- SQL translation of analysis logic

## Notes

The included CSV is sample data for demonstration. For real use, replace it with your own application tracking data using the same column names.
