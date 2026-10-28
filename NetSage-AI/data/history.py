import csv
import os
from datetime import datetime


RESULTS_FILE = "data/results.csv"


def save_review(
    case_id,
    symptom,
    ai_diagnosis,
    rule_findings,
    comparison,
    human_review,
    review_reason="",
    evaluation=None
):

    os.makedirs("data", exist_ok=True)

    rule_text = "; ".join(
        finding.get("issue", "")
        for finding in rule_findings
    )

    if evaluation is None:
        evaluation = {}

    evaluation_result = evaluation.get(
        "result",
        ""
    )

    evaluation_category = evaluation.get(
        "category",
        ""
    )

    file_exists = os.path.exists(
        RESULTS_FILE
    )

    file_is_empty = (
        not file_exists
        or os.path.getsize(RESULTS_FILE) == 0
    )

    with open(
        RESULTS_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if file_is_empty:

            writer.writerow([
                "timestamp",
                "case_id",
                "symptom",
                "ai_root_cause",
                "ai_confidence",
                "rule_findings",
                "comparison",
                "ai_evaluation",
                "evaluation_category",
                "human_review",
                "review_reason"
            ])

        writer.writerow([
            datetime.now().isoformat(
                timespec="seconds"
            ),
            case_id,
            symptom,
            ai_diagnosis.get(
                "root_cause",
                ""
            ),
            ai_diagnosis.get(
                "confidence",
                0
            ),
            rule_text,
            comparison.get(
                "status",
                ""
            ),
            evaluation_result,
            evaluation_category,
            human_review,
            review_reason
        ])
