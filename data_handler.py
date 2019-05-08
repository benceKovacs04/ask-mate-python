import connection
import time


def get_question(id):
    all_questions = connection.get_all_data_from_file('sample_data/question.csv')

    for question in all_questions:
        if question['id'] == id:
            return question


def get_answer(id):
    all_answers = connection.get_all_data_from_file('sample_data/answer.csv')

    for answer in all_answers:
        if answer['id'] == id:
            return answer


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


def add_time_stamp():
    time_stamp = time.time()

    return round(time_stamp)


def generate_id(file_name):
    all_questions = connection.get_all_data_from_file(file_name)
    last_id = all_questions[-1]['id']
    new_id = int(last_id) + 1

    return new_id
