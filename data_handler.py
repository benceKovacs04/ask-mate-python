import connection
from datetime import datetime
from psycopg2 import sql


@connection.connection_handler
def get_all_questions(cursor, limit, order_by='submission_time', order_direction='DESC'):
    if limit is None:
        sql_query = f"""
                    SELECT title, id FROM question
                    ORDER BY {order_by} {order_direction}"""
        cursor.execute(sql_query)
    else:
        sql_query = f"""
                    SELECT title, id FROM question
                    ORDER BY {order_by} {order_direction}
                    LIMIT {limit}
                    """
        cursor.execute(sql_query)

    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def get_latest_questions(cursor):
    cursor.execute("""
                   SELECT title, id FROM question
                   """)


@connection.connection_handler
def search_question(cursor, searched_question):
    searched_question = '%' + searched_question['search'] + '%'
    cursor.execute("""
                   SELECT title, id FROM question
                   WHERE title LIKE %(title)s
                   OR message LIKE %(message)s;
                   """,
                   {'title': searched_question,
                    'message': searched_question}
                    )
    found_questions = cursor.fetchall()
    return found_questions


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
def get_single_answer_by_id(cursor, id):
    cursor.execute("""
                    SELECT * FROM answer
                    WHERE id = %(id)s;
                    """,
                    {'id': id})

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


@connection.connection_handler
def update_question(cursor, question_id, updated_details):
    cursor.execute("""
                   UPDATE question
                   SET title = %(title)s, message = %(message)s, image = %(image)s
                   WHERE id = %(question_id)s;    
                   """,
                   {'title': updated_details['title'],
                    'message': updated_details['message'],
                    'image': updated_details['image'],
                    'question_id': question_id}
                   )


@connection.connection_handler
def delete_question(cursor, id):
    cursor.execute("""
                       DELETE FROM question_tag
                       WHERE question_id = %(id)s;
                               """,
                   {'id': id}
                   )

    cursor.execute("""
                    DELETE FROM comment
                    WHERE question_id = %(id)s;
                                   """,
                   {'id': id}
                   )

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
def get_question_details(cursor, id):
    cursor.execute("""
                    SELECT * FROM question
                    WHERE id = %(id)s;
                           """,
                   {'id': id})

    question = cursor.fetchall()
    return question[0]


@connection.connection_handler
def add_new_answer(cursor, question_id, new_answer):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
                    INSERT INTO answer (submission_time, vote_number, question_id, message, image) 
                    VALUES (%(submission_time)s, %(vote_number)s, %(question_id)s, %(message)s, %(image)s)""",
                   {'submission_time': dt,
                    'vote_number': 0,
                    'question_id': question_id,
                    'message': new_answer['message'],
                    'image': new_answer['image']})


@connection.connection_handler
def increase_view_number(cursor, question_id):
    cursor.execute("""
                    UPDATE question 
                    SET view_number = view_number + 1
                    WHERE id = %(question_id)s""",
                   {'question_id': question_id})


@connection.connection_handler
def change_vote_number(cursor, table, vote, id):

    cursor.execute(
        sql.SQL("update {table} set vote_number = vote_number + %(vote)s WHERE id = %(id)s").
            format(table=sql.Identifier(str(table))), {'vote': vote, 'id': id})


@connection.connection_handler
def edit_answer(cursor, answer_id, message, image):
    cursor.execute("""
                    UPDATE answer
                    SET message = %(message)s, image = %(image)s
                    WHERE id = %(answer_id)s""",
                   {'message': message,
                    'image': image,
                   'answer_id': answer_id})