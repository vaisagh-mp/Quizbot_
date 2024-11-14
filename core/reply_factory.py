from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST

def generate_bot_responses(message, session):
    bot_responses = []

    # Check if we are at the start of the quiz
    current_question_id = session.get("current_question_id")
    if current_question_id is None:
        # Start a new quiz, clear previous answers
        bot_responses.append(BOT_WELCOME_MESSAGE)
        session["current_question_id"] = 0
        session["answers"] = {}  # Clear previous answers
        session.save()
        
        # Retrieve the first question directly to display immediately
        first_question, first_question_id = get_next_question(-1)
        if first_question:
            bot_responses.append(first_question["question_text"])
            bot_responses.extend(first_question["options"])
            session["current_question_id"] = first_question_id
            session.save()
    else:
        # Record the user's answer and move to the next question
        success, error = record_current_answer(
            message, current_question_id, session
        )
        if not success:
            return [error]

        # Retrieve the next question
        next_question, next_question_id = get_next_question(current_question_id)
        if next_question:
            bot_responses.append(next_question["question_text"])
            bot_responses.extend(next_question["options"])
            session["current_question_id"] = next_question_id
            session.save()
        else:
            # End of the quiz
            final_response = generate_final_response(session)
            bot_responses.append(final_response)
            session["current_question_id"] = None
            session.save()

    return bot_responses

def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question in the session.
    '''
    if current_question_id is None:
        return False, "No question to answer."

    session["answers"] = session.get("answers", {})
    session["answers"][current_question_id] = answer
    session.save()

    return True, ""

def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    next_question_id = current_question_id + 1

    if next_question_id < len(PYTHON_QUESTION_LIST):
        return PYTHON_QUESTION_LIST[next_question_id], next_question_id
    else:
        return None, -1

def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    answers = session.get("answers", {})
    num_correct_answers = 0

    for question_id, answer in answers.items():
        question_id = int(question_id)
        correct_answer = PYTHON_QUESTION_LIST[question_id]['answer']
        if answer == correct_answer:
            num_correct_answers += 1

    total_questions = len(PYTHON_QUESTION_LIST)
    score_percentage = (num_correct_answers / total_questions) * 100

    final_response = f"Quiz completed!\nYou answered {num_correct_answers} out of {total_questions} questions correctly."
    final_response += f"\nYour score: {score_percentage:.2f}%"

    return final_response
