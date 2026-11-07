
import json
import re
from ai_service import generate_ai_response


# 1. Generate AI quiz questions
def generate_quiz(topic, level="Beginner", num_questions=5):

    if not topic.strip():
        raise ValueError("Topic is required.")

    if not 1 <= num_questions <= 20:
        raise ValueError("Number of questions must be between 1 and 20.")

    prompt = f"""
    You are an expert educational quiz creator.

    Generate {num_questions} multiple-choice questions.

    Topic: {topic}
    Difficulty Level: {level}

    Requirements:
    1. Generate exactly {num_questions} questions.
    2. Each question must have four options.
    3. Use options A, B, C and D.
    4. Only one option must be correct.
    5. Provide a clear explanation of the answer.
    6. Questions must match the difficulty level.

    Return ONLY valid JSON in this format:

    {{
        "topic": "{topic}",
        "questions": [
            {{
                "question": "Question text",
                "options": {{
                    "A": "Option A",
                    "B": "Option B",
                    "C": "Option C",
                    "D": "Option D"
                }},
                "correct_answer": "A",
                "explanation": "Explanation of the correct answer"
            }}
        ]
    }}
    """

    response = generate_ai_response(prompt)

    if not response:
        raise RuntimeError("Unable to generate quiz.")

    # Remove Markdown code fences
    response = response.strip()
    response = re.sub(r"^```(?:json)?\s*", "", response)
    response = re.sub(r"\s*```$", "", response)

    # Parse JSON
    try:
        quiz_data = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError("Gemini returned invalid quiz JSON.") from e

    # Validate quiz structure
    if not isinstance(quiz_data, dict):
        raise ValueError("Invalid quiz format.")

    questions = quiz_data.get("questions")

    if not isinstance(questions, list):
        raise ValueError("Questions must be a list.")

    if len(questions) != num_questions:
        raise ValueError("Incorrect number of questions generated.")

    required_options = {"A", "B", "C", "D"}

    for index, question in enumerate(questions, start=1):

        if not isinstance(question, dict):
            raise ValueError(f"Invalid question {index}.")

        if not isinstance(question.get("question"), str) or not question["question"].strip():
            raise ValueError(f"Question {index} has invalid text.")

        options = question.get("options")

        if not isinstance(options, dict) or set(options.keys()) != required_options:
            raise ValueError(f"Question {index} must have four options.")

        if not all(
            isinstance(value, str) and value.strip()
            for value in options.values()
        ):
            raise ValueError(f"Question {index} has empty options.")

        correct = question.get("correct_answer")

        if correct not in required_options:
            raise ValueError(f"Question {index} has an invalid answer.")

        if not isinstance(question.get("explanation"), str) or not question["explanation"].strip():
            raise ValueError(f"Question {index} has no explanation.")

    quiz_data["topic"] = topic

    return quiz_data


# 2. Evaluate student answers
def evaluate_quiz(questions, student_answers):

    score = 0
    results = []

    for index, question in enumerate(questions):

        correct_answer = question["correct_answer"]

        student_answer = student_answers.get(index)

        is_correct = student_answer == correct_answer

        if is_correct:
            score += 1

        results.append({
            "question": question["question"],
            "student_answer": student_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question["explanation"]
        })

    total = len(questions)

    percentage = round((score / total) * 100, 2) if total else 0

    # Generate performance feedback
    if percentage >= 80:
        feedback = "Excellent! You have a strong understanding of this topic."
    elif percentage >= 60:
        feedback = "Good work! Revise a few concepts to improve further."
    else:
        feedback = "You need more practice. Review the topic and try again."

    return {
        "score": score,
        "total": total,
        "percentage": percentage,
        "feedback": feedback,
        "results": results
    }
