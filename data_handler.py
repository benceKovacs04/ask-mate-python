import connection
from datetime import datetime
from psycopg2 import sql
from flask import session


@connection.connection_handler
def get_all_questions(cursor, limit, order_by='submission_time', order_direction='DESC'):

    sql_query = """
                SELECT title, id FROM question
                ORDER BY {order_by} """

    if order_direction == "DESC":
        sql_query = sql_query + "DESC"
    else:
        sql_query = sql_query + "ASC"

    if limit:
        sql_query = sql_query + f" LIMIT {limit}"

    sql_query = sql.SQL(sql_query).format(order_by=sql.Identifier(order_by))
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
                    'message': searched_question})
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
                    INSERT INTO answer (submission_time, vote_number, question_id, message, image, user_id) 
                    VALUES (%(submission_time)s, %(vote_number)s, %(question_id)s, %(message)s, %(image)s, %(user_id)s)""",
                   {'submission_time': dt,
                    'vote_number': 0,
                    'question_id': question_id,
                    'message': new_answer['message'],
                    'image': new_answer['image'],
                    'user_id': session['userid']})


@connection.connection_handler
def increase_view_number(cursor, question_id):
    cursor.execute("""
                    UPDATE question 
                    SET view_number = view_number + 1
                    WHERE id = %(question_id)s""",
                   {'question_id': question_id})


@connection.connection_handler
def change_vote_number(cursor, target_table, vote_direction, id):
    vote = 0

    if vote_direction == 'up':
        vote = 1
    elif vote_direction == 'down':
        vote = -1

    cursor.execute(
        sql.SQL("update {target_table} set vote_number = vote_number + %(vote)s WHERE id = %(id)s").
            format(target_table=sql.Identifier(str(target_table))), {'vote': vote, 'id': id})


@connection.connection_handler
def delete_answer(cursor, answer_id):
    sql_query = """
                DELETE FROM answer
                WHERE id = %(answer_id)s"""

    cursor.execute(sql_query,
                   {'answer_id': answer_id})


@connection.connection_handler
def edit_answer(cursor, answer_id, message, image):
    cursor.execute("""
                    UPDATE answer
                    SET message = %(message)s, image = %(image)s
                    WHERE id = %(answer_id)s""",
                   {'message': message,
                    'image': image,
                   'answer_id': answer_id})


def get_tag_name_by_question_id(question_id):
    tag_ids_dict = get_question_tag_ids(question_id)
    tag_ids_list = [tag['tag_id'] for tag in tag_ids_dict]
    question_tags = get_question_tag_names(tag_ids_list)

    return question_tags


@connection.connection_handler
def get_all_question_tags(cursor):
    cursor.execute("""
                    SELECT name FROM tag""")

    all_tags = cursor.fetchall()
    return all_tags


@connection.connection_handler
def get_question_tag_ids(cursor, question_id):
    cursor.execute("""
                    SELECT tag_id FROM question_tag
                    WHERE question_id=%(question_id)s""",
                   {'question_id': question_id})

    tag_ids = cursor.fetchall()
    return tag_ids


@connection.connection_handler
def get_question_tag_names(cursor, tag_ids):
    cursor.execute("""
                    SELECT name FROM tag
                    WHERE id = ANY(%(tag_ids)s)""",
                   {'tag_ids': tag_ids})

    question_tags = cursor.fetchall()
    return question_tags


@connection.connection_handler
def add_new_tag(cursor, new_tag):
    cursor.execute("""
                    INSERT INTO tag (name)
                    VALUES (%(new_tag)s)""",
                   {'new_tag': new_tag})


@connection.connection_handler
def check_if_tag_exists(cursor, tag_name):
    """
    This function checks whether a potentially new tag already exists (by name).
    :return: True if it exists, False if it doesn't
    """
    cursor.execute("""
                    SELECT id FROM tag
                    WHERE name = %(tag_name)s""",
                   {'tag_name': tag_name})

    tag_id = cursor.fetchall()

    if tag_id:
        return True
    else:
        return False


@connection.connection_handler
def get_tag_id_from_tag_table(cursor, tag_names):
    """
    This function recieves tag names and returns the IDs of the corresponding
    tags, so they can be added to question_tag table
    :return:
    """
    cursor.execute("""
                    SELECT id FROM tag
                    WHERE name = ANY(%(tag_names)s)""",
                   {'tag_names': tag_names})

    ids = cursor.fetchall()

    return ids


@connection.connection_handler
def add_new_question_tag(cursor, question_id, tag_ids):
    cursor.execute("""
                    INSERT INTO question_tag (question_id, tag_id)
                    VALUES (%(question_id)s, unnest(%(tag_ids)s))""",
                   {'question_id': question_id,
                    'tag_ids': tag_ids})


@connection.connection_handler
def save_registration(cursor, username, hashed_password):
    sql_query = """
                INSERT INTO users (username, pw_hash)
                VALUES (%(username)s, %(hashed_pw)s)"""
    sql_values = {
                'username': username,
                'hashed_pw': hashed_password
    }

    cursor.execute(sql_query, sql_values)

@connection.connection_handler
def get_hashed_pw(cursor, username):
    sql_query = """
                SELECT id, pw_hash FROM users
                WHERE username = %(username)s"""

    cursor.execute(sql_query,
                   {'username': username})

    return cursor.fetchall()



def add_question_tag_handler(question_id, tags_from_form):
    """
    When we add a tag to a question we can add an existing tag to it and/or
    define a new one.
    This function separates the user input then handles SQL insert calls with the right
    parameters

    :param question_id: The ID of the question where the added tags belong
    :param tags_from_form: The tags we get from the request.form
    :return: Nothing
    """
    new_tag = tags_from_form['new_tag']

    if new_tag:
        if not check_if_tag_exists(new_tag):
            add_new_tag(tags_from_form['new_tag'])

    # I need to create a list of values here
    tags_to_add_to_question_tags = []
    for tag in tags_from_form.values():
        if tag != '':
            tags_to_add_to_question_tags.append(tag)

    # I need to create a list of values here
    ids_of_names = get_tag_id_from_tag_table(tags_to_add_to_question_tags)
    ids_to_insert_to_question_tag = []
    for tag in ids_of_names:
        ids_to_insert_to_question_tag.append(tag['id'])


    add_new_question_tag(question_id, ids_to_insert_to_question_tag)



