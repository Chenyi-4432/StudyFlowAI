import streamlit as st
import pandas as pd
import requests
import re
from datetime import date, timedelta

st.set_page_config(
    page_title="StudyFlow AI",
    page_icon="📚",
    layout="wide"
)

# =============================
# SUPABASE REST API CONFIG
# =============================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

COURSES_URL = f"{SUPABASE_URL}/rest/v1/courses"
TASKS_URL = f"{SUPABASE_URL}/rest/v1/tasks"


# =============================
# DATABASE FUNCTIONS
# =============================
def get_courses():
    r = requests.get(f"{COURSES_URL}?select=*", headers=HEADERS)
    if r.status_code == 200:
        return r.json()
    st.error(f"Failed to load courses: {r.text}")
    return []


def add_course(course_name):
    data = {"course_name": course_name}
    r = requests.post(COURSES_URL, headers=HEADERS, json=data)
    if r.status_code not in [200, 201]:
        st.error(f"Failed to add course: {r.text}")


def delete_course(course_id):
    r = requests.delete(f"{COURSES_URL}?id=eq.{course_id}", headers=HEADERS)
    if r.status_code not in [200, 204]:
        st.error(f"Failed to delete course: {r.text}")


def get_tasks():
    r = requests.get(f"{TASKS_URL}?select=*", headers=HEADERS)
    if r.status_code == 200:
        return r.json()
    st.error(f"Failed to load tasks: {r.text}")
    return []


def add_task(task_data):
    r = requests.post(TASKS_URL, headers=HEADERS, json=task_data)
    if r.status_code not in [200, 201]:
        st.error(f"Failed to add task: {r.text}")


def update_task_completed(task_id, completed):
    data = {"completed": completed}
    r = requests.patch(f"{TASKS_URL}?id=eq.{task_id}", headers=HEADERS, json=data)
    if r.status_code not in [200, 204]:
        st.error(f"Failed to update task: {r.text}")


def delete_task(task_id):
    r = requests.delete(f"{TASKS_URL}?id=eq.{task_id}", headers=HEADERS)
    if r.status_code not in [200, 204]:
        st.error(f"Failed to delete task: {r.text}")


# =============================
# THEME
# =============================
THEMES = {
    "White Original": {
        "bg": "#FFFFFF",
        "sidebar": "#F2F4F8",
        "text": "#262730",
        "primary": "#6C63FF"
    },
    "Night Dark": {
        "bg": "#121212",
        "sidebar": "#1E1E1E",
        "text": "#F5F5F5",
        "primary": "#9B8CFF"
    },
    "Eye Protection Green": {
        "bg": "#F3F8EF",
        "sidebar": "#E5F0DE",
        "text": "#243B2A",
        "primary": "#4F8A5B"
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

        h1, h2, h3, h4, p, label, span, div {{
            color: {theme["text"]};
        }}

        .main-title {{
            color: {theme["primary"]};
            font-size: 48px;
            font-weight: 800;
        }}

        .section-title {{
            color: {theme["primary"]};
            font-size: 28px;
            font-weight: 700;
            margin-top: 25px;
        }}

        .stButton button {{
            background-color: {theme["primary"]};
            color: white;
            border-radius: 10px;
            border: none;
            font-weight: 600;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# =============================
# HELPER FUNCTIONS
# =============================
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


def parse_smart_input(text, courses):
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

    detected_course = "Unassigned"

    for course in courses:
        if course["course_name"].lower() in lower_text:
            detected_course = course["course_name"]

    return {
        "task": text,
        "course": detected_course,
        "deadline": str(deadline),
        "difficulty": difficulty,
        "estimated_hours": estimated_hours,
        "completed": False
    }


def generate_steps(difficulty):
    if difficulty == "Easy":
        return [
            "Review the requirement.",
            "Complete the main work.",
            "Check and submit."
        ]

    if difficulty == "Medium":
        return [
            "Read the instructions carefully.",
            "Break the task into smaller parts.",
            "Finish the first draft.",
            "Review and improve.",
            "Submit before deadline."
        ]

    return [
        "Understand the full requirement.",
        "Identify the hardest part.",
        "Break it into research, analysis, writing, and revision.",
        "Start with the hardest section.",
        "Prepare a complete draft.",
        "Review carefully.",
        "Submit before deadline."
    ]


# =============================
# SIDEBAR
# =============================
st.sidebar.header("🎨 Appearance")

theme_choice = st.sidebar.radio(
    "Choose Page Template",
    ["White Original", "Night Dark", "Eye Protection Green"]
)

apply_theme(theme_choice)

courses = get_courses()
tasks = get_tasks()

st.sidebar.header("📘 Course Settings")

new_course = st.sidebar.text_input("Add New Course")

if st.sidebar.button("Add Course"):
    if new_course.strip() == "":
        st.sidebar.warning("Please enter a course name.")
    else:
        add_course(new_course.strip())
        st.rerun()

if len(courses) > 0:
    course_options = {c["course_name"]: c["id"] for c in courses}

    delete_course_name = st.sidebar.selectbox(
        "Choose Course to Delete",
        list(course_options.keys())
    )

    if st.sidebar.button("Delete Course"):
        delete_course(course_options[delete_course_name])
        st.rerun()
else:
    st.sidebar.info("No courses yet. Add your first course.")


st.sidebar.header("➕ Add New Task")

input_mode = st.sidebar.radio(
    "Input Mode",
    ["Smart Input", "Manual Input"]
)

if input_mode == "Smart Input":
    smart_text = st.sidebar.text_area(
        "Describe your task",
        placeholder="Example: 60308A assignment due in 5 days hard 6 hours"
    )

    if st.sidebar.button("Analyze and Add Task"):
        if smart_text.strip() == "":
            st.sidebar.warning("Please enter task description.")
        else:
            task_data = parse_smart_input(smart_text, courses)
            add_task(task_data)
            st.rerun()

else:
    task_name = st.sidebar.text_input("Task Name")

    if len(courses) > 0:
        course = st.sidebar.selectbox(
            "Course",
            [c["course_name"] for c in courses]
        )
    else:
        course = "Unassigned"
        st.sidebar.warning("No course available. Task will be Unassigned.")

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
            st.sidebar.warning("Please enter task name.")
        else:
            add_task({
                "task": task_name.strip(),
                "course": course,
                "deadline": str(deadline),
                "difficulty": difficulty,
                "estimated_hours": estimated_hours,
                "completed": False
            })
            st.rerun()


# =============================
# MAIN PAGE
# =============================
st.markdown('<div class="main-title">📚 StudyFlow AI</div>', unsafe_allow_html=True)
st.subheader("AI-powered course task manager for international students")

st.write(
    "StudyFlow AI helps students manage deadlines, prioritize tasks, "
    "break down assignments, and build a healthier study-life balance."
)

st.markdown('<div class="section-title">📌 Dashboard</div>', unsafe_allow_html=True)

if len(tasks) == 0:
    st.info("No tasks yet. Add your first task from the sidebar.")

else:
    df = pd.DataFrame(tasks)

    df["deadline"] = pd.to_datetime(df["deadline"]).dt.date
    df["days_left"] = df["deadline"].apply(lambda x: (x - date.today()).days)

    df["priority_score"] = df.apply(
        lambda row: calculate_priority(
            row["days_left"],
            row["difficulty"],
            row["estimated_hours"]
        ),
        axis=1
    )

    df = df.sort_values(
        by="priority_score",
        ascending=False
    ).reset_index(drop=True)

    total_tasks = len(df)
    completed_tasks = int(df["completed"].sum())
    urgent_tasks = len(df[(df["days_left"] <= 3) & (df["completed"] == False)])
    remaining_hours = df[df["completed"] == False]["estimated_hours"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tasks", total_tasks)
    col2.metric("Completed", completed_tasks)
    col3.metric("Urgent Tasks", urgent_tasks)
    col4.metric("Remaining Workload", f"{remaining_hours} hrs")

    progress = completed_tasks / total_tasks
    st.progress(progress)

    if progress == 1:
        st.success("🎉 Amazing! You completed all tasks.")
    elif progress >= 0.5:
        st.success("👏 Good progress! Keep going.")
    else:
        st.info("Small progress every day matters.")

    st.markdown('<div class="section-title">🔥 Auto Priority Ranking</div>', unsafe_allow_html=True)

    st.dataframe(
        df[
            [
                "task",
                "course",
                "deadline",
                "days_left",
                "difficulty",
                "estimated_hours",
                "priority_score",
                "completed"
            ]
        ],
        use_container_width=True
    )

    st.markdown('<div class="section-title">🎯 Today Recommendation</div>', unsafe_allow_html=True)

    unfinished_df = df[df["completed"] == False]

    if len(unfinished_df) > 0:
        top_task = unfinished_df.iloc[0]

        st.success(
            f"Today, you should focus on **{top_task['task']}** "
            f"for **{top_task['course']}**."
        )

    else:
        st.success("🎉 No unfinished tasks today.")

    st.markdown('<div class="section-title">🗓️ Suggested Schedule Table</div>', unsafe_allow_html=True)

    schedule_rows = []

    for _, row in unfinished_df.iterrows():
        days_left = max(row["days_left"], 1)
        daily_hours = round(row["estimated_hours"] / days_left, 1)

        for i in range(days_left):
            schedule_date = date.today() + timedelta(days=i)

            if schedule_date <= row["deadline"]:
                schedule_rows.append({
                    "Date": schedule_date,
                    "Course": row["course"],
                    "Task": row["task"],
                    "Suggested Study Time": f"{daily_hours} hrs",
                    "Priority Score": row["priority_score"]
                })

    if schedule_rows:
        schedule_df = pd.DataFrame(schedule_rows)
        st.dataframe(schedule_df, use_container_width=True)
    else:
        st.info("No schedule needed.")

    st.markdown('<div class="section-title">🤖 Task Breakdown</div>', unsafe_allow_html=True)

    if len(unfinished_df) > 0:
        selected_task = st.selectbox(
            "Choose a task to break down",
            unfinished_df["task"].tolist()
        )

        selected_row = unfinished_df[unfinished_df["task"] == selected_task].iloc[0]

        if st.button("Generate Study Plan"):
            steps = generate_steps(selected_row["difficulty"])

            for i, step in enumerate(steps, start=1):
                st.write(f"{i}. {step}")

    st.markdown('<div class="section-title">✅ Complete Tasks</div>', unsafe_allow_html=True)

    for _, row in df.iterrows():
        checked = st.checkbox(
            f"{row['task']} — {row['course']}",
            value=row["completed"],
            key=f"task_{row['id']}"
        )

        if checked != row["completed"]:
            update_task_completed(row["id"], checked)
            if checked:
                st.balloons()
                st.success(f"Great job! You completed: {row['task']}")
            st.rerun()

    st.markdown('<div class="section-title">🗑️ Delete Task</div>', unsafe_allow_html=True)

    task_options = {row["task"]: row["id"] for _, row in df.iterrows()}

    task_to_delete = st.selectbox(
        "Choose a task to delete",
        list(task_options.keys())
    )

    if st.button("Delete Selected Task"):
        delete_task(task_options[task_to_delete])
        st.rerun()