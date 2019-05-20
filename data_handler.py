import connection
from datetime import datetime


@connection.connection_handler
def get_all_questions(cursor):
    cursor.execute("""
                        SELECT title, id FROM question
                        ORDER BY submission_time DESC;
                       """)

    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def get_answers_to_question(cursor, question_id):
    cursor.execute("""
                            SELECT * FROM answer
                            WHERE question_id = %(question_id)s;
                               """,
                   {'question_id': question_id})

    answers = cursor.fetchall()
    return answers


@connection.connection_handler
def add_new_question_and_return_its_id(cursor, details):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql_query = """
                    INSERT INTO question (submission_time, view_number, vote_number, title, message, image) 
                    VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s)
                    RETURNING id"""

    cursor.execute(sql_query,
                   {'submission_time': dt,
                    'view_number': 0,
                    'vote_number': 0,
                    'title': details['title'],
                    'message': details['message'],
                    'image': details['image']})

    last_id = cursor.fetchall()

    return last_id[0]['id']



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

@connection.connection_handler
def delete_question(cursor, id):
    cursor.execute("""
                   DELETE FROM answer
                   WHERE question_id = %(id)s;
                           """,
                   {'id': id}
                   )

    cursor.execute("""
                   DELETE FROM question
                   WHERE id = %(id)s;
                   """,
                   {'id':id}
                   )



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




def generate_id(file_name):
    all_questions = connection.get_all_data_from_file(file_name)
    if len(all_questions) == 0:
        new_id = 0
    else:
        last_id = all_questions[-1]['id']
        new_id = int(last_id) + 1

    return new_id
