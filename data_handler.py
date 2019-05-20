import connection
import time


@connection.connection_handler
def get_all_questions(cursor):
    cursor.execute("""
                        SELECT title, id FROM question
                        ORDER BY submission_time DESC;
                       """)

    questions = cursor.fetchall()
    return questions


def get_question(id):
    all_questions = connection.get_all_data_from_file('sample_data/question.csv')

    for question in all_questions:
        if question['id'] == id:
            return question


@connection.connection_handler
def get_answers_to_question(cursor, question_id):
    cursor.execute("""
                            SELECT * FROM answer
                            WHERE question_id = %(question_id)s;
                               """,
                   {'question_id': question_id})

    answers = cursor.fetchall()
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


@connection.connection_handler
def show_question(cursor, id):
    cursor.execute("""
                            SELECT * FROM question
                            WHERE id = %(id)s;
                           """,
                   {'id': id})

    question = cursor.fetchall()
    return question[0]


def get_new_answer_id(question_id):
    question_answers = connection.get_all_data_from_file('sample_data/answer.csv')
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
