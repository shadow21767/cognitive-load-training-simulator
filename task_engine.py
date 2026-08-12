import random

MEDICATIONS = [
    ("Amoxicillin", "500 mg", "Oral", "Every 8 hours"),
    ("Metformin", "500 mg", "Oral", "Twice daily"),
    ("Lisinopril", "10 mg", "Oral", "Once daily"),
    ("Acetaminophen", "325 mg", "Oral", "Every 6 hours"),
    ("Atorvastatin", "20 mg", "Oral", "Once daily"),
]
COLORS = ["RED", "BLUE", "GREEN", "YELLOW"]


def medication_task(difficulty: int) -> dict:
    medication, dose, route, frequency = random.choice(MEDICATIONS)
    correct = f"{medication} — {dose} — {route} — {frequency}"
    distractors = []
    for m, d, r, f in MEDICATIONS:
        distractors.extend([
            f"{m} — {d} — {r} — {f}",
            f"{m} — {dose} — {r} — {f}",
            f"{medication} — {d} — {route} — {f}",
        ])
    distractors = list(dict.fromkeys(x for x in distractors if x != correct))
    random.shuffle(distractors)
    options = [correct] + distractors[: min(2 + difficulty, 5)]
    random.shuffle(options)
    return {
        "task_type": "Medication Match",
        "prompt": f"Select the label matching **{medication}**, **{dose}**, **{route}**, **{frequency}**.",
        "correct": correct,
        "options": options,
    }


def stroop_task() -> dict:
    word = random.choice(COLORS)
    ink = random.choice([c for c in COLORS if c != word])
    return {
        "task_type": "Stroop Interference",
        "prompt": f"The word is **{word}**. Ignore the word and select the simulated ink color: **{ink}**.",
        "correct": ink,
        "options": COLORS.copy(),
    }


def memory_task(number: int) -> dict:
    options = [str(number)]
    while len(options) < 4:
        candidate = str(random.randint(10, 99))
        if candidate not in options:
            options.append(candidate)
    random.shuffle(options)
    return {
        "task_type": "Working Memory",
        "prompt": "Select the number you were asked to remember.",
        "correct": str(number),
        "options": options,
    }


def keyboard_task() -> dict:
    letter = random.choice(["A", "S", "D", "F"])
    return {
        "task_type": "Keyboard Response",
        "prompt": f"Type **{letter}** and submit the response.",
        "correct": letter,
        "options": [],
    }


def create_task(condition_cfg: dict, difficulty: int, task_number: int, memory_number: int) -> dict:
    switch_trial = random.random() < float(condition_cfg["switch_probability"])
    distraction = random.random() < float(condition_cfg["distraction_probability"])

    if task_number == 3 and condition_cfg.get("memory_load"):
        task = memory_task(memory_number)
    elif task_number == 6:
        task = keyboard_task()
    elif random.random() < float(condition_cfg["stroop_probability"]) or switch_trial:
        task = stroop_task()
    else:
        task = medication_task(difficulty)

    task["switch_trial"] = switch_trial
    task["distraction_present"] = distraction
    return task
