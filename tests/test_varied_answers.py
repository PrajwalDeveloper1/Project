import random

from app import local_resume_chat_answer


def test_summary_answer_uses_variation_pool():
    random.seed(0)
    answer = local_resume_chat_answer(
        "rewrite my summary",
        "Senior product designer with 5 years of UX and design systems experience.",
        "Product designer for a B2B SaaS team.",
    )

    valid_answers = {
        "Your summary can feel sharper when it leads with your role, the value you create, and the kind of problems you solve.",
        "A concise summary works best when it names the role, your specialty, and the measurable impact you produce.",
        "The strongest summary connects your specialty, your target scope, and the outcomes you deliver in plain language.",
    }

    assert answer in valid_answers
