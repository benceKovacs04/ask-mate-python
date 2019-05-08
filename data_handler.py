import connection


def get_question(id):
    all_questions = connection.get_all_data_from_file('sample_data/question.csv')

    for question in all_questions:
        if question['id'] == id:
            return question

def get_answers_to_question(question_id):
    all_answers = connection.get_all_data_from_file('sample_data/answer.csv')
    answers = []

    for answer in all_answers:
        print(answer)
        print(answer['message'])
        if answer['question_id'] == question_id:
            answers.append(answer)

    return answers


def update_question_in_data(updated_question, id):
    all_questions = connection.get_all_data_from_file('sample_data/question.csv')

    for index in range(len(all_questions)):
        if all_questions[index]['id'] == updated_question['id']:
            all_questions[index] = updated_question
            break

    connection.write_to_csv('sample_data/question.csv', all_questions)



def show_question(id):
    question = get_question(id)
    question['view_number'] = str(int(question['view_number']) + 1)
    update_question_in_data(question, id)

    return question

def show_answer(id):
    answer =get_answer(id)