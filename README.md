# Job Search Funnel Analytics

A Python and SQL analytics project that converts job application records into funnel metrics, source performance, response timing, and weekly activity trends.

The project follows a practical analyst workflow: define business questions, prepare structured data, calculate KPIs, generate charts, and summarise findings in a written report.

## Business Questions

- Which application sources create the strongest interview opportunities?
- How healthy is the funnel from application to interview to offer?
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

The script reads the dataset from `data/` and writes the report and charts to `outputs/`.

## Output

- Executive report: `outputs/report.md`
- Funnel chart: `outputs/stage_funnel.svg`
- Source performance chart: `outputs/source_breakdown.svg`
- Weekly activity chart: `outputs/applications_by_week.svg`

## Skills Demonstrated

- Data cleaning and validation with Python
- Funnel KPI and source performance analysis
- Response-time and weekly trend analysis
- Reproducible reporting with generated outputs
- SQL queries that match the Python analysis logic
