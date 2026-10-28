def normalize(text):
    return (
        text.lower()
        .strip()
        .replace("_", " ")
        .replace("-", " ")
    )


def evaluate_ai(
    ai_diagnosis,
    known_correct_answer
):

    ai_text = normalize(
        ai_diagnosis.get("root_cause", "")
    )

    correct_text = normalize(
        known_correct_answer
    )

    # Strong keyword matching for the current MVP
    issue_groups = {
        "vlan": [
            "vlan",
            "switchport"
        ],
        "dhcp": [
            "dhcp"
        ],
        "gateway": [
            "gateway"
        ],
        "routing": [
            "route",
            "routing"
        ],
        "interface": [
            "interface",
            "administratively down"
        ],
        "dns": [
            "dns",
            "domain name"
        ],
        "acl": [
            "acl",
            "access control"
        ],
        "nat": [
            "nat",
            "network address translation"
        ]
    }

    for category, keywords in issue_groups.items():

        ai_match = any(
            keyword in ai_text
            for keyword in keywords
        )

        correct_match = any(
            keyword in correct_text
            for keyword in keywords
        )

        if ai_match and correct_match:

            return {
                "result": "CORRECT",
                "category": category
            }

    return {
        "result": "WRONG",
        "category": "UNKNOWN"
    }