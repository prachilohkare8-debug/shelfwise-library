import json

from ollama import chat


MODEL = "llama3.2:3b"


SYSTEM_PROMPT = """
You are NetSage AI, an AI-assisted Cisco networking
troubleshooting assistant.

Analyze the user's networking symptom and Cisco command output.

Your job is to identify the most likely root cause.

IMPORTANT RULES:

1. Use only the evidence provided.
2. Do not invent command output.
3. Do not assume an IP address is invalid just because it is
   different from the network address.
4. Carefully distinguish:
   - network address
   - host address
   - subnet mask
   - default gateway
5. If the evidence is insufficient, say so.
6. Recommend a useful Cisco command when more evidence is needed.
7. Return ONLY valid JSON.

Return exactly this structure:

{
    "root_cause": "string",
    "osi_layer": "string",
    "confidence": 0.0,
    "evidence": [
        "string"
    ],
    "next_command": "string",
    "fix_steps": [
        "string"
    ]
}
"""


def diagnose_network(symptom, command_output):

    user_prompt = f"""
NETWORK SYMPTOM:
{symptom}

CISCO COMMAND OUTPUT:
{command_output}

Analyze the problem carefully.

Return only JSON.
"""

    try:

        response = chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            options={
                "temperature": 0
            }
        )

        text = response.message.content.strip()

        # Remove markdown code fences if the model adds them
        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        return json.loads(text)

    except Exception as error:

        return {
            "root_cause": "Local AI diagnosis failed.",
            "osi_layer": "Unknown",
            "confidence": 0.0,
            "evidence": [
                f"Error: {type(error).__name__}"
            ],
            "next_command": "Review the rule-based findings.",
            "fix_steps": [
                "Check that Ollama is running.",
                "Check that the selected model is installed."
            ]
        }