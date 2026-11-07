
from database import (
    save_quiz_attempt,
    update_topic_progress,
    get_quiz_history,
    get_topic_progress
)


# 1. Record quiz performance
def record_quiz_result(
    learner_id,
    topic,
    score,
    total_questions,
    answers,
    feedback
):

    if total_questions <= 0:
        raise ValueError("Total questions must be positive.")

    if score < 0 or score > total_questions:
        raise ValueError("Invalid quiz score.")

    # Save quiz attempt
    save_quiz_attempt(
        learner_id,
        topic,
        score,
        total_questions,
        answers,
        feedback
    )

    # Update topic progress
    update_topic_progress(
        learner_id,
        topic,
        score,
        total_questions
    )


# 2. Calculate overall performance
def calculate_average(history):

    if not history:
        return 0

    total_percentage = sum(
        (item[1] / item[2]) * 100
        for item in history
        if item[2] > 0
    )

    valid_attempts = sum(1 for item in history if item[2] > 0)

    if valid_attempts == 0:
        return 0

    return round(total_percentage / valid_attempts, 2)


# 3. Generate learning recommendations
def generate_recommendations(progress):

    recommendations = []

    for topic, status, percentage in progress:

        if status == "Needs Revision":
            recommendations.append(
                f"Revise {topic}. Your last score was {percentage}%."
            )

        elif status == "Completed":
            recommendations.append(
                f"Good progress in {topic}. Move to the next topic."
            )

    if not recommendations:
        recommendations.append(
            "Start taking quizzes to receive personalized recommendations."
        )

    return recommendations


# 4. Get complete student progress
def get_learning_dashboard(learner_id):

    history = get_quiz_history(learner_id)

    progress = get_topic_progress(learner_id)

    average = calculate_average(history)

    completed_topics = [
        item[0] for item in progress
        if item[1] == "Completed"
    ]

    weak_topics = [
        item[0] for item in progress
        if item[1] == "Needs Revision"
    ]

    recommendations = generate_recommendations(progress)

    return {
        "total_quizzes": len(history),
        "average_score": average,
        "completed_topics": completed_topics,
        "weak_topics": weak_topics,
        "recommendations": recommendations
    }
