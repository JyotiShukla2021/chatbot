
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
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

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    try:
        # Get the current question from the list
        current_question = PYTHON_QUESTION_LIST[current_question_id]

        # Validate the answer (example: checking if it matches expected answers)
        if answer not in current_question.get("options", []):
            return False, f"Invalid answer. Please choose one of {current_question['options']}."

        # Store the answer in the session
        user_answers = session.get("user_answers", {})
        user_answers[current_question_id] = answer
        session["user_answers"] = user_answers
        session.save()

        return True, ""
    except IndexError:
        return False, "Invalid question ID."


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''

    try:
        # Move to the next question
        next_question_id = current_question_id + 1

        # Check if the next question exists
        if next_question_id < len(PYTHON_QUESTION_LIST):
            next_question = PYTHON_QUESTION_LIST[next_question_id]["question"]
            return next_question, next_question_id
        else:
            # No more questions left
            return None, None
    except IndexError:
        return None, None



def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''

    user_answers = session.get("user_answers", {})
    score = 0

    # Calculate the score by comparing user answers with correct answers
    for question_id, answer in user_answers.items():
        correct_answer = PYTHON_QUESTION_LIST[question_id].get("correct_answer")
        if answer == correct_answer:
            score += 1

    # Generate the final result message
    total_questions = len(PYTHON_QUESTION_LIST)
    return f"Quiz completed! Your score: {score}/{total_questions}."
