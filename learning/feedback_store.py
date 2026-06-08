import json
from pathlib import Path
from datetime import datetime


FEEDBACK_FILE = Path("learning/feedback.json")


class FeedbackStore:
    def __init__(self):
        FEEDBACK_FILE.parent.mkdir(exist_ok=True)

        if not FEEDBACK_FILE.exists():
            FEEDBACK_FILE.write_text("[]", encoding="utf-8")

    def add_feedback(self, text: str):
        data = self.get_feedback()

        data.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "feedback": text
        })

        FEEDBACK_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def get_feedback(self) -> list:
        try:
            return json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []

    def get_feedback_text(self) -> str:
        feedback = self.get_feedback()

        if not feedback:
            return "Пока пользовательских исправлений нет."

        return "\n".join(
            [f'- {item["time"]}: {item["feedback"]}' for item in feedback[-20:]]
        )