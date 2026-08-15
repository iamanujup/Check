import io

LETTERS = "abcdefghijklmnopqrstuvwxyz"


def format_quiz(questions):
    out = []

    for n, q in enumerate(questions, 1):
        out.append(f"{n}. {q.get('question', '')}\n")

        for i, option in enumerate(q.get("options", [])):
            label = LETTERS[i] if i < len(LETTERS) else str(i + 1)
            mark = " ✅" if i == q.get("correct", -1) else ""
            out.append(f"({label}) {option}{mark}\n")

        explanation = q.get("explanation", "")
        if explanation:
            out.append(f"Ex: {explanation}\n")

        out.append("\n")

    return "".join(out)


def make_txt(text, filename):
    bio = io.BytesIO(text.encode("utf-8"))
    bio.name = filename
    return bio
