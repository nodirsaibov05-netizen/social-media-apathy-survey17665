import json
import csv
from datetime import datetime
import re
import os

# -10 types of variables-
version_float = 2.0                          # float
allowed_formats = frozenset({".json", ".csv", ".txt"})  # frozenset
used_ids = set()                                     # set
student_record = {}                                  # dict
answers_list = []                                    # list
prefixes = ("Mr", "Ms", "Dr")                         # tuple
question_range = range(1, 21)                        # range
debug = False                                        # bool
max_questions = 20                                   # int
title_str = "Social Media Use & Apathy Level Assessment"  # str
# ----------------------------------------------------

# -20 Questions implemented in code-
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
     "opts": [("Totally disagree ",0), ("Rather disagree",1), ("Neutral",2), ("Rather agree",3), ("Totally agree",4)]},
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

# -6 Final states-
psych_states = {
    "Missing/Very weak connection, High activity & motivation": (0, 32),
    "Weak connection – does not interfere with real life": (33, 45),
    "Moderate connection – symptoms noticeable but not dominant": (46, 58),
    "Pronounced connection – intensive SM use + clear apathy": (59, 71),
    "Strong connection – excessive use, high passivity": (72, 85),
    "Critically strong dependence – serious loss of life interest, seek medical help": (86, 100)
}

# Functions
def validate_name(name: str) -> bool:
    return bool(re.match(r"^[A-Za-z\s'-]+$", name.strip())) and len(name.strip()) >= 2

def validate_dob(dob: str) -> bool:
    try:
        year, month, day = map(int, dob.split("-"))
        date = datetime(year, month, day)
        return date <= datetime.now()
    except:
        return False

def load_questions_from_file(path: str):
    path = path.strip().strip('"\'')
    
    if not os.path.exists(path):
        print("File not found. Check the path.")
        return None
        
    if not path.lower().endswith(".json"):
        print("Works with .json files")
        return None
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Two formats:
        if isinstance(data, list):
            # file - list od questions
            loaded_questions = data
        elif isinstance(data, dict):
            # file - dictionary with "questions" key
            loaded_questions = data.get("questions", [])
        else:
            print("Invalid file format")
            return None

        if len(loaded_questions) < 10:
            print("Number of questions should be more than 10")
            return None
            
        print(f"Successfully loaded {len(loaded_questions)} from file.")
        return loaded_questions
        
    except Exception as e:
        print(f"Error in reading the file: {e}")
        return None

def save_questions_and_states():
    data = {
        "questions": questions,
        "psychological_states": list(psych_states.items())
    }
    with open("survey_questions_and_states.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Saved: survey_questions_and_states.json")

# -Questionnaire-
def run_survey(q_list):
    total = 0
    answers_list.clear()
    
    for idx in question_range:
        q = q_list[idx-1]
        
        # Questions implementation
        question_text = q.get("q") or q.get("text") or q.get("question", "No question")
        
        # Answers implementation
        raw_opts = q.get("opts") or q.get("options") or q.get("answers", [])
        
        # Everything in one type: [["Never",0], ...]
        options = []
        for item in raw_opts:
            if isinstance(item, dict):
                text = item.get("text", item.get("answer", "???"))
                score = item.get("score", item.get("value", 0))
            elif isinstance(item, (list, tuple)):
                text = item[0]
                score = item[1] if len(item) > 1 else 0
            else:
                text = str(item)
                score = 0
            options.append([text, score])
        
        if len(options) != 5:
            print("Error: There should be 5 answer options")
            continue
            
        print(f"\nQuestion {idx}/{max_questions}: {question_text}")
        for i, (text, score) in enumerate(options, 1):
            print(f"  {i}. {text}")
            
        while True:
            try:
                choice = int(input("Choose (1-5): "))
                if 1 <= choice <= 5:
                    selected = options[choice-1]
                    total += selected[1]
                    answers_list.append({
                        "question": question_text,
                        "answer": selected[0],
                        "score": selected[1]
                    })
                    break
            except:
                pass
            print("Enter a number between 1-5")
    
    return total

def get_result(score: int) -> str:
    for state, (low, high) in psych_states.items():
        if low <= score <= high:
            return state
    return "Unknown"

# -Saving results: 3 types-
def save_result(fmt: str, data: dict):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"result_{data['student_id']}_{ts}.{fmt}"
    if fmt == "json":
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    elif fmt == "csv":
        with open(filename, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Field", "Value"])
            for k, v in data.items():
                w.writerow([k, str(v)])
    else:  # txt
        with open(filename, "w", encoding="utf-8") as f:
            for k, v in data.items():
                f.write(f"{k}: {v}\n")
    print(f"Saved: {filename}")

# -Main-
def main():
    print("="*70)
    print(title_str.center(70))
    print("="*70)
    print("1. Load existing result file")
    print("2. Start new questionnaire (embedded questions)")
    print("3. Start new questionnaire (load questions from file)")
    print("4. Save survey questions + psychological states to external file")
    
    choice = input("\nSelect (1-4): ").strip()

    if choice == "4":
        save_questions_and_states()
        return
    if choice == "1":
        path = input("File name: ")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                print(f.read())
        else:
            print("File not found")
        return

    # Data entry with validation
    while True:
        name = input("Given name: ").strip()
        if validate_name(name): break
        print("Only letters, space, -, '")

    while True:
        surname = input("Surname: ").strip()
        if validate_name(surname): break
        print("Only letters, space, -, '")

    while True:
        dob = input("Date of birth (YYYY-MM-DD): ")
        if validate_dob(dob): break
        print("Invalid date")

    while True:
        sid = input("Student ID (digits only): ").strip()
        if sid.isdigit() and len(sid) >= 5 and sid not in used_ids:
            used_ids.add(sid)
            break
        print("Invalid or duplicate ID")

    # Questions choice
    current_questions = questions
    if choice == "3":
        path = input("Path to questions file (.json): ")
        loaded = load_questions_from_file(path)
        if loaded:
            current_questions = loaded
            print(f"Loaded {len(loaded)} questions from file")

    # Questionnaire
    total_score = run_survey(current_questions)
    result = get_result(total_score)

    print(f"\n{'='*30} RESULT {'='*30}")
    print(f"Name: {name} {surname} | ID: {sid}")
    print(f"Total score: {total_score}/100")
    print(f"Result: {result}")

    # Saving results
    fmt = input("Save as (json/csv/txt) [json]: ").lower().strip() or "json"
    if fmt not in ["json", "csv", "txt"]:
        fmt = "json"

    student_record = {
        "given_name": name,
        "surname": surname,
        "dob": dob,
        "student_id": sid,
        "total_score": total_score,
        "result": result,
        "answers": answers_list,
        "survey_date": datetime.now().isoformat(),
        "version": version_float
    }

    save_result(fmt, student_record)

if __name__ == "__main__":
    main()