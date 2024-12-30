
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if current_question_id is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)
        session["active"] = False

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses

def record_current_answer(answer, current_question_id, session):

    if current_question_id is None:
        if session.get("active"):
            return True, ""
        return False, "No more questions. Please reset."

    question = PYTHON_QUESTION_LIST[current_question_id]
    correct_answer = question.get("answer")

    user_answers = session.get("user_answers", {})
    user_answers[current_question_id] = {
        "user_answer": answer,
        "is_correct": answer.strip().lower() == correct_answer.strip().lower()
    }
    session["user_answers"] = user_answers
    session.save()

    return True, ""

def get_next_question(current_question_id):

    if current_question_id is None:
        next_question_id = 0
    else:
        next_question_id = current_question_id + 1

    if next_question_id < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_question_id]["question_text"]
        return next_question, next_question_id
    else:
        return None, None

def generate_final_response(session):

    user_answers = session.get("user_answers", {})
    total_questions = len(PYTHON_QUESTION_LIST)

    if not user_answers:
        return "You haven't answered any questions yet."

    correct_answers = sum(1 for ans in user_answers.values() if ans["is_correct"])

    return f"You've completed the quiz! \nYou answered {correct_answers}/{total_questions} questions correctly."
