def compare_diagnosis(ai_diagnosis, rule_findings):

    ai_root_cause = ai_diagnosis.get(
        "root_cause",
        ""
    ).lower()

    if not rule_findings:

        return {
            "status": "NO_RULE_FINDING",
            "message": (
                "The rule checker did not detect "
                "a known configuration problem."
            )
        }

    rule_issues = [
        finding["issue"].lower()
        for finding in rule_findings
    ]

    # Check whether important words from the rule
    # findings appear in the AI diagnosis.

    matches = []

    keywords = [
        "gateway",
        "vlan",
        "route",
        "routing",
        "interface",
        "dhcp",
        "dns",
        "acl",
        "nat",
        "subnet"
    ]

    for keyword in keywords:

        ai_mentions = keyword in ai_root_cause

        rule_mentions = any(
            keyword in issue
            for issue in rule_issues
        )

        if ai_mentions and rule_mentions:
            matches.append(keyword)

    if matches:

        return {
            "status": "AGREEMENT",
            "message": (
                "AI diagnosis is consistent with "
                "the rule-based findings."
            ),
            "matching_concepts": matches
        }

    return {
        "status": "DISAGREEMENT",
        "message": (
            "AI diagnosis does not clearly match "
            "the rule-based findings."
        ),
        "matching_concepts": []
    }