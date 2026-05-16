import streamlit as st
import pandas as pd
from datetime import date, timedelta
import re

st.set_page_config(
    page_title="StudyFlow AI",
    page_icon="📚",
    layout="wide"
)

# =============================
# Session State
# =============================
if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "courses" not in st.session_state:
    st.session_state.courses = []

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "White Original"

# =============================
# Theme System
# =============================
THEMES = {
    "White Original": {
        "bg": "#FFFFFF",
        "sidebar": "#F2F4F8",
        "card": "#F7F8FC",
        "text": "#262730",
        "subtext": "#4F566B",
        "primary": "#6C63FF",
        "border": "#E8EAF2"
    },
    "Night Dark": {
        "bg": "#121212",
        "sidebar": "#1E1E1E",
        "card": "#242424",
        "text": "#F5F5F5",
        "subtext": "#C9CDD6",
        "primary": "#9B8CFF",
        "border": "#3A3A3A"
    },
    "Eye Protection Green": {
        "bg": "#F3F8EF",
        "sidebar": "#E5F0DE",
        "card": "#FFFFFF",
        "text": "#243B2A",
        "subtext": "#526B55",
        "primary": "#4F8A5B",
        "border": "#CFE3C7"
    }
}


def apply_theme(theme_name):
    theme = THEMES[theme_name]

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {theme["bg"]};
            color: {theme["text"]};
        }}

        section[data-testid="stSidebar"] {{
            background-color: {theme["sidebar"]};
        }}

        h1, h2, h3, h4, h5, h6, p, label, span, div {{
            color: {theme["text"]};
        }}

        .main-title {{
            color: {theme["primary"]};
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 10px;
        }}

        .section-title {{
            color: {theme["primary"]};
            font-size: 28px;
            font-weight: 700;
            margin-top: 28px;
            margin-bottom: 12px;
        }}

        .subtitle {{
            color: {theme["subtext"]};
            font-size: 18px;
        }}

        div[data-testid="stMetric"] {{
            background-color: {theme["card"]};
            border: 1px solid {theme["border"]};
            padding: 16px;
            border-radius: 14px;
        }}

        .stButton button {{
            background-color: {theme["primary"]};
            color: white;
            border-radius: 10px;
            border: none;
            padding: 8px 16px;
            font-weight: 600;
        }}

        .stButton button:hover {{
            opacity: 0.85;
            color: white;
        }}

        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input,
        .stDateInput input,
        div[data-baseweb="select"] {{
            background-color: {theme["card"]};
            color: {theme["text"]};
            border-color: {theme["border"]};
        }}

        .stProgress > div > div > div > div {{
            background-color: {theme["primary"]};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# =============================
# Helper Functions
# =============================
def detect_course(text):
    text_lower = text.lower()

    for course in st.session_state.courses:
        if course.lower() in text_lower:
            return course

    if len(st.session_state.courses) > 0:
        return st.session_state.courses[0]

    return "Unassigned"


def parse_smart_input(text):
    lower_text = text.lower()

    difficulty = "Medium"
    estimated_hours = 3
    deadline = date.today() + timedelta(days=7)

    if "easy" in lower_text:
        difficulty = "Easy"
    elif "hard" in lower_text or "difficult" in lower_text:
        difficulty = "Hard"

    hours_match = re.search(r"(\d+)\s*(hours|hour|hrs|hr)", lower_text)
    if hours_match:
        estimated_hours = int(hours_match.group(1))

    if "today" in lower_text:
        deadline = date.today()
    elif "tomorrow" in lower_text:
        deadline = date.today() + timedelta(days=1)
    elif "next week" in lower_text:
        deadline = date.today() + timedelta(days=7)
    else:
        days_match = re.search(r"in\s*(\d+)\s*days", lower_text)
        if days_match:
            deadline = date.today() + timedelta(days=int(days_match.group(1)))

    return {
        "Task": text,
        "Course": detect_course(text),
        "Deadline": deadline,
        "Difficulty": difficulty,
        "Estimated Hours": estimated_hours,
        "Completed": False
    }


def calculate_priority(days_left, difficulty, estimated_hours):
    difficulty_score = {
        "Easy": 1,
        "Medium": 2,
        "Hard": 3
    }

    urgency_score = max(0, 10 - days_left) * 2
    difficulty_points = difficulty_score.get(difficulty, 2) * 3
    workload_points = estimated_hours

    return urgency_score + difficulty_points + workload_points


def generate_study_steps(task, difficulty):
    if difficulty == "Easy":
        return [
            "Review the task requirement.",
            "Complete the main work.",
            "Check your answer before submission."
        ]

    if difficulty == "Medium":
        return [
            "Read the task instructions carefully.",
            "Break the task into smaller sections.",
            "Finish the first draft.",
            "Review and improve your work.",
            "Submit before the deadline."
        ]

    return [
        "Understand the assignment requirements.",
        "Identify the most difficult part.",
        "Break the work into research, analysis, writing, and revision.",
        "Start with the hardest section first.",
        "Prepare a complete draft.",
        "Review carefully.",
        "Submit before the deadline."
    ]


def create_schedule(df):
    schedule = []
    unfinished = df[df["Completed"] == False]

    for _, row in unfinished.iterrows():
        days_left = max(row["Days Left"], 1)
        daily_hours = round(row["Estimated Hours"] / days_left, 1)

        for i in range(days_left):
            schedule_date = date.today() + timedelta(days=i)

            if schedule_date <= row["Deadline"]:
                schedule.append({
                    "Date": schedule_date,
                    "Course": row["Course"],
                    "Task": row["Task"],
                    "Suggested Study Time": f"{daily_hours} hrs",
                    "Priority Score": row["Priority Score"]
                })

    if len(schedule) == 0:
        return pd.DataFrame()

    return pd.DataFrame(schedule).sort_values(
        by=["Date", "Priority Score"],
        ascending=[True, False]
    )

# =============================
# Sidebar Appearance
# =============================
st.sidebar.header("🎨 Appearance")

theme_choice = st.sidebar.radio(
    "Choose Page Template",
    ["White Original", "Night Dark", "Eye Protection Green"],
    index=["White Original", "Night Dark", "Eye Protection Green"].index(
        st.session_state.theme_mode
    )
)

st.session_state.theme_mode = theme_choice
apply_theme(theme_choice)

# =============================
# Header
# =============================
st.markdown('<div class="main-title">📚 StudyFlow AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-powered course task manager for international students</div>',
    unsafe_allow_html=True
)

st.write(
    "StudyFlow AI helps students manage deadlines, prioritize tasks, "
    "break down assignments, and build a healthier study-life balance."
)

# =============================
# Sidebar Course Settings
# =============================
st.sidebar.header("📘 Course Settings")

new_course = st.sidebar.text_input("Add New Course")

if st.sidebar.button("Add Course"):
    clean_course = new_course.strip()

    if clean_course == "":
        st.sidebar.warning("Please enter a course name.")
    elif clean_course in st.session_state.courses:
        st.sidebar.warning("This course already exists.")
    else:
        st.session_state.courses.append(clean_course)
        st.sidebar.success(f"{clean_course} added!")

if len(st.session_state.courses) == 0:
    st.sidebar.info("No courses yet. Please add your first course.")
else:
    st.sidebar.write("Current Courses:")

    for course in st.session_state.courses:
        st.sidebar.write(f"- {course}")

    course_to_delete = st.sidebar.selectbox(
        "Choose Course to Delete",
        st.session_state.courses
    )

    if st.sidebar.button("Delete Course"):
        st.session_state.courses.remove(course_to_delete)

        for task in st.session_state.tasks:
            if task["Course"] == course_to_delete:
                task["Course"] = "Unassigned"

        st.sidebar.success(f"{course_to_delete} deleted!")

# =============================
# Sidebar Add Task
# =============================
st.sidebar.header("➕ Add New Task")

input_mode = st.sidebar.radio(
    "Choose Input Mode",
    ["Smart Input", "Manual Input"]
)

if input_mode == "Smart Input":
    smart_text = st.sidebar.text_area(
        "Describe your task",
        placeholder="Example: 60308A assignment due in 5 days hard 6 hours"
    )

    if st.sidebar.button("Analyze and Add Task"):
        if smart_text.strip() == "":
            st.sidebar.warning("Please enter a task description.")
        else:
            task = parse_smart_input(smart_text)
            st.session_state.tasks.append(task)
            st.sidebar.success("Smart task added successfully!")

else:
    task_name = st.sidebar.text_input("Task Name")

    if len(st.session_state.courses) == 0:
        st.sidebar.warning("Please add at least one course first.")
        course = "Unassigned"
    else:
        course = st.sidebar.selectbox("Course", st.session_state.courses)

    deadline = st.sidebar.date_input("Deadline", min_value=date.today())
    difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    estimated_hours = st.sidebar.number_input(
        "Estimated Hours",
        min_value=1,
        max_value=50,
        value=3
    )

    if st.sidebar.button("Add Task"):
        if task_name.strip() == "":
            st.sidebar.warning("Please enter a task name.")
        elif len(st.session_state.courses) == 0:
            st.sidebar.warning("Please add a course before creating a task.")
        else:
            st.session_state.tasks.append({
                "Task": task_name,
                "Course": course,
                "Deadline": deadline,
                "Difficulty": difficulty,
                "Estimated Hours": estimated_hours,
                "Completed": False
            })
            st.sidebar.success("Task added successfully!")

# =============================
# Dashboard
# =============================
st.markdown('<div class="section-title">📌 Dashboard</div>', unsafe_allow_html=True)

if len(st.session_state.tasks) == 0:
    st.info("No tasks yet. Add your first task from the sidebar.")

else:
    df = pd.DataFrame(st.session_state.tasks)
    df["Deadline"] = pd.to_datetime(df["Deadline"]).dt.date
    df["Days Left"] = df["Deadline"].apply(lambda x: (x - date.today()).days)

    df["Priority Score"] = df.apply(
        lambda row: calculate_priority(
            row["Days Left"],
            row["Difficulty"],
            row["Estimated Hours"]
        ),
        axis=1
    )

    df = df.sort_values(by="Priority Score", ascending=False).reset_index(drop=True)

    total_tasks = len(df)
    completed_tasks = int(df["Completed"].sum())
    urgent_tasks = len(df[(df["Days Left"] <= 3) & (df["Completed"] == False)])
    remaining_hours = df[df["Completed"] == False]["Estimated Hours"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tasks", total_tasks)
    col2.metric("Completed", completed_tasks)
    col3.metric("Urgent Tasks", urgent_tasks)
    col4.metric("Remaining Workload", f"{remaining_hours} hrs")

    progress = completed_tasks / total_tasks
    st.progress(progress)

    if progress == 1:
        st.success("🎉 Amazing! You completed all tasks. Enjoy your free time!")
    elif progress >= 0.5:
        st.success("👏 Good progress! Keep going.")
    else:
        st.info("Small progress every day matters.")

    st.markdown('<div class="section-title">🔥 Auto Priority Ranking</div>', unsafe_allow_html=True)

    st.dataframe(
        df[
            [
                "Task",
                "Course",
                "Deadline",
                "Days Left",
                "Difficulty",
                "Estimated Hours",
                "Priority Score",
                "Completed"
            ]
        ],
        use_container_width=True
    )

    st.markdown('<div class="section-title">🎯 Today Recommendation</div>', unsafe_allow_html=True)

    unfinished_df = df[df["Completed"] == False]

    if len(unfinished_df) > 0:
        top_task = unfinished_df.iloc[0]

        st.success(
            f"Today, you should focus on **{top_task['Task']}** "
            f"for **{top_task['Course']}**."
        )

        st.write(
            f"Reason: It has **{top_task['Days Left']} days left**, "
            f"difficulty is **{top_task['Difficulty']}**, "
            f"and estimated workload is **{top_task['Estimated Hours']} hours**."
        )
    else:
        st.success("🎉 No unfinished tasks today.")

    st.markdown('<div class="section-title">🗓️ Suggested Schedule Table</div>', unsafe_allow_html=True)

    schedule_df = create_schedule(df)

    if len(schedule_df) == 0:
        st.info("No schedule needed. All tasks are completed.")
    else:
        st.dataframe(schedule_df, use_container_width=True)

    st.markdown('<div class="section-title">🤖 Task Breakdown</div>', unsafe_allow_html=True)

    if len(unfinished_df) > 0:
        selected_task = st.selectbox(
            "Choose a task to break down",
            unfinished_df["Task"].tolist()
        )

        selected_row = unfinished_df[unfinished_df["Task"] == selected_task].iloc[0]

        if st.button("Generate Study Plan"):
            steps = generate_study_steps(
                selected_row["Task"],
                selected_row["Difficulty"]
            )

            st.subheader(f"Study Plan for: {selected_task}")

            for i, step in enumerate(steps, start=1):
                st.write(f"{i}. {step}")
    else:
        st.info("All tasks are completed.")

    st.markdown('<div class="section-title">✅ Complete Tasks</div>', unsafe_allow_html=True)

    for i, task in enumerate(st.session_state.tasks):
        checked = st.checkbox(
            f"{task['Task']} — {task['Course']}",
            value=task["Completed"],
            key=f"task_done_{i}"
        )

        if checked and not st.session_state.tasks[i]["Completed"]:
            st.balloons()
            st.success(f"Great job! You completed: {task['Task']}")

        st.session_state.tasks[i]["Completed"] = checked

    st.markdown('<div class="section-title">🗑️ Delete Task</div>', unsafe_allow_html=True)

    task_names = [task["Task"] for task in st.session_state.tasks]

    task_to_delete = st.selectbox("Choose a task to delete", task_names)

    if st.button("Delete Selected Task"):
        st.session_state.tasks = [
            task for task in st.session_state.tasks
            if task["Task"] != task_to_delete
        ]
        st.success("Task deleted.")