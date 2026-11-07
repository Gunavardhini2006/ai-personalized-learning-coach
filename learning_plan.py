
import json
import re
from ai_service import generate_ai_response


def generate_learning_plan(subject, goal, level, days, daily_minutes):

    # Validate student inputs
    if not subject or not goal:
        raise ValueError("Subject and learning goal are required.")

    if days <= 0 or daily_minutes <= 0:
        raise ValueError("Duration and study time must be positive.")

    # Create prompt for Gemini
    prompt = f"""
    You are an expert AI learning coach.

    Create a personalized learning plan using these details:

    Subject: {subject}
    Learning Goal: {goal}
    Current Level: {level}
    Total Duration: {days} days
    Daily Study Time: {daily_minutes} minutes

    Requirements:
    1. Create exactly {days} days of learning.
    2. Follow the student's current knowledge level.
    3. Divide topics logically from basic to advanced.
    4. Include a clear learning objective for each day.
    5. Include practical learning activities.
    6. Keep daily study time within {daily_minutes} minutes.
    7. Include estimated time for each day's activities.

    Return ONLY valid JSON in this format:

    {{
        "subject": "{subject}",
        "goal": "{goal}",
        "level": "{level}",
        "total_days": {days},
        "daily_minutes": {daily_minutes},
        "plan": [
            {{
                "day": 1,
                "topic": "Topic name",
                "objective": "Learning objective",
                "duration_minutes": {daily_minutes},
                "activities": [
                    "Read the topic",
                    "Practice examples"
                ]
            }}
        ]
    }}
    """

    # Get response from Gemini
    response = generate_ai_response(prompt)

    if not response:
        raise RuntimeError("Unable to generate learning plan.")

    # Remove Markdown code fences if Gemini includes them
    response = response.strip()
    response = re.sub(r"^```(?:json)?\s*", "", response)
    response = re.sub(r"\s*```$", "", response)

    # Convert JSON response into Python dictionary
    try:
        plan_data = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError("Gemini returned invalid JSON.") from e

    # Validate the generated plan
    required_fields = [
        "subject", "goal", "level",
        "total_days", "daily_minutes", "plan"
    ]

    for field in required_fields:
        if field not in plan_data:
            raise ValueError(f"Missing field: {field}")

    if not isinstance(plan_data["plan"], list):
        raise ValueError("Plan must be a list.")

    if len(plan_data["plan"]) != days:
        raise ValueError("Generated plan has an incorrect number of days.")

    for index, day in enumerate(plan_data["plan"], start=1):

        day_fields = [
            "day", "topic", "objective",
            "duration_minutes", "activities"
        ]

        for field in day_fields:
            if field not in day:
                raise ValueError(f"Missing {field} in Day {index}.")

        if day["day"] != index:
            raise ValueError("Day numbers are not in correct order.")

        if not isinstance(day["topic"], str) or not day["topic"].strip():
            raise ValueError(f"Invalid topic in Day {index}.")

        if not isinstance(day["objective"], str) or not day["objective"].strip():
            raise ValueError(f"Invalid objective in Day {index}.")

        duration = day["duration_minutes"]

        if not isinstance(duration, int) or isinstance(duration, bool):
            raise ValueError(f"Invalid duration in Day {index}.")

        if duration <= 0 or duration > daily_minutes:
            raise ValueError(f"Invalid study time in Day {index}.")

        if not isinstance(day["activities"], list) or not day["activities"]:
            raise ValueError(f"Invalid activities in Day {index}.")

    return plan_data
