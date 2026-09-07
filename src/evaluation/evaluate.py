import json
from pathlib import Path
from datetime import datetime

from src.agent.search_agent import answer_question


BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / "questions.json"
RESULTS_DIRECTORY = BASE_DIR / "results"


def load_questions():
    """Read evaluation questions from the JSON file."""
    with QUESTIONS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def mock_answer_question(question):
    """
    Temporary fake backend response.

    Later, replace this with Member 2's real answer_question function.
    """
    return {
        "answer": "Temporary test answer",
        "search_steps": [
            {
                "round": 1,
                "query": question,
                "sources_found": 3,
                "status": "insufficient"
            },
            {
                "round": 2,
                "query": f"More information about: {question}",
                "sources_found": 2,
                "status": "sufficient"
            }
        ],
        "sources": [
            {
                "source": "sample-document.pdf",
                "page": 1
            }
        ]
    }


def evaluate_question(question_data):
    """Run one question and prepare a result record."""
    q_text = question_data.get("question", "")
    response = answer_question(q_text)

    return {
        "id": question_data.get("id", question_data.get("qid", q_text)),
        "question": q_text,
        "expected_answer": question_data.get("expected_answer"),
        "actual_answer": response.get("answer"),
        "search_steps": response.get("search_steps", []),
        "sources": response.get("sources", []),

        # These will initially be checked manually.
        "retrieval_score": None,
        "answer_score": None,
        "citation_score": None,
        "search_round_score": None,
        "failure_reason": None,
        "reviewer_notes": ""
    }


def save_results(results):
    """Save results without overwriting an earlier evaluation."""
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
        qid_display = question.get("id", question.get("qid", "<no-id>"))
        print(f"Testing {qid_display}: {question.get('question', '')}")
        result = evaluate_question(question)
        results.append(result)

    save_results(results)


if __name__ == "__main__":
    main()