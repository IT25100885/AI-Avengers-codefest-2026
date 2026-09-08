import json
from datetime import datetime
from pathlib import Path

from src.agent.search_agent import answer_question


BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / "questions.json"
RESULTS_DIRECTORY = BASE_DIR / "results"


def load_questions():
    """Load evaluation questions from questions.json."""
    with QUESTIONS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_question(question_data):
    """Run one evaluation question through the real reasoning agent."""
    question_text = question_data.get("question", "")

    response = answer_question(question_text)

    return {
        "id": question_data.get(
            "id",
            question_data.get("qid", question_text)
        ),
        "question": question_text,
        "expected_answer": question_data.get("expected_answer"),
        "actual_answer": response.get("answer"),
        "search_steps": response.get("search_steps", []),
        "sources": response.get("sources", []),

        # Final scores are reviewed manually.
        "retrieval_score": None,
        "answer_score": None,
        "citation_score": None,
        "search_round_score": None,

        # Fill these after reviewing the result.
        "failure_reason": None,
        "reviewer_notes": ""
    }


def save_results(results):
    """Save evaluation results without overwriting previous runs."""
    RESULTS_DIRECTORY.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_DIRECTORY / f"evaluation_{timestamp}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    print(f"Evaluation completed: {output_file}")


def main():
    questions = load_questions()
    results = []

    for question in questions:
        question_id = question.get(
            "id",
            question.get("qid", "<no-id>")
        )

        print(
            f"Testing {question_id}: "
            f"{question.get('question', '')}"
        )

        result = evaluate_question(question)
        results.append(result)

    save_results(results)


if __name__ == "__main__":
    main()