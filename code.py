import streamlit as st
import json
from datetime import datetime
import re
import os

st.set_page_config(page_title="Social Media & Apathy Survey", layout="centered")
st.title("Social Media Use & Apathy Level Assessment")
st.caption("Assessment of the relationship between excessive use of social media and manifestations of apathy")

# --10 types of variables--
version_float = 2.0
allowed_formats = frozenset({".json", ".csv", ".txt"})
used_ids = st.session_state.get("used_ids", set())  # сохраняем между сессиями
debug = False
max_questions = 20
title_str = "Social Media Use & Apathy Level Assessment"

# --- 20 Questions ---
questions = [
    {"q": "I open social media even when I'm actively engaged in other things (studies, work).",
     "opts": [("Never",0), ("Rarely",1), ("Sometimes",2), ("Often",3), ("Always",4)]},
    {"q": "I spend significantly more time on social media than I originally planned.",
     "opts": [("Never",0), ("Rarely",1), ("Sometimes",2), ("Often",3), ("Always",4)]},
    {"q": "I use social media to fill in the 'empty' pauses during the day (in transport, in line).",
     "opts": [("Never",0), ("Rarely",1), ("Sometimes",2), ("Often",3), ("Always",4)]},
    {"q": "I feel like I have to be online so I don't miss important information or trends (FOMO).",
     "opts": [("Never",0), ("Rarely",1), ("Sometimes",2), ("Often",3), ("Always",4)]},
    {"q": "If my social media content doesn't get the expected reaction, I feel disappointed.",
     "opts": [("Totally disagree",1), ("Rather disagree",2), ("Neutral",3), ("Rather agree",4), ("Totally agree",5)]},
    {"q": "Even when I'm bored on social media, I keep browsing them because I can't find an alternative.",
     "opts": [("Never",0), ("Rarely",1), ("Sometimes",2), ("Often",3), ("Always",4)]},
    {"q": "I tend to passively consume content on social media, almost never creating my own.",
     "opts": [("Totally disagree",0), ("Rather disagree",1), ("Neutral",2), ("Rather agree",3), ("Totally agree",4)]},
    {"q": "I've lost interest in my old hobbies or pursuits.",
     "opts": [("Totally disagree",0), ("Rather disagree",1), ("Neutral",2), ("Rather agree",3), ("Totally agree",4)]},
    {"q": "I don't care how events will develop in my life in the coming months/years.",
     "opts": [("Totally disagree",1), ("Rather disagree",2), ("Neutral",3), ("Rather agree",4), ("Totally agree",5)]},
    {"q": "It is difficult for me to feel strong positive emotions (joy, delight) even in favorable situations.",
     "opts": [("Totally disagree",1), ("Rather disagree",2), ("Neutral",3), ("Rather agree",4), ("Totally agree",5)]},
    {"q": "I often feel a lack of purpose or direction in my life.",
     "opts": [("Totally disagree",0), ("Rather disagree",1), ("Neutral",2), ("Rather agree",3), ("Totally agree",4)]},
    {"q": "I am indifferent to the praise or criticism from others.",
     "opts": [("Totally disagree",1), ("Rather disagree",2), ("Neutral",3), ("Rather agree",4), ("Totally agree",5)]},
    {"q": "I stop following the progress of my friends in real life, preferring to monitor their online activity.",
     "opts": [("Totally disagree",0), ("Rather disagree",1), ("Neutral",2), ("Rather agree",3), ("Totally agree",4)]},
    {"q": "I became less sensitive to the need to help others or participate in social life.",
     "opts": [("Totally disagree",0), ("Rather disagree",1), ("Neutral",2), ("Rather agree",3), ("Totally agree",4)]},
    {"q": "The more time I spend on social media, the less energy I have for active actions in real life.",
     "opts": [("Totally disagree",1), ("Rather disagree",2), ("Neutral",3), ("Rather agree",4), ("Totally agree",5)]},
    {"q": "Scrolling through the news feed often makes me feel like I don't need to put in effort, because nothing will change anyway.",
     "opts": [("Never",0), ("Rarely",1), ("Sometimes",2), ("Often",3), ("Always",4)]},
    {"q": "After using social media for a long time, I become passive and unable to switch to something productive.",
     "opts": [("Never",0), ("Rarely",1), ("Sometimes",2), ("Often",3), ("Always",4)]},
    {"q": "I use social media because I don't want to waste efforts on finding more challenging and meaningful activities.",
     "opts": [("Totally disagree",0), ("Rather disagree",1), ("Neutral",2), ("Rather agree",3), ("Totally agree",4)]},
    {"q": "My attitude towards personal achievements became more indifferent after spending a lot of time in social media.",
     "opts": [("Totally disagree",1), ("Rather disagree",2), ("Neutral",3), ("Rather agree",4), ("Totally agree",5)]},
    {"q": "If I have to choose between active activity and passive viewing of social media content, I almost always choose viewing.",
     "opts": [("Never",0), ("Rarely",1), ("Sometimes",2), ("Often",3), ("Always",4)]}
]

psych_states = {
    "Missing/Very weak connection, High activity & motivation. 
    No symptoms of apathy; the use of social media is under complete control, without causing procrastination. Life activity, motivation and interest in real hobbies remain at a very high level.": (0, 32),
    "Weak connection – does not interfere with real life. The use of social media is moderate and does not have a significant negative impact on the daily routine or emotional background. Any signs of apathy are minimal and are most likely caused by other factors unrelated to online activity.": (33, 45),
    "Moderate connection – symptoms noticeable but not dominant. The time spent on social media is noticeably increasing, which sometimes leads to passive consumption of content and reduced motivation to perform complex tasks. There is a moderate risk of developing apathy, as social media begins to be used as a means of avoidance": (46, 58),
    "Pronounced connection – intensive SM use + clear apathy. Heavy use of SM correlates with overt manifestations of apathy, such as emotional lethargy and lack of goals. Time spent online significantly displaces productive activities and social contacts in the real world": (59, 71),
    "Strong connection – excessive use, high passivity. Social media activity becomes almost obsessive and dominant, which is accompanied by significant manifestations of apathy (loss of meaning, complete indifference). There is a high degree of inertia and passivity that requires attention to behavioral patterns.": (72, 85),
    "Critically strong dependence – serious loss of life interest. This condition indicates a critical dependence on SM and the accompanying deep apathy, in which there is a complete lack of will and motivation. A malfunction requires examination by a specialist and, possibly, psychological intervention.": (86, 100)
}

# --- Menu ---
menu = st.sidebar.selectbox("Menu", [
    "2. Start new survey (embedded)",
    "1. Load existing result",
    "3. Start new survey (from file)",
    "4. Save questions + states"
])

if menu == "4. Save questions + states":
    data = {"questions": questions, "psychological_states": list(psych_states.items())}
    st.download_button("Download questions_and_states.json", json.dumps(data, indent=2, ensure_ascii=False), "survey_questions_and_states.json")
    st.stop()

if menu == "1. Load existing result":
    uploaded = st.file_uploader("Upload result (.json/.csv/.txt)", type=["json", "csv", "txt"])
    if uploaded:
        st.code(uploaded.read().decode("utf-8"))
    st.stop()

current_questions = questions
if menu == "3. Start new survey (from file)":
    uploaded = st.file_uploader("Upload questions.json", type="json", key="qfile")
    if uploaded:
        try:
            data = json.load(uploaded)
            current_questions = data if isinstance(data, list) else data.get("questions", questions)
            st.success(f"Loaded {len(current_questions)} questions")
        except:
            st.error("Invalid file")

# --- Questionnaire start ---
if "started" not in st.session_state:
    st.header("Personal Information")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Given name", placeholder="Nodixon")
        surname = st.text_input("Surname", placeholder="Saibov")
    with col2:
        dob = st.text_input("Date of birth (YYYY-MM-DD)", placeholder="2005-05-26")
        sid = st.text_input("Student ID", placeholder="17665")

    if st.button("Start Survey", key="start_survey"):
        if (name.strip() and surname.strip() and
            re.match(r"^\d{4}-\d{2}-\d{2}$", dob) and
            sid.isdigit() and len(sid) >= 5 and sid not in used_ids):
            used_ids.add(sid)
            st.session_state.update({
                "name": name.strip(), "surname": surname.strip(),
                "dob": dob, "sid": sid, "answers": [], "idx": 0, "started": True
            })
            st.rerun()
        else:
            st.error("Check data: name/surname not empty, date YYYY-MM-DD, ID ≥5 digits and unique")

    st.stop()

# --- Main part ---
if st.session_state.idx < len(current_questions):
    q = current_questions[st.session_state.idx]
    st.write(f"**Question {st.session_state.idx + 1}/{len(current_questions)}**")
    st.write(q["q"])

    for i, (text, score) in enumerate(q["opts"]):
        if st.button(text, key=f"q{st.session_state.idx}_opt{i}"):
            st.session_state.answers.append({"q": q["q"], "answer": text, "score": score})
            st.session_state.idx += 1
            st.rerun()

    st.progress(st.session_state.idx / len(current_questions))

# --- Result ---
else:
    total = sum(a["score"] for a in st.session_state.answers)
    result = next((s for s, (l, h) in psych_states.items() if l <= total <= h), "Unknown")
    st.balloons()
    st.success(f"**{result}** (Score: {total}/100)")

    data = {
        "given_name": st.session_state.name,
        "surname": st.session_state.surname,
        "dob": st.session_state.dob,
        "student_id": st.session_state.sid,
        "total_score": total,
        "result": result,
        "answers": st.session_state.answers,
        "survey_date": datetime.now().isoformat(),
        "version": version_float
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"result_{st.session_state.sid}_{ts}"

    fmt = st.selectbox("Save as", ["json", "csv", "txt"])
    if fmt == "json":
        st.download_button("Download JSON", json.dumps(data, indent=2, ensure_ascii=False), f"{filename}.json")
    elif fmt == "csv":
        csv_lines = ["Field,Value"]
        for k, v in data.items():
            if k != "answers":
                csv_lines.append(f"{k},{v}")
        for a in data["answers"]:
            csv_lines.append(f"Question,{a['q']}")
            csv_lines.append(f"Answer,{a['answer']}")
            csv_lines.append(f"Score,{a['score']}")
        st.download_button("Download CSV", "\n".join(csv_lines), f"{filename}.csv")
    else:
        txt = "\n".join(f"{k}: {v}" for k, v in data.items() if k != "answers")
        txt += "\n\nAnswers:\n" + "\n".join(f"Q: {a['q']}\nA: {a['answer']} (score: {a['score']})" for a in data["answers"])
        st.download_button("Download TXT", txt, f"{filename}.txt")



