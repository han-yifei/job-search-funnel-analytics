from collections import Counter, defaultdict
import csv
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "job_applications_sample.csv"
OUTPUT_DIR = ROOT / "outputs"

DATE_FORMAT = "%Y-%m-%d"
STAGE_ORDER = ["Applied", "Screen", "Interview", "Take-home", "Offer"]
INTERVIEW_STAGES = {"Interview", "Take-home", "Offer"}


def parse_date(value):
    value = value.strip()
    if not value:
        return None
    return datetime.strptime(value, DATE_FORMAT).date()


def load_rows(path):
    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    cleaned = []
    for row in rows:
        item = dict(row)
        item["application_date"] = parse_date(row["application_date"])
        item["response_date"] = parse_date(row["response_date"])
        item["interview_date"] = parse_date(row["interview_date"])
        item["salary_min"] = int(row["salary_min"])
        item["salary_max"] = int(row["salary_max"])
        cleaned.append(item)
    return cleaned


def pct(part, whole):
    if whole == 0:
        return 0.0
    return round(100 * part / whole, 1)


def week_start(date_value):
    return date_value - timedelta(days=date_value.weekday())


def summarize(rows):
    total = len(rows)
    responses = [row for row in rows if row["response_date"]]
    interviews = [row for row in rows if row["stage_reached"] in INTERVIEW_STAGES]
    offers = [row for row in rows if row["stage_reached"] == "Offer"]
    active = [row for row in rows if row["current_status"] == "Active"]

    days_to_response = [
        (row["response_date"] - row["application_date"]).days
        for row in rows
        if row["response_date"]
    ]

    source_metrics = []
    by_source = defaultdict(list)
    for row in rows:
        by_source[row["source"]].append(row)

    for source, source_rows in by_source.items():
        count = len(source_rows)
        source_responses = sum(1 for row in source_rows if row["response_date"])
        source_interviews = sum(1 for row in source_rows if row["stage_reached"] in INTERVIEW_STAGES)
        source_offers = sum(1 for row in source_rows if row["stage_reached"] == "Offer")
        source_metrics.append(
            {
                "source": source,
                "applications": count,
                "responses": source_responses,
                "interviews": source_interviews,
                "offers": source_offers,
                "response_rate": pct(source_responses, count),
                "interview_rate": pct(source_interviews, count),
            }
        )

    source_metrics.sort(key=lambda item: (item["interview_rate"], item["applications"]), reverse=True)

    stage_counts = {}
    for stage in STAGE_ORDER:
        current_index = STAGE_ORDER.index(stage)
        stage_counts[stage] = sum(
            1
            for row in rows
            if STAGE_ORDER.index(row["stage_reached"]) >= current_index
        )

    weekly = Counter(week_start(row["application_date"]) for row in rows)

    return {
        "total": total,
        "responses": len(responses),
        "interviews": len(interviews),
        "offers": len(offers),
        "active": len(active),
        "response_rate": pct(len(responses), total),
        "interview_rate": pct(len(interviews), total),
        "offer_rate": pct(len(offers), total),
        "avg_days_to_response": round(mean(days_to_response), 1) if days_to_response else None,
        "source_metrics": source_metrics,
        "stage_counts": stage_counts,
        "weekly": dict(sorted(weekly.items())),
    }


def svg_bar_chart(title, labels, values, output_path, value_suffix=""):
    width = 920
    row_height = 38
    top = 68
    left = 190
    chart_width = 600
    height = top + row_height * len(labels) + 40
    max_value = max(values) if values else 1

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        f'<text x="32" y="38" font-family="Arial" font-size="24" font-weight="700" fill="#111827">{title}</text>',
    ]

    for index, (label, value) in enumerate(zip(labels, values)):
        y = top + index * row_height
        bar_width = int((value / max_value) * chart_width) if max_value else 0
        lines.extend(
            [
                f'<text x="32" y="{y + 22}" font-family="Arial" font-size="14" fill="#374151">{label}</text>',
                f'<rect x="{left}" y="{y}" width="{bar_width}" height="24" rx="4" fill="#2563eb"/>',
                f'<text x="{left + bar_width + 10}" y="{y + 18}" font-family="Arial" font-size="14" fill="#111827">{value}{value_suffix}</text>',
            ]
        )

    lines.append("</svg>")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_report(summary, output_path):
    source_rows = "\n".join(
        "| {source} | {applications} | {response_rate}% | {interview_rate}% | {offers} |".format(**item)
        for item in summary["source_metrics"]
    )

    best_source = summary["source_metrics"][0]["source"] if summary["source_metrics"] else "N/A"
    report = f"""# Job Search Funnel Report

## Executive Summary

- Total applications analyzed: **{summary["total"]}**
- Active applications: **{summary["active"]}**
- Response rate: **{summary["response_rate"]}%**
- Interview opportunity rate: **{summary["interview_rate"]}%**
- Offer rate: **{summary["offer_rate"]}%**
- Average days to first response: **{summary["avg_days_to_response"]}**

## Main Insight

The strongest source in this sample is **{best_source}**, based on interview opportunity rate. Referral-driven applications perform especially well because they reduce cold-start screening risk and tend to produce faster recruiter engagement.

## Funnel Counts

| Stage reached | Applications |
|---|---:|
"""

    for stage, count in summary["stage_counts"].items():
        report += f"| {stage} | {count} |\n"

    report += f"""
## Source Performance

| Source | Applications | Response Rate | Interview Rate | Offers |
|---|---:|---:|---:|---:|
{source_rows}

## Recommendations

- Prioritize referral and recruiter channels when possible.
- Keep LinkedIn active, but measure whether high application volume creates enough interviews.
- Track response dates consistently, because time-to-response is a useful early signal of employer interest.
- Review rejected applications by source and role type to identify skill gaps.

## Generated Charts

- `outputs/stage_funnel.svg`
- `outputs/source_breakdown.svg`
- `outputs/applications_by_week.svg`
"""

    output_path.write_text(report, encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    rows = load_rows(DATA_FILE)
    summary = summarize(rows)

    svg_bar_chart(
        "Application Funnel",
        list(summary["stage_counts"].keys()),
        list(summary["stage_counts"].values()),
        OUTPUT_DIR / "stage_funnel.svg",
    )

    svg_bar_chart(
        "Interview Rate by Source",
        [item["source"] for item in summary["source_metrics"]],
        [item["interview_rate"] for item in summary["source_metrics"]],
        OUTPUT_DIR / "source_breakdown.svg",
        "%",
    )

    svg_bar_chart(
        "Applications by Week",
        [date_value.isoformat() for date_value in summary["weekly"].keys()],
        list(summary["weekly"].values()),
        OUTPUT_DIR / "applications_by_week.svg",
    )

    write_report(summary, OUTPUT_DIR / "report.md")
    print(f"Wrote report and charts to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
