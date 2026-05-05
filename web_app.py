import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

os.chdir(os.path.split(__file__)[0])
from email_sender import send_result_email

st.set_page_config(page_title="Creativity Study", layout="centered")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #ffffff; }
[data-testid="stHeader"] { background-color: #ffffff; }
.main .block-container { background-color: #ffffff; padding-top: 2rem; color: #2c3e50; }
h1, h2, h3 { color: #3a5a8c !important; }
p, label, div, span, li { color: #2c3e50 !important; }
.stTextInput input { background-color: #ffffff !important; color: #2c3e50 !important; }
.stTextArea textarea { background-color: #ffffff !important; color: #2c3e50 !important; }
.stButton > button {
    background-color: #a8c8e8;
    color: #1a2e4a !important;
    border: none;
    border-radius: 8px;
    padding: 0.5em 2em;
    font-weight: 600;
}
.stButton > button:hover { background-color: #7fb3d9; }
#auto-btn { display: none; }
</style>
""", unsafe_allow_html=True)

if "stage" not in st.session_state:
    st.session_state.stage = "q1"
if "data" not in st.session_state:
    st.session_state.data = {}
if "task_index" not in st.session_state:
    st.session_state.task_index = 0

IMAGE_DIR = "images"
RATING_OPTIONS = ["0", "1", "2", "3", "4", "5", "6", "7"]
TASK_DURATION = 180
BREAK_DURATION = 30

def countdown_timer(remaining_seconds, label, auto_trigger_key):
    """Show JS countdown. When it hits 0, click the hidden Streamlit button."""
    st.markdown(f'<div id="timer-display">⏱ {label}: <strong id="timer-val"></strong></div>', unsafe_allow_html=True)
    # Hidden button that JS will click when time is up
    clicked = st.button("__auto__", key=auto_trigger_key)
    st.markdown("""
<style>
button[kind="secondary"][data-testid="baseButton-secondary"] { display: none !important; }
</style>
""", unsafe_allow_html=True)
    st.components.v1.html(f"""
<script>
var remaining = {int(remaining_seconds)};
function fmt(s) {{
    var m = Math.floor(s / 60);
    var sec = s % 60;
    return m + ":" + (sec < 10 ? "0" : "") + sec;
}}
function tick() {{
    var el = window.parent.document.getElementById("timer-val");
    if (el) el.innerText = fmt(remaining);
    if (remaining <= 0) {{
        var buttons = window.parent.document.querySelectorAll("button");
        for (var i = 0; i < buttons.length; i++) {{
            if (buttons[i].innerText.trim() === "__auto__") {{
                buttons[i].click();
                return;
            }}
        }}
    }}
    remaining--;
    setTimeout(tick, 1000);
}}
tick();
</script>
""", height=0)
    return clicked

def save_to_excel(data):
    exp_code = data.get("exp_code", "unknown")
    filename = f"{exp_code}.xlsx"
    new_row = {
        "Submission Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Experiment Code": data.get("exp_code", ""),
        "Q1: Last Digit of Experiment Code": data.get("q1_last_digit", ""),
        "Q2: Stress Resistance Score (0-7)": data.get("q2_resistance", ""),
        "Q3: Current Stress Level (0-7)": data.get("q3_stress", ""),
        "Group": data.get("group", ""),
        "Task 1 (Brick) - Responses": data.get("task1", ""),
        "Task 2 (Paperclip) - Responses": data.get("task2", ""),
        "Task 3 (Newspaper) - Responses": data.get("task3", ""),
        "Q5: Stress During Experiment (0-7)": data.get("q5_stress", ""),
    }
    df = pd.DataFrame([new_row])
    df.to_excel(filename, index=False)
    return filename

# ── Stage 1: Experiment Code ──────────────────────────────────────────────────
if st.session_state.stage == "q1":
    st.title("Creativity Research Study")
    st.markdown("Welcome! Please read each question carefully and answer honestly.")
    st.markdown("---")
    exp_code = st.text_input(
        label="Q1: Please enter your experiment code:",
        placeholder="Enter your experiment code here",
        key="exp_code_input"
    )
    st.markdown("")
    if st.button("Continue →", type="primary"):
        code = exp_code.strip()
        if not code:
            st.error("Please enter your experiment code.")
        elif not code[-1].isdigit():
            st.error("The last character of your experiment code must be a digit.")
        else:
            last = code[-1]
            st.session_state.data["exp_code"] = code
            st.session_state.data["q1_last_digit"] = last
            st.session_state.data["group"] = "control" if int(last) % 2 == 1 else "experimental"
            st.session_state.stage = "q2_q3"
            st.rerun()

# ── Stage 2: Q2 + Q3 ─────────────────────────────────────────────────────────
elif st.session_state.stage == "q2_q3":
    st.title("Creativity Research Study")
    st.markdown("---")
    q2_val = st.radio(
        label="Q2: On a scale of 0–7, how would you rate your ability to cope with pressure? (0 = very low, 7 = very high)",
        options=RATING_OPTIONS,
        index=None,
        key="q2_radio"
    )
    st.markdown("---")
    q3_val = st.radio(
        label="Q3: On a scale of 0–7, how stressed do you feel right now? (0 = not at all, 7 = extremely stressed)",
        options=RATING_OPTIONS,
        index=None,
        key="q3_radio"
    )
    st.markdown("")
    if st.button("Continue →", type="primary"):
        if q2_val is None or q3_val is None:
            st.error("Please answer both questions before continuing.")
        else:
            st.session_state.data["q2_resistance"] = q2_val
            st.session_state.data["q3_stress"] = q3_val
            st.session_state.stage = "task_intro"
            st.rerun()

# ── Stage 3: Task Instructions ────────────────────────────────────────────────
elif st.session_state.stage == "task_intro":
    group = st.session_state.data["group"]
    st.title("Main Task Instructions")
    st.markdown("---")
    if group == "control":
        st.markdown("""
You will be participating in a **job recruitment exercise**.

Your competitors are university students at the same level as you.
**Everyone works independently — no AI tools, no search engines are allowed.**

Final rankings will be based on your **creativity score**.

**Your task:** For each object shown, generate as many **unusual, novel, and reasonable non-conventional uses** as possible within **3 minutes**.
Exclude the object's original/intended use.
Give your best effort to outperform the other candidates.

You may respond in your native language.
        """)
    else:
        st.markdown("""
You will be participating in a **job recruitment exercise**.

Your competitors are university students at the same level as you.
**Some of them will have access to AI tools** to assist their thinking and expand their creative ideas, giving them a creative advantage.

Final rankings will be based on your **creativity score**.

**Your task:** For each object shown, generate as many **unusual, novel, and reasonable non-conventional uses** as possible within **3 minutes**.
Exclude the object's original/intended use.
Give your best effort to outperform the other candidates.

You may respond in your native language.
        """)
    st.markdown("---")
    st.markdown("There are **3 objects** in total. After each 3-minute task, you will have a **30-second break**.")
    st.markdown("")
    if st.button("I'm Ready — Start Task 1", type="primary"):
        st.session_state.stage = "task"
        st.session_state.task_index = 0
        st.rerun()

# ── Stage 4: Tasks ────────────────────────────────────────────────────────────
elif st.session_state.stage == "task":
    idx = st.session_state.task_index
    group = st.session_state.data["group"]

    tasks = [
        {"name": "Brick",     "control_img": "Control-bricks.jpg",     "exp_img": "Experimental-bricks.jpg",     "key": "task1"},
        {"name": "Paperclip", "control_img": "Control-paperclips.jpg", "exp_img": "Experimental-paperclips.jpg", "key": "task2"},
        {"name": "Newspaper", "control_img": "Control-newspapers.jpg", "exp_img": "Experimental-newspapers.jpg", "key": "task3"},
    ]
    task = tasks[idx]
    img_file = task["control_img"] if group == "control" else task["exp_img"]
    img_path = os.path.join(IMAGE_DIR, img_file)

    task_key = f"task_start_{idx}"
    if task_key not in st.session_state:
        st.session_state[task_key] = time.time()

    elapsed = time.time() - st.session_state[task_key]
    remaining = max(0, TASK_DURATION - elapsed)

    st.title(f"Task {idx + 1} of 3: {task['name']}")
    st.markdown("---")

    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists(img_path):
            st.image(img_path, caption=task["name"], width=260)
        else:
            st.warning(f"Image not found: {img_path}")
    with col2:
        st.markdown(f"""
**Object: {task['name']}**

List as many **unusual, novel, and reasonable non-conventional uses** as you can think of.

- One use per line
- Exclude the original/intended use
- You have **3 minutes**
        """)

    st.text_area(
        label=f"Your responses for {task['name']} (one use per line):",
        height=220,
        key=f"response_{idx}"
    )

    auto_clicked = countdown_timer(remaining, "Time remaining", f"auto_task_{idx}")

    st.markdown("")
    manual_clicked = st.button("Submit & Continue", type="primary", key=f"manual_task_{idx}")

    if auto_clicked or manual_clicked:
        st.session_state.data[task["key"]] = st.session_state.get(f"response_{idx}", "")
        st.session_state.stage = "break" if idx < 2 else "final_q"
        st.rerun()

# ── Stage 5: Break ────────────────────────────────────────────────────────────
elif st.session_state.stage == "break":
    idx = st.session_state.task_index
    task_names = ["Brick", "Paperclip", "Newspaper"]

    if "break_start" not in st.session_state or st.session_state.get("break_idx") != idx:
        st.session_state.break_start = time.time()
        st.session_state.break_idx = idx

    elapsed = time.time() - st.session_state.break_start
    remaining = max(0, BREAK_DURATION - elapsed)

    st.title("Rest Break")
    st.markdown("---")
    st.markdown(f"### Task {idx + 1} complete! Great work. 🎉")
    st.markdown("Please take about **30 seconds** to rest and relax before the next task.")
    st.markdown("")
    if idx + 1 < len(task_names):
        st.markdown(f"**Next object: {task_names[idx + 1]}**")
    st.markdown("")

    auto_clicked = countdown_timer(remaining, "Next task starts in", f"auto_break_{idx}")

    st.markdown("")
    manual_clicked = st.button(f"I'm Ready — Start Task {idx + 2}", type="primary", key=f"manual_break_{idx}")

    if auto_clicked or manual_clicked:
        st.session_state.task_index += 1
        st.session_state.stage = "task"
        st.rerun()

# ── Stage 6: Final Question ───────────────────────────────────────────────────
elif st.session_state.stage == "final_q":
    st.title("Final Question")
    st.markdown("---")
    st.markdown("You have completed all three tasks. Thank you for your effort!")
    st.markdown("")
    q5_val = st.radio(
        label="Q5: On a scale of 0–7, how stressed did you feel during the tasks above? (0 = not at all, 7 = extremely stressed)",
        options=RATING_OPTIONS,
        index=None,
        key="q5_radio"
    )
    st.markdown("")
    if st.button("Submit All Responses", type="primary"):
        if q5_val is None:
            st.error("Please answer the question before submitting.")
        else:
            st.session_state.data["q5_stress"] = q5_val
            exp_code = st.session_state.data.get("exp_code", "unknown")
            filename = save_to_excel(st.session_state.data)
            send_result_email(exp_code, filename)
            st.session_state.stage = "done"
            st.rerun()

# ── Stage 7: Done ─────────────────────────────────────────────────────────────
elif st.session_state.stage == "done":
    st.title("Submission Complete ✅")
    st.markdown("---")
    st.markdown("Your responses have been successfully recorded.")
    st.markdown("Thank you for participating in this study!")
    st.markdown("You may now close this window.")
