import csv
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "job_applications_sample.csv"
OUTPUT_DIR = ROOT / "outputs"

DATE_FORMAT = "%Y-%m-%d"
STAGE_ORDER = ["Applied", "Screen", "Interview", "Take-home", "Offer"]
INTERVIEW_STAGES = ["Interview", "Take-home", "Offer"]


def parse_date(text):
    if text == "":
        return None
    return datetime.strptime(text, DATE_FORMAT).date()


def percent(part, total):
    if total == 0:
        return 0
    return round(part / total * 100, 1)


def get_week_start(date_value):
    return date_value - timedelta(days=date_value.weekday())


def read_applications():
    applications = []

    with DATA_FILE.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["application_date"] = parse_date(row["application_date"])
            row["response_date"] = parse_date(row["response_date"])
            row["interview_date"] = parse_date(row["interview_date"])
            row["salary_min"] = int(row["salary_min"])
            row["salary_max"] = int(row["salary_max"])
            applications.append(row)

    return applications


def count_funnel_stage(applications, stage):
    stage_index = STAGE_ORDER.index(stage)
    count = 0

    for application in applications:
        reached_stage = application["stage_reached"]
        reached_index = STAGE_ORDER.index(reached_stage)

        if reached_index >= stage_index:
            count += 1

    return count


def analyse_applications(applications):
    total_applications = len(applications)
    response_count = 0
    interview_count = 0
    offer_count = 0
    active_count = 0
    total_days_to_response = 0

    source_summary = {}
    weekly_summary = {}

    for application in applications:
        source = application["source"]
        stage = application["stage_reached"]
        status = application["current_status"]
        response_date = application["response_date"]
        application_date = application["application_date"]

        if source not in source_summary:
            source_summary[source] = {
                "source": source,
                "applications": 0,
                "responses": 0,
                "interviews": 0,
                "offers": 0,
            }

        source_summary[source]["applications"] += 1

        if response_date is not None:
            response_count += 1
            source_summary[source]["responses"] += 1
            total_days_to_response += (response_date - application_date).days

        if stage in INTERVIEW_STAGES:
            interview_count += 1
            source_summary[source]["interviews"] += 1

        if stage == "Offer":
            offer_count += 1
            source_summary[source]["offers"] += 1

        if status == "Active":
            active_count += 1

        week = get_week_start(application_date)
        if week not in weekly_summary:
            weekly_summary[week] = 0
        weekly_summary[week] += 1

    sources = []
    for source_name in source_summary:
        item = source_summary[source_name]
        item["response_rate"] = percent(item["responses"], item["applications"])
        item["interview_rate"] = percent(item["interviews"], item["applications"])
        sources.append(item)

    sources.sort(key=lambda item: item["interview_rate"], reverse=True)

    stage_counts = {}
    for stage in STAGE_ORDER:
        stage_counts[stage] = count_funnel_stage(applications, stage)

    if response_count > 0:
        average_days_to_response = round(total_days_to_response / response_count, 1)
    else:
        average_days_to_response = 0

    return {
        "total": total_applications,
        "active": active_count,
        "responses": response_count,
        "interviews": interview_count,
        "offers": offer_count,
        "response_rate": percent(response_count, total_applications),
        "interview_rate": percent(interview_count, total_applications),
        "offer_rate": percent(offer_count, total_applications),
        "avg_days_to_response": average_days_to_response,
        "sources": sources,
        "stage_counts": stage_counts,
        "weekly_summary": dict(sorted(weekly_summary.items())),
    }


def save_bar_chart(title, labels, values, output_file, suffix=""):
    width = 920
    row_height = 38
    top = 68
    left = 190
    chart_width = 600
    height = top + row_height * len(labels) + 40
    biggest_value = max(values)

    svg_lines = []
    svg_lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    )
    svg_lines.append('<rect width="100%" height="100%" fill="#f8fafc"/>')
    svg_lines.append(
        f'<text x="32" y="38" font-family="Arial" font-size="24" font-weight="700" fill="#111827">{title}</text>'
    )

    for index in range(len(labels)):
        label = labels[index]
        value = values[index]
        y = top + index * row_height
        bar_width = int(value / biggest_value * chart_width)

        svg_lines.append(
            f'<text x="32" y="{y + 22}" font-family="Arial" font-size="14" fill="#374151">{label}</text>'
        )
        svg_lines.append(
            f'<rect x="{left}" y="{y}" width="{bar_width}" height="24" rx="4" fill="#2563eb"/>'
        )
        svg_lines.append(
            f'<text x="{left + bar_width + 10}" y="{y + 18}" font-family="Arial" font-size="14" fill="#111827">{value}{suffix}</text>'
        )

    svg_lines.append("</svg>")
    output_file.write_text("\n".join(svg_lines) + "\n", encoding="utf-8")


def save_report(summary):
    best_source = summary["sources"][0]
    offer_context = ""

    if summary["offers"] == 1 and best_source["offers"] == 1:
        offer_context = " and the only offer recorded in the period"

    report = f"""# Job Search Funnel Report

## Executive Summary

- Total applications analyzed: **{summary["total"]}**
- Active applications: **{summary["active"]}**
- Response rate: **{summary["response_rate"]}%**
- Interview opportunity rate: **{summary["interview_rate"]}%**
- Offer rate: **{summary["offer_rate"]}%**
- Average days to first response: **{summary["avg_days_to_response"]}**

## Main Insight

**{best_source["source"]}** is the strongest source by interview opportunity rate. It produced the highest conversion from application to interview-stage outcomes{offer_context}.

## Funnel Counts

| Stage reached | Applications |
|---|---:|
"""

    for stage in summary["stage_counts"]:
        count = summary["stage_counts"][stage]
        report += f"| {stage} | {count} |\n"

    report += """
## Source Performance

| Source | Applications | Response Rate | Interview Rate | Offers |
|---|---:|---:|---:|---:|
"""

    for source in summary["sources"]:
        report += (
            f"| {source['source']} | {source['applications']} | "
            f"{source['response_rate']}% | {source['interview_rate']}% | {source['offers']} |\n"
        )

    report += """
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

    (OUTPUT_DIR / "report.md").write_text(report, encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    applications = read_applications()
    summary = analyse_applications(applications)

    save_bar_chart(
        "Application Funnel",
        list(summary["stage_counts"].keys()),
        list(summary["stage_counts"].values()),
        OUTPUT_DIR / "stage_funnel.svg",
    )

    save_bar_chart(
        "Interview Rate by Source",
        [source["source"] for source in summary["sources"]],
        [source["interview_rate"] for source in summary["sources"]],
        OUTPUT_DIR / "source_breakdown.svg",
        "%",
    )

    save_bar_chart(
        "Applications by Week",
        [week.isoformat() for week in summary["weekly_summary"]],
        list(summary["weekly_summary"].values()),
        OUTPUT_DIR / "applications_by_week.svg",
    )

    save_report(summary)
    print("Analysis complete. Check the outputs folder.")


if __name__ == "__main__":
    main()
