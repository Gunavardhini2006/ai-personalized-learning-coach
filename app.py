
import streamlit as st

from database import (
    initialize_db,
    save_learner,
    save_learning_plan
)

from learning_plan import generate_learning_plan

from quiz_manager import (
    generate_quiz,
    evaluate_quiz
)

from progress_tracker import (
    record_quiz_result,
    get_learning_dashboard
)


# ---------------------------------
# 1. APPLICATION CONFIGURATION
# ---------------------------------

st.set_page_config(
    page_title="AI Personalized Learning Coach",
    page_icon="🎓",
    layout="wide"
)

# Initialize database
initialize_db()

# Initialize session state
if "learner_id" not in st.session_state:
    st.session_state.learner_id = None

if "learning_plan" not in st.session_state:
    st.session_state.learning_plan = None

if "level" not in st.session_state:
    st.session_state.level = "Beginner"

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False


# ---------------------------------
# 2. APPLICATION HEADER
# ---------------------------------

st.title("🎓 AI Personalized Learning Coach")

st.write(
    "Your personal AI-powered learning assistant. "
    "Create study plans, practice quizzes and track your progress."
)

st.divider()


# ---------------------------------
# 3. SIDEBAR NAVIGATION
# ---------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a section",
    [
        "Student Profile",
        "Study Planner",
        "Quiz Center",
        "Progress Dashboard"
    ]
)


# ---------------------------------
# 4. STUDENT PROFILE
# ---------------------------------

if page == "Student Profile":

    st.header("👤 Student Profile")

    st.write("Enter your learning preferences below.")

    with st.form("student_form"):

        subject = st.text_input(
            "What subject do you want to learn?",
            placeholder="Example: Python"
        )

        goal = st.text_area(
            "What is your learning goal?",
            placeholder="Example: Learn Python programming from basics"
        )

        level = st.selectbox(
            "Your current knowledge level",
            ["Beginner", "Intermediate", "Advanced"]
        )

        days = st.number_input(
            "How many days do you want to study?",
            min_value=1,
            max_value=90,
            value=7
        )

        minutes = st.number_input(
            "Daily study time (minutes)",
            min_value=15,
            max_value=480,
            value=45,
            step=15
        )

        submitted = st.form_submit_button(
            "Generate My Study Plan"
        )

    if submitted:

        if not subject.strip() or not goal.strip():

            st.error("Please enter both subject and learning goal.")

        else:

            with st.spinner("Creating your personalized study plan..."):

                try:

                    # Generate AI study plan
                    plan = generate_learning_plan(
                        subject,
                        goal,
                        level,
                        int(days),
                        int(minutes)
                    )

                    # Save learner
                    learner_id = save_learner(
                        subject,
                        goal,
                        level,
                        int(days),
                        int(minutes)
                    )

                    # Save study plan
                    save_learning_plan(learner_id, plan)

                    # Store data in session
                    st.session_state.learner_id = learner_id
                    st.session_state.learning_plan = plan
                    st.session_state.level = level
                    st.session_state.quiz_data = None
                    st.session_state.quiz_result = None
                    st.session_state.quiz_submitted = False

                    st.success("Your personalized study plan is ready!")

                except Exception as e:

                    st.error(f"Unable to create study plan: {e}")


# ---------------------------------
# 5. STUDY PLANNER
# ---------------------------------

elif page == "Study Planner":

    st.header("📚 Your Personalized Study Plan")

    plan = st.session_state.learning_plan

    if plan:

        st.subheader(plan["subject"])

        st.write("**Learning Goal:**", plan["goal"])
        st.write("**Current Level:**", plan["level"])
        st.write("**Total Days:**", plan["total_days"])

        st.divider()

        for day in plan["plan"]:

            with st.expander(
                f"Day {day['day']}: {day['topic']}",
                expanded=False
            ):

                st.write("**Learning Objective:**")
                st.write(day["objective"])

                st.write(
                    f"**Study Duration:** {day['duration_minutes']} minutes"
                )

                st.write("**Activities:**")

                for activity in day["activities"]:
                    st.write(f"- {activity}")

    else:

        st.info(
            "No study plan available. "
            "Go to Student Profile and generate your study plan first."
        )


# ---------------------------------
# 6. QUIZ CENTER
# ---------------------------------

elif page == "Quiz Center":

    st.header("🧠 AI Quiz Center")

    plan = st.session_state.learning_plan

    if not plan:

        st.info("Generate a study plan before starting a quiz.")

    else:

        topics = [
            day["topic"] for day in plan["plan"]
        ]

        with st.form("quiz_generation_form"):

            selected_topic = st.selectbox(
                "Select a topic",
                topics
            )

            num_questions = st.selectbox(
                "Number of questions",
                [5, 10, 15]
            )

            generate_button = st.form_submit_button(
                "Generate Quiz"
            )

        if generate_button:

            with st.spinner("Generating your quiz using Gemini..."):

                try:

                    quiz = generate_quiz(
                        selected_topic,
                        st.session_state.level,
                        num_questions
                    )

                    st.session_state.quiz_data = quiz
                    st.session_state.quiz_topic = selected_topic
                    st.session_state.quiz_result = None
                    st.session_state.quiz_submitted = False

                    st.success("Quiz generated successfully!")

                except Exception as e:

                    st.error(f"Unable to generate quiz: {e}")

        # Display generated quiz
        quiz = st.session_state.quiz_data

        if quiz:

            st.divider()

            st.subheader(
                f"Quiz: {st.session_state.quiz_topic}"
            )

            if not st.session_state.quiz_submitted:

                with st.form("quiz_answer_form"):

                    student_answers = {}

                    for index, question in enumerate(quiz["questions"]):

                        st.markdown(
                            f"**Question {index + 1}: "
                            f"{question['question']}**"
                        )

                        answer = st.radio(
                            "Choose your answer:",
                            options=["A", "B", "C", "D"],
                            format_func=lambda option, q=question:
                                f"{option}. {q['options'][option]}",
                            index=None,
                            key=f"answer_{index}"
                        )

                        student_answers[index] = answer

                        st.divider()

                    submit_quiz = st.form_submit_button(
                        "Submit My Answers"
                    )

                if submit_quiz:

                    # Evaluate quiz
                    result = evaluate_quiz(
                        quiz["questions"],
                        student_answers
                    )

                    st.session_state.quiz_result = result

                    st.session_state.quiz_submitted = True

                    # Save quiz and update progress
                    try:

                        if st.session_state.learner_id is None:
                            st.error("Please create a student profile first.")

                        else:

                            record_quiz_result(
                                st.session_state.learner_id,
                                st.session_state.quiz_topic,
                                result["score"],
                                result["total"],
                                student_answers,
                                result["feedback"]
                            )

                    except Exception as e:

                        st.error(f"Unable to save quiz result: {e}")

            # Display quiz results
            if st.session_state.quiz_submitted:

                result = st.session_state.quiz_result

                st.subheader("📊 Your Quiz Results")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Score",
                    f"{result['score']}/{result['total']}"
                )

                col2.metric(
                    "Percentage",
                    f"{result['percentage']}%"
                )

                col3.metric(
                    "Performance",
                    "Excellent" if result["percentage"] >= 80
                    else "Good" if result["percentage"] >= 60
                    else "Needs Practice"
                )

                st.info(result["feedback"])

                st.subheader("Answer Review")

                for index, item in enumerate(result["results"]):

                    st.write(
                        f"**Question {index + 1}: {item['question']}**"
                    )

                    st.write(
                        f"Your Answer: {item['student_answer'] or 'Not answered'}"
                    )

                    st.write(
                        f"Correct Answer: {item['correct_answer']}"
                    )

                    if item["is_correct"]:
                        st.success("Correct answer!")
                    else:
                        st.error("Incorrect answer.")

                    st.write(
                        f"Explanation: {item['explanation']}"
                    )

                    st.divider()

                if st.button("Generate Another Quiz"):

                    st.session_state.quiz_data = None
                    st.session_state.quiz_result = None
                    st.session_state.quiz_submitted = False

                    st.rerun()


# ---------------------------------
# 7. PROGRESS DASHBOARD
# ---------------------------------

elif page == "Progress Dashboard":

    st.header("📈 Learning Progress Dashboard")

    learner_id = st.session_state.learner_id

    if learner_id is None:

        st.info(
            "Please create a student profile and complete quizzes "
            "to view your learning progress."
        )

    else:

        dashboard = get_learning_dashboard(learner_id)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Quizzes",
            dashboard["total_quizzes"]
        )

        col2.metric(
            "Average Score",
            f"{dashboard['average_score']}%"
        )

        col3.metric(
            "Completed Topics",
            len(dashboard["completed_topics"])
        )

        st.divider()

        st.subheader("✅ Completed Topics")

        if dashboard["completed_topics"]:

            for topic in dashboard["completed_topics"]:
                st.success(topic)

        else:

            st.write("No topics completed yet.")

        st.subheader("📌 Topics Needing Revision")

        if dashboard["weak_topics"]:

            for topic in dashboard["weak_topics"]:
                st.warning(topic)

        else:

            st.write("No topics currently need revision.")

        st.divider()

        st.subheader("💡 Personalized Recommendations")

        for recommendation in dashboard["recommendations"]:
            st.info(recommendation)

        if dashboard["total_quizzes"] > 0:

            st.subheader("Overall Performance")

            st.progress(
                min(
                    dashboard["average_score"] / 100,
                    1.0
                )
            )

            st.write(
                f"Average quiz performance: "
                f"{dashboard['average_score']}%"
            )


# ---------------------------------
# 8. APPLICATION FOOTER
# ---------------------------------

st.divider()

st.caption(
    "AI Personalized Learning Coach | "
    "Powered by Python, Streamlit, SQLite and Google Gemini"
)
