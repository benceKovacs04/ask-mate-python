import connection
import time


def get_question(id):
    all_questions = connection.get_all_data_from_file('sample_data/question.csv')

    for question in all_questions:
        if question['id'] == id:
            return question


def get_answers_to_question(question_id):
    all_answers = connection.get_all_data_from_file('sample_data/answer.csv')
    answers = []

    for answer in all_answers:
        if answer['question_id'] == question_id:
            answers.append(answer)
    return answers


def get_answer_by_id(question_id, answer_id):

    answers = get_answers_to_question(question_id)
    for answer in answers:
        if answer['id'] == answer_id:
            return answer


def update_entry_in_data(updated_data, file_name):
    all_data = connection.get_all_data_from_file(file_name)

    for index in range(len(all_data)):
        if all_data[index]['id'] == updated_data['id']:
            all_data[index] = updated_data
            break

    connection.write_to_csv(file_name, all_data)

def delete_question_from_data(question_to_delete):
    all_answers = connection.get_all_data_from_file('sample_data/answer.csv')
    question_id = question_to_delete['id']
    answers_to_delete = get_answers_to_question(question_id)

    for index in range(len(all_answers)):
        if all_answers[index] in answers_to_delete:
            del all_answers[index]

    connection.write_to_csv('sample_data/answer.csv', all_answers)

    all_questions = connection.get_all_data_from_file('sample_data/question.csv')

    for index in range(len(all_questions)):
        if all_questions[index]['id'] == question_to_delete['id']:
            del all_questions[index]
            break

    connection.write_to_csv('sample_data/question.csv', all_questions)


def show_question(id, voted):

    question = get_question(id)

    if voted:
        return question

    updated_question = increase_view_number(question)

    return updated_question


def increase_view_number(question):
    question['view_number'] = str(int(question['view_number']) + 1)
    update_entry_in_data(question, 'sample_data/question.csv')

    return question


def get_new_answer_id(question_id):
    question_answers = get_answers_to_question(question_id)
    if len(question_answers) != 0:
        new_id = str(int(question_answers[-1]['id']) + 1)
    else:
        new_id = 0

    return new_id


def add_time_stamp():
    time_stamp = time.time()

    return round(time_stamp)


def generate_id(file_name):
    all_questions = connection.get_all_data_from_file(file_name)
    if len(all_questions) == 0:
        new_id = 0
    else:
        last_id = all_questions[-1]['id']
        new_id = int(last_id) + 1

    return new_id
