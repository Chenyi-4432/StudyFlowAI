import streamlit as st
from datetime import date
import pandas as pd

st.set_page_config(
    page_title="StudyFlow AI",
    page_icon="📚",
    layout="wide"
)

if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.title("📚 StudyFlow AI")
st.subheader("AI-powered course task manager for international students")

st.markdown("""
StudyFlow AI helps students manage academic deadlines, break down complex assignments,
and decide what to do first.
""")

# -----------------------------
# Sidebar: Add Task
# -----------------------------
st.sidebar.header("➕ Add New Task")

task_name = st.sidebar.text_input("Task Name")
course = st.sidebar.text_input("Course")
deadline = st.sidebar.date_input("Deadline", min_value=date.today())
difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
estimated_hours = st.sidebar.number_input("Estimated Hours", min_value=1, max_value=50, value=3)

if st.sidebar.button("Add Task"):
    if task_name and course:
        task = {
            "Task": task_name,
            "Course": course,
            "Deadline": deadline,
            "Difficulty": difficulty,
            "Estimated Hours": estimated_hours,
            "Status": "Not Started"
        }
        st.session_state.tasks.append(task)
        st.sidebar.success("Task added successfully!")
    else:
        st.sidebar.warning("Please enter task name and course.")

# -----------------------------
# Main Dashboard
# -----------------------------
st.header("📌 Dashboard")

if len(st.session_state.tasks) == 0:
    st.info("No tasks yet. Add your first task from the sidebar.")
else:
    df = pd.DataFrame(st.session_state.tasks)
    df["Days Left"] = df["Deadline"].apply(lambda x: (x - date.today()).days)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Tasks", len(df))

    with col2:
        urgent_tasks = len(df[df["Days Left"] <= 3])
        st.metric("Urgent Tasks", urgent_tasks)

    with col3:
        total_hours = df["Estimated Hours"].sum()
        st.metric("Estimated Workload", f"{total_hours} hrs")

    st.subheader("📋 Task List")
    st.dataframe(df, use_container_width=True)

    # -----------------------------
    # Priority Recommendation
    # -----------------------------
    st.subheader("🔥 Today's Priority")

    difficulty_score = {
        "Easy": 1,
        "Medium": 2,
        "Hard": 3
    }

    df["Difficulty Score"] = df["Difficulty"].map(difficulty_score)

    df["Priority Score"] = (
        (10 - df["Days Left"].clip(lower=0)) * 2
        + df["Difficulty Score"] * 3
        + df["Estimated Hours"]
    )

    priority_task = df.sort_values(
        by="Priority Score",
        ascending=False
    ).iloc[0]

    st.success(
        f"Today, you should focus on: **{priority_task['Task']}** "
        f"for **{priority_task['Course']}**."
    )

    # -----------------------------
    # AI-like Task Breakdown
    # -----------------------------
    st.subheader("🤖 AI Task Breakdown")

    selected_task = st.selectbox("Choose a task to break down", df["Task"].tolist())

    if st.button("Generate Study Plan"):
        task_info = df[df["Task"] == selected_task].iloc[0]

        st.markdown(f"### Study Plan for: {selected_task}")

        if task_info["Difficulty"] == "Easy":
            steps = [
                "Review the task requirements.",
                "Complete the main work.",
                "Check and submit before the deadline."
            ]
        elif task_info["Difficulty"] == "Medium":
            steps = [
                "Read the instructions carefully.",
                "Break the task into smaller sections.",
                "Complete the first draft.",
                "Review your work.",
                "Submit before the deadline."
            ]
        else:
            steps = [
                "Understand the assignment requirements.",
                "Identify the most difficult parts.",
                "Break the task into research, analysis, writing, and revision.",
                "Work on the hardest part first.",
                "Prepare a complete draft.",
                "Review and improve the final version.",
                "Submit before the deadline."
            ]

        for i, step in enumerate(steps, start=1):
            st.write(f"{i}. {step}")