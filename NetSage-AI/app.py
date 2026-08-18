import json
import uuid
import os
import pandas as pd
import streamlit as st

from rules.checker import run_all_checks
from ai.diagnosis import diagnose_network
from evaluation.comparison import compare_diagnosis
from evaluation.evaluator import evaluate_ai
from data.history import save_review


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NetSage AI",
    page_icon="🌐",
    layout="wide"
)


# ============================================================
# CONSTANTS
# ============================================================

RESULTS_FILE = "data/results.csv"


CATEGORY_MAP = {
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


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "case_id": "LIVE-" + str(uuid.uuid4())[:8].upper(),
    "review_mode": None,
    "diagnosis": None,
    "findings": [],
    "comparison": None,
    "evaluation": None,
    "symptom": "",
    "command_output": "",
    "selected_case": None
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# LOAD CASES
# ============================================================

try:

    with open(
        "data/cases.json",
        "r",
        encoding="utf-8"
    ) as file:

        cases = json.load(file)

except Exception as error:

    st.error(
        f"Could not load data/cases.json: {error}"
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🌐 NetSage AI")

st.sidebar.caption(
    "AI-Assisted Network Troubleshooting"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🔍 Troubleshoot",
        "📊 Dashboard"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "Local AI + Rule Verification + "
    "Human Review"
)


# ============================================================
# ============================================================
# TROUBLESHOOTING PAGE
# ============================================================
# ============================================================

if page == "🔍 Troubleshoot":

    st.title("🌐 NetSage AI")

    st.subheader(
        "AI-Assisted Network Troubleshooting"
    )

    st.write(
        "Diagnose Cisco-style networking problems using "
        "local AI, deterministic Python rules, and "
        "human-in-the-loop validation."
    )

    # --------------------------------------------------------
    # CASE SELECTION
    # --------------------------------------------------------

    st.divider()

    st.header("📂 Troubleshooting Case")

    case_options = [
        f"{case['case_id']} — {case['category']}"
        for case in cases
    ]

    selected_option = st.selectbox(
        "Select a case",
        case_options
    )

    selected_case_id = selected_option.split(" — ")[0]

    selected_case = next(
        case
        for case in cases
        if case["case_id"] == selected_case_id
    )

    st.session_state.selected_case = selected_case

    # --------------------------------------------------------
    # CASE DETAILS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            f"**Case ID:** {selected_case['case_id']}\n\n"
            f"**Category:** {selected_case['category']}"
        )

    with col2:

        st.info(
            "**Known Correct Answer:**\n\n"
            + selected_case.get(
                "known_correct_answer",
                "Not available"
            )
        )

    # --------------------------------------------------------
    # SYMPTOM
    # --------------------------------------------------------

    st.header("🖥️ Network Information")

    symptom = st.text_area(
        "Network Symptom",
        value=selected_case.get(
            "symptom",
            ""
        ),
        height=100
    )

    # --------------------------------------------------------
    # TOPOLOGY
    # --------------------------------------------------------

    st.write("### Topology Notes")

    st.info(
        selected_case.get(
            "topology_notes",
            "No topology notes available."
        )
    )

    # --------------------------------------------------------
    # COMMAND OUTPUT
    # --------------------------------------------------------

    command_output = st.text_area(
        "Cisco / Packet Tracer Command Output",
        value=selected_case.get(
            "show_commands_output",
            ""
        ),
        height=220
    )

    # --------------------------------------------------------
    # ANALYZE
    # --------------------------------------------------------

    if st.button(
        "🔍 Analyze Network",
        type="primary",
        use_container_width=True
    ):

        st.session_state.review_mode = None
        st.session_state.diagnosis = None
        st.session_state.findings = []
        st.session_state.comparison = None
        st.session_state.evaluation = None

        st.session_state.case_id = (
            selected_case["case_id"]
        )

        st.session_state.symptom = symptom

        st.session_state.command_output = command_output

        # ----------------------------------------------------
        # RULE CHECKER
        # ----------------------------------------------------

        with st.spinner(
            "🛡️ Running deterministic checks..."
        ):

            findings = run_all_checks(

                command_output,

                expected_vlan=selected_case.get(
                    "expected_vlan"
                ),

                actual_vlan=selected_case.get(
                    "actual_vlan"
                ),

                expected_network=selected_case.get(
                    "expected_network"
                ),

                dhcp_gateway=selected_case.get(
                    "dhcp_gateway"
                ),

                dhcp_network=selected_case.get(
                    "dhcp_network"
                ),

                expected_next_hop=selected_case.get(
                    "expected_next_hop"
                ),

                actual_next_hop=selected_case.get(
                    "actual_next_hop"
                ),

                expected_route=selected_case.get(
                    "expected_route"
                ),

                actual_route=selected_case.get(
                    "actual_route"
                ),

                expected_native_vlan=selected_case.get(
                    "expected_native_vlan"
                ),

                actual_native_vlan=selected_case.get(
                    "actual_native_vlan"
                ),

                expected_dns=selected_case.get(
                    "expected_dns"
                ),

                actual_dns=selected_case.get(
                    "actual_dns"
                ),

                expected_acl_interface=selected_case.get(
                    "expected_acl_interface"
                ),

                actual_acl_interface=selected_case.get(
                    "actual_acl_interface"
                ),

                expected_acl_direction=selected_case.get(
                    "expected_acl_direction"
                ),

                actual_acl_direction=selected_case.get(
                    "actual_acl_direction"
                ),

                expected_inside=selected_case.get(
                    "expected_inside"
                ),

                expected_outside=selected_case.get(
                    "expected_outside"
                ),

                actual_inside=selected_case.get(
                    "actual_inside"
                ),

                actual_outside=selected_case.get(
                    "actual_outside"
                ),

                nat_overload=selected_case.get(
                    "nat_overload"
                ),

                expected_ssid=selected_case.get(
                    "expected_ssid"
                ),

                actual_ssid=selected_case.get(
                    "actual_ssid"
                ),

                expected_security=selected_case.get(
                    "expected_security"
                ),

                actual_security=selected_case.get(
                    "actual_security"
                )
            )

        st.session_state.findings = findings

        # ----------------------------------------------------
        # AI
        # ----------------------------------------------------

        with st.spinner(
            "🤖 NetSage AI is analyzing..."
        ):

            try:

                diagnosis = diagnose_network(
                    symptom,
                    command_output
                )

            except Exception as error:

                st.error(
                    "AI diagnosis failed."
                )

                st.exception(error)

                st.stop()

        st.session_state.diagnosis = diagnosis

        # ----------------------------------------------------
        # COMPARISON
        # ----------------------------------------------------

        comparison = compare_diagnosis(
            diagnosis,
            findings
        )

        st.session_state.comparison = comparison

        # ----------------------------------------------------
        # EVALUATION
        # ----------------------------------------------------

        evaluation = evaluate_ai(
            diagnosis,
            selected_case.get(
                "known_correct_answer",
                ""
            )
        )

        st.session_state.evaluation = evaluation

        st.success(
            "Analysis completed successfully."
        )

    # ========================================================
    # RESULTS
    # ========================================================

    if st.session_state.diagnosis is not None:

        diagnosis = st.session_state.diagnosis
        findings = st.session_state.findings
        comparison = st.session_state.comparison
        evaluation = st.session_state.evaluation

        # ----------------------------------------------------
        # RULE VERIFICATION
        # ----------------------------------------------------

        st.divider()

        st.header("🛡️ Rule-Based Verification")

        if findings:

            for finding in findings:

                issue = finding.get(
                    "issue",
                    "Unknown issue"
                )

                severity = finding.get(
                    "severity",
                    "Medium"
                )

                if severity.upper() == "HIGH":

                    st.error(
                        f"🔴 {issue} | Severity: {severity}"
                    )

                elif severity.upper() == "MEDIUM":

                    st.warning(
                        f"🟡 {issue} | Severity: {severity}"
                    )

                else:

                    st.info(
                        f"🔵 {issue} | Severity: {severity}"
                    )

        else:

            st.success(
                "✅ No known configuration problem "
                "was detected."
            )

        # ----------------------------------------------------
        # AI DIAGNOSIS
        # ----------------------------------------------------

        st.divider()

        st.header("🤖 AI Diagnosis")

        root_cause = diagnosis.get(
            "root_cause",
            "No diagnosis available."
        )

        osi_layer = diagnosis.get(
            "osi_layer",
            "Unknown"
        )

        try:

            confidence = float(
                diagnosis.get(
                    "confidence",
                    0
                )
            )

        except:

            confidence = 0

        confidence = max(
            0,
            min(1, confidence)
        )

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "Likely Root Cause"
            )

            st.write(
                root_cause
            )

        with col2:

            st.subheader(
                "OSI Layer"
            )

            st.write(
                osi_layer
            )

        st.subheader(
            "AI Confidence"
        )

        st.progress(
            confidence
        )

        st.write(
            f"**{confidence * 100:.1f}% confidence**"
        )

        # ----------------------------------------------------
        # EVIDENCE
        # ----------------------------------------------------

        st.subheader(
            "Evidence"
        )

        evidence = diagnosis.get(
            "evidence",
            []
        )

        if evidence:

            for item in evidence:

                st.write(
                    f"• {item}"
                )

        else:

            st.write(
                "No evidence provided."
            )

        # ----------------------------------------------------
        # NEXT COMMAND
        # ----------------------------------------------------

        st.subheader(
            "Recommended Next Command"
        )

        st.code(
            diagnosis.get(
                "next_command",
                "No command suggested."
            )
        )

        # ----------------------------------------------------
        # FIX STEPS
        # ----------------------------------------------------

        st.subheader(
            "Suggested Fix Steps"
        )

        fix_steps = diagnosis.get(
            "fix_steps",
            []
        )

        if fix_steps:

            for index, step in enumerate(
                fix_steps,
                start=1
            ):

                st.write(
                    f"**{index}.** {step}"
                )

        else:

            st.write(
                "No fix steps provided."
            )

        # ----------------------------------------------------
        # AI VS RULE
        # ----------------------------------------------------

        st.divider()

        st.header(
            "⚖️ AI vs Rule Verification"
        )

        if comparison:

            status = comparison.get(
                "status",
                "UNKNOWN"
            )

            if status == "AGREEMENT":

                st.success(
                    "🟢 AI and deterministic rules agree."
                )

            elif status == "DISAGREEMENT":

                st.error(
                    "🔴 AI and deterministic rules disagree."
                )

            else:

                st.warning(
                    "🟡 No deterministic rule finding "
                    "was available."
                )

            matching = comparison.get(
                "matching_concepts",
                []
            )

            if matching:

                st.write(
                    "**Matching concepts:** "
                    + ", ".join(matching)
                )

        # ----------------------------------------------------
        # EVALUATION
        # ----------------------------------------------------

        st.divider()

        st.header(
            "📊 AI Accuracy Evaluation"
        )

        if evaluation:

            result = evaluation.get(
                "result",
                "UNKNOWN"
            )

            category = evaluation.get(
                "category",
                "UNKNOWN"
            )

            if result == "CORRECT":

                st.success(
                    f"✅ AI diagnosis matches the "
                    f"known correct issue "
                    f"({category.upper()})."
                )

            elif result == "WRONG":

                st.error(
                    "❌ AI diagnosis does not match "
                    "the known correct issue."
                )

            else:

                st.warning(
                    f"Evaluation result: {result}"
                )

            st.write(
                "**Known Correct Answer:** "
                + selected_case.get(
                    "known_correct_answer",
                    "Not available."
                )
            )

        # ----------------------------------------------------
        # HUMAN REVIEW
        # ----------------------------------------------------

        st.divider()

        st.header(
            "👤 Human Review"
        )

        st.write(
            "The AI does not make the final decision. "
            "A human reviewer validates the diagnosis."
        )

        col1, col2, col3 = st.columns(3)

        # ACCEPT
        with col1:

            if st.button(
                "✅ Accept",
                use_container_width=True
            ):

                save_review(
                    case_id=st.session_state.case_id,
                    symptom=st.session_state.symptom,
                    ai_diagnosis=st.session_state.diagnosis,
                    rule_findings=st.session_state.findings,
                    comparison=st.session_state.comparison,
                    human_review="ACCEPTED",
                    review_reason="",
                    evaluation=st.session_state.evaluation
                )

                st.success(
                    "Diagnosis accepted and saved."
                )

        # EDIT
        with col2:

            if st.button(
                "✏️ Edit",
                use_container_width=True
            ):

                st.session_state.review_mode = "EDIT"

        # REJECT
        with col3:

            if st.button(
                "❌ Reject",
                use_container_width=True
            ):

                st.session_state.review_mode = "REJECT"

        # ----------------------------------------------------
        # EDIT
        # ----------------------------------------------------

        if st.session_state.review_mode == "EDIT":

            st.subheader(
                "✏️ Correct the AI Diagnosis"
            )

            edited_diagnosis = st.text_area(
                "Correct diagnosis",
                value=diagnosis.get(
                    "root_cause",
                    ""
                ),
                height=100
            )

            review_reason = st.text_area(
                "Why was the AI diagnosis edited?",
                height=100
            )

            if st.button(
                "💾 Save Edited Diagnosis"
            ):

                if not edited_diagnosis.strip():

                    st.error(
                        "Enter the corrected diagnosis."
                    )

                elif not review_reason.strip():

                    st.error(
                        "Explain why the diagnosis was edited."
                    )

                else:

                    edited_result = diagnosis.copy()

                    edited_result["root_cause"] = (
                        edited_diagnosis.strip()
                    )

                    save_review(
                        case_id=st.session_state.case_id,
                        symptom=st.session_state.symptom,
                        ai_diagnosis=edited_result,
                        rule_findings=st.session_state.findings,
                        comparison=st.session_state.comparison,
                        human_review="EDITED",
                        review_reason=review_reason.strip(),
                        evaluation=st.session_state.evaluation
                    )

                    st.success(
                        "Edited diagnosis saved."
                    )

                    st.session_state.review_mode = None

        # ----------------------------------------------------
        # REJECT
        # ----------------------------------------------------

        if st.session_state.review_mode == "REJECT":

            st.subheader(
                "❌ Reject AI Diagnosis"
            )

            rejection_reason = st.text_area(
                "Why is the AI diagnosis incorrect?",
                height=100
            )

            if st.button(
                "🚫 Confirm Rejection"
            ):

                if not rejection_reason.strip():

                    st.error(
                        "Provide a rejection reason."
                    )

                else:

                    save_review(
                        case_id=st.session_state.case_id,
                        symptom=st.session_state.symptom,
                        ai_diagnosis=st.session_state.diagnosis,
                        rule_findings=st.session_state.findings,
                        comparison=st.session_state.comparison,
                        human_review="REJECTED",
                        review_reason=rejection_reason.strip(),
                        evaluation=st.session_state.evaluation
                    )

                    st.error(
                        "Diagnosis rejected and saved."
                    )

                    st.session_state.review_mode = None


# ============================================================
# ============================================================
# DASHBOARD PAGE
# ============================================================
# ============================================================

elif page == "📊 Dashboard":

    st.title("📊 NetSage AI Dashboard")

    st.subheader(
        "Network Troubleshooting Analytics"
    )

    st.write(
        "Monitor AI performance, rule verification, "
        "human review, and troubleshooting categories."
    )

    # --------------------------------------------------------
    # LOAD RESULTS
    # --------------------------------------------------------

    if not os.path.exists(
        RESULTS_FILE
    ):

        st.info(
            "No review history exists yet."
        )

        st.write(
            "Go to **🔍 Troubleshoot**, analyze a case, "
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

    # --------------------------------------------------------
    # CLEAN COLUMNS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    df["category"] = (
        df["case_id"]
        .map(CATEGORY_MAP)
        .fillna("OTHER")
    )

    # --------------------------------------------------------
    # SIDEBAR FILTERS
    # --------------------------------------------------------

    st.sidebar.divider()

    st.sidebar.header(
        "🔎 Dashboard Filters"
    )

    categories = sorted(
        df["category"]
        .unique()
    )

    selected_categories = st.sidebar.multiselect(
        "Issue Category",
        categories,
        default=categories
    )

    review_options = sorted(
        df["human_review"]
        .unique()
    )

    selected_reviews = st.sidebar.multiselect(
        "Human Review",
        review_options,
        default=review_options
    )

    if "ai_evaluation" in df.columns:

        ai_options = sorted(
            df["ai_evaluation"]
            .unique()
        )

        selected_ai = st.sidebar.multiselect(
            "AI Evaluation",
            ai_options,
            default=ai_options
        )

    else:

        selected_ai = []

    # --------------------------------------------------------
    # APPLY FILTERS
    # --------------------------------------------------------

    filtered_df = df[
        df["category"].isin(
            selected_categories
        )
        &
        df["human_review"].isin(
            selected_reviews
        )
    ]

    if (
        "ai_evaluation" in filtered_df.columns
        and selected_ai
    ):

        filtered_df = filtered_df[
            filtered_df["ai_evaluation"].isin(
                selected_ai
            )
        ]

    # --------------------------------------------------------
    # OVERVIEW
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # AI ACCURACY
    # --------------------------------------------------------

    st.divider()

    st.header(
        "🤖 AI Performance"
    )

    if "ai_evaluation" in filtered_df.columns:

        evaluated = filtered_df[
            filtered_df["ai_evaluation"].isin(
                ["CORRECT", "WRONG"]
            )
        ]

    else:

        evaluated = pd.DataFrame()

    if not evaluated.empty:

        ai_correct = (
            evaluated["ai_evaluation"]
            .eq("CORRECT")
            .sum()
        )

        ai_wrong = (
            evaluated["ai_evaluation"]
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
            "No evaluated cases available yet."
        )

    # --------------------------------------------------------
    # HUMAN ACCEPTANCE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CATEGORY CHART
    # --------------------------------------------------------

    st.divider()

    st.header(
        "🌐 Issue Categories"
    )

    category_counts = (
        filtered_df["category"]
        .value_counts()
    )

    if not category_counts.empty:

        st.bar_chart(
            category_counts
        )

    # --------------------------------------------------------
    # REVIEW DISTRIBUTION
    # --------------------------------------------------------

    st.divider()

    st.header(
        "👤 Human Review Distribution"
    )

    review_counts = (
        filtered_df["human_review"]
        .value_counts()
    )

    if not review_counts.empty:

        st.bar_chart(
            review_counts
        )

    # --------------------------------------------------------
    # AI EVALUATION
    # --------------------------------------------------------

    if "ai_evaluation" in filtered_df.columns:

        st.divider()

        st.header(
            "🧠 AI Evaluation Distribution"
        )

        evaluation_counts = (
            filtered_df[
                filtered_df["ai_evaluation"].isin(
                    ["CORRECT", "WRONG"]
                )
            ]["ai_evaluation"]
            .value_counts()
        )

        if not evaluation_counts.empty:

            st.bar_chart(
                evaluation_counts
            )

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CASE PERFORMANCE
    # --------------------------------------------------------

    st.divider()

    st.header(
        "📋 Case Performance"
    )

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

    # --------------------------------------------------------
    # DETAILED HISTORY
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # EXPORT
    # --------------------------------------------------------

    st.divider()

    st.header(
        "💾 Export"
    )

    csv_data = filtered_df.to_csv(
        index=False
    )

    st.download_button(
        label="⬇️ Download Review History",
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