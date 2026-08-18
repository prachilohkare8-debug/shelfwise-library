import os
import pandas as pd
import streamlit as st


RESULTS_FILE = "data/results.csv"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NetSage AI Dashboard",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("📊 NetSage AI Dashboard")

st.subheader(
    "Network Troubleshooting Analytics"
)

st.write(
    "Monitor AI diagnosis accuracy, deterministic "
    "verification, and human review outcomes."
)


# ============================================================
# LOAD DATA
# ============================================================

if not os.path.exists(RESULTS_FILE):

    st.warning(
        "No review history found."
    )

    st.info(
        "Run at least one case in NetSage AI "
        "and submit a human review."
    )

    st.stop()


try:

    df = pd.read_csv(
        RESULTS_FILE
    )

except Exception as error:

    st.error(
        f"Could not read results.csv: {error}"
    )

    st.stop()


if df.empty:

    st.info(
        "No reviewed cases available yet."
    )

    st.stop()


# ============================================================
# CLEAN DATA
# ============================================================

df.columns = (
    df.columns
    .str.strip()
)

for column in [
    "human_review",
    "ai_evaluation",
    "comparison"
]:

    if column in df.columns:

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header(
    "🔎 Filters"
)


# ------------------------------------------------------------
# CATEGORY MAP
# ------------------------------------------------------------

category_map = {

    "C001": "VLAN",
    "C002": "DHCP",
    "C003": "ROUTING",
    "C004": "INTERFACE",
    "C005": "GATEWAY",

    "C006": "VLAN",
    "C007": "VLAN",
    "C008": "VLAN",
    "C009": "VLAN",

    "C010": "DHCP",
    "C011": "DHCP",
    "C012": "DHCP",
    "C013": "DHCP",

    "C014": "ROUTING",
    "C015": "ROUTING",
    "C016": "ROUTING",
    "C017": "ROUTING",

    "C018": "DNS",
    "C019": "DNS",
    "C020": "DNS",
    "C021": "DNS",

    "C022": "ACL",
    "C023": "ACL",
    "C024": "ACL",
    "C025": "ACL",

    "C026": "NAT",
    "C027": "NAT",
    "C028": "NAT",

    "C029": "WIRELESS",
    "C030": "WIRELESS",
    "C031": "WIRELESS",
    "C032": "WIRELESS"
}


if "case_id" in df.columns:

    df["category"] = (
        df["case_id"]
        .map(category_map)
        .fillna("OTHER")
    )


# ------------------------------------------------------------
# CATEGORY FILTER
# ------------------------------------------------------------

categories = sorted(
    df["category"]
    .dropna()
    .unique()
)

selected_categories = st.sidebar.multiselect(
    "Category",
    categories,
    default=categories
)


# ------------------------------------------------------------
# REVIEW FILTER
# ------------------------------------------------------------

review_options = sorted(
    df["human_review"]
    .dropna()
    .unique()
)

selected_reviews = st.sidebar.multiselect(
    "Human Review",
    review_options,
    default=review_options
)


# ------------------------------------------------------------
# AI RESULT FILTER
# ------------------------------------------------------------

if "ai_evaluation" in df.columns:

    ai_options = sorted(
        df["ai_evaluation"]
        .dropna()
        .unique()
    )

else:

    ai_options = []


selected_ai_results = st.sidebar.multiselect(
    "AI Evaluation",
    ai_options,
    default=ai_options
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    df["category"].isin(
        selected_categories
    )
    &
    df["human_review"].isin(
        selected_reviews
    )
]


if "ai_evaluation" in filtered_df.columns:

    if selected_ai_results:

        filtered_df = filtered_df[
            filtered_df["ai_evaluation"].isin(
                selected_ai_results
            )
        ]


# ============================================================
# OVERVIEW
# ============================================================

st.divider()

st.header(
    "📈 Overview"
)


total_reviews = len(
    filtered_df
)

accepted = (
    filtered_df["human_review"]
    .eq("ACCEPTED")
    .sum()
)

edited = (
    filtered_df["human_review"]
    .eq("EDITED")
    .sum()
)

rejected = (
    filtered_df["human_review"]
    .eq("REJECTED")
    .sum()
)


# ============================================================
# TOP METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Reviews",
        total_reviews
    )


with col2:

    st.metric(
        "Accepted",
        accepted
    )


with col3:

    st.metric(
        "Edited",
        edited
    )


with col4:

    st.metric(
        "Rejected",
        rejected
    )


# ============================================================
# AI ACCURACY
# ============================================================

st.divider()

st.header(
    "🤖 AI Performance"
)


if "ai_evaluation" in filtered_df.columns:

    evaluated_df = filtered_df[
        filtered_df["ai_evaluation"].isin(
            ["CORRECT", "WRONG"]
        )
    ]

else:

    evaluated_df = pd.DataFrame()


if not evaluated_df.empty:

    ai_correct = (
        evaluated_df["ai_evaluation"]
        .eq("CORRECT")
        .sum()
    )

    ai_wrong = (
        evaluated_df["ai_evaluation"]
        .eq("WRONG")
        .sum()
    )

    ai_total = (
        ai_correct + ai_wrong
    )

    ai_accuracy = (
        ai_correct / ai_total
    ) * 100


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "AI Accuracy",
            f"{ai_accuracy:.1f}%"
        )


    with col2:

        st.metric(
            "AI Correct",
            ai_correct
        )


    with col3:

        st.metric(
            "AI Wrong",
            ai_wrong
        )


else:

    st.info(
        "AI accuracy will appear after reviewed "
        "cases containing evaluation results are saved."
    )


# ============================================================
# HUMAN ACCEPTANCE RATE
# ============================================================

if total_reviews > 0:

    acceptance_rate = (
        accepted / total_reviews
    ) * 100

else:

    acceptance_rate = 0


st.metric(
    "Human Acceptance Rate",
    f"{acceptance_rate:.1f}%"
)


# ============================================================
# CATEGORY DISTRIBUTION
# ============================================================

st.divider()

st.header(
    "🌐 Issue Categories"
)


if not filtered_df.empty:

    category_counts = (
        filtered_df["category"]
        .value_counts()
    )

    st.bar_chart(
        category_counts
    )


# ============================================================
# HUMAN REVIEW DISTRIBUTION
# ============================================================

st.divider()

st.header(
    "👤 Human Review Distribution"
)


if not filtered_df.empty:

    review_counts = (
        filtered_df["human_review"]
        .value_counts()
    )

    st.bar_chart(
        review_counts
    )


# ============================================================
# AI EVALUATION DISTRIBUTION
# ============================================================

if "ai_evaluation" in filtered_df.columns:

    st.divider()

    st.header(
        "🧠 AI Evaluation Distribution"
    )

    ai_counts = (
        filtered_df[
            filtered_df["ai_evaluation"]
            .isin(["CORRECT", "WRONG"])
        ]["ai_evaluation"]
        .value_counts()
    )

    if not ai_counts.empty:

        st.bar_chart(
            ai_counts
        )


# ============================================================
# AI CONFIDENCE
# ============================================================

st.divider()

st.header(
    "🎯 AI Confidence"
)


if "ai_confidence" in filtered_df.columns:

    confidence = pd.to_numeric(
        filtered_df["ai_confidence"],
        errors="coerce"
    ).dropna()

    if not confidence.empty:

        average_confidence = (
            confidence.mean()
        ) * 100

        st.metric(
            "Average AI Confidence",
            f"{average_confidence:.1f}%"
        )

        st.line_chart(
            confidence.reset_index(
                drop=True
            )
        )

    else:

        st.info(
            "No valid confidence values available."
        )


# ============================================================
# CASE PERFORMANCE
# ============================================================

st.divider()

st.header(
    "📋 Case Performance"
)


if not filtered_df.empty:

    case_columns = [
        column
        for column in [
            "case_id",
            "category",
            "ai_root_cause",
            "ai_confidence",
            "ai_evaluation",
            "comparison",
            "human_review"
        ]
        if column in filtered_df.columns
    ]

    st.dataframe(
        filtered_df[
            case_columns
        ],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# REVIEW HISTORY
# ============================================================

st.divider()

st.header(
    "📝 Detailed Review History"
)


history_columns = [
    column
    for column in [
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
    ]
    if column in filtered_df.columns
]


st.dataframe(
    filtered_df[
        history_columns
    ],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# EXPORT
# ============================================================

st.divider()

st.header(
    "💾 Export"
)


csv_data = filtered_df.to_csv(
    index=False
)

st.download_button(
    label="⬇️ Download Filtered Results",
    data=csv_data,
    file_name="netsage_review_history.csv",
    mime="text/csv",
    use_container_width=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "NetSage AI • Local LLM + Deterministic Rules + "
    "Known-Answer Evaluation + Human-in-the-Loop Review"
)
