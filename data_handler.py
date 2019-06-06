import connection
from datetime import datetime
from psycopg2 import sql
from flask import session


@connection.connection_handler
def get_all_questions(cursor, limit, order_by='submission_time', order_direction='DESC'):

    sql_query = """
                SELECT title, id, user_id FROM question
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
def get_selected_answer(cursor, question_id):
    sql_query = """
                SELECT * FROM accepted_answers
                WHERE question_id = %(question_id)s"""

    cursor.execute(sql_query,
                   {'question_id': question_id})

    return cursor.fetchone()


@connection.connection_handler
def get_single_answer_by_id(cursor, id):
    cursor.execute("""
                    SELECT * FROM answer
                    WHERE id = %(id)s;
                    """,
                    {'id': id})

    answers = cursor.fetchone()
    return answers


@connection.connection_handler
def add_new_question_and_return_its_id(cursor, details):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql_query = """
                    INSERT INTO question (submission_time, view_number, vote_number, title, message, image, user_id) 
                    VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s, %(user_id)s)
                    RETURNING id"""

    cursor.execute(sql_query,
                   {'submission_time': dt,
                    'view_number': 0,
                    'vote_number': 0,
                    'title': details['title'],
                    'message': details['message'],
                    'image': details['image'],
                    'user_id': int(session['userid'])
                    })

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
def get_question_details(cursor, question_id):
    cursor.execute("""
                    SELECT question.*, users.username FROM question
                    LEFT JOIN users on question.user_id=users.id
                    WHERE question.id = %(question_id)s;
                           """,
                   {'question_id': question_id
                    })

    question = cursor.fetchall()
    return question[0]


@connection.connection_handler
def add_new_answer(cursor, question_id, new_answer):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
                    INSERT INTO answer (submission_time, vote_number, question_id, message, image, user_id) 
                    VALUES (%(submission_time)s, %(vote_number)s, %(question_id)s, %(message)s, %(image)s, %(user_id)s)
                    """,
                   {'submission_time': dt,
                    'vote_number': 0,
                    'question_id': question_id,
                    'message': new_answer['message'],
                    'image': new_answer['image'],
                    'user_id': session['userid']
                    })


@connection.connection_handler
def increase_view_number(cursor, question_id):
    cursor.execute("""
                    UPDATE question 
                    SET view_number = view_number + 1
                    WHERE id = %(question_id)s""",
                   {'question_id': question_id})


@connection.connection_handler
def change_reputation(cursor, entity, vote_direction, entity_id):
    if vote_direction == 'up':
        if entity == 'question':
            reputation_change = 5
        elif entity == 'answer':
            reputation_change = 10
    elif vote_direction == 'down':
        reputation_change = -2

    user_id_dict = get_user_id_of_owner_of_entity(entity, entity_id)

    user_id_of_owner = int(user_id_dict['user_id'])

    cursor.execute("""
                    UPDATE users
                    SET reputation = reputation + %(reputation_change)s
                    WHERE id = %(user_id_of_owner)s
                    """,
                    {'reputation_change': reputation_change,
                     'user_id_of_owner': user_id_of_owner})


@connection.connection_handler
def get_user_id_of_owner_of_entity(cursor, entity, entity_id):
    sql_query = """
                SELECT user_id
                FROM {entity}
                """

    sql_query = sql_query + f" WHERE id = {entity_id}"

    sql_query = sql.SQL(sql_query).format(entity=sql.Identifier(entity))

    cursor.execute(sql_query)
    user_id = cursor.fetchone()

    return user_id


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

@connection.connection_handler
def get_tag_name_by_question_id(cursor, question_id):
    sql_query = """
                SELECT name FROM tag
                JOIN question_tag ON question_tag.tag_id = tag.id
                WHERE question_id = %(question_id)s"""

    cursor.execute(sql_query,
                   {'question_id': question_id})

    return cursor.fetchall()


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
def get_tag_id(cursor, tag_name):
    """
    This function recieves a tag name and returns the ID of the corresponding
    tag, so it can be added to question_tag table
    :return:
    """
    cursor.execute("""
                    SELECT id FROM tag
                    WHERE name = %(tag_name)s""",
                   {'tag_name': tag_name})

    tag_id = cursor.fetchone()

    return tag_id['id']


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

    return cursor.fetchone()


@connection.connection_handler
def get_all_user(cursor):
    cursor.execute("""
                    SELECT username, id
                    FROM users
                    """)

    all_user = cursor.fetchall()

    return all_user


@connection.connection_handler
def save_accepted_answer(cursor, question_id, answer_id):
    sql_query = """
                INSERT INTO accepted_answers 
                VALUES (%(question_id)s, %(answer_id)s)"""

    cursor.execute(sql_query,
                   {'question_id': question_id,
                    'answer_id': answer_id})


@connection.connection_handler
def delete_accepted_answer(cursor, question_id, answer_id):
    sql_query = """
                DELETE FROM accepted_answers
                WHERE question_id = %(question_id)s AND
                answer_id = %(answer_id)s"""

    cursor.execute(sql_query,
                   {'question_id': question_id,
                    'answer_id': answer_id})


@connection.connection_handler
def add_tag_to_question(cursor, question_id, tag_name):
    tag_id = get_tag_id(tag_name)
    sql_query = """
                INSERT INTO question_tag
                VALUES (%(question_id)s, %(tag_id)s)"""

    cursor.execute(sql_query,
                   {'question_id': question_id,
                    'tag_id': tag_id})

@connection.connection_handler
def save_new_tag(cursor, new_tag_name):
    sql_query = """
                INSERT INTO tag (name)
                VALUES (%(new_tag_name)s)"""

    cursor.execute(sql_query,
                   {'new_tag_name': new_tag_name})

@connection.connection_handler
def get_user_activities(cursor, user_id):
    sql_query = """
                SELECT question.title, question.id
                FROM question
                """
    sql_query = sql_query + f" WHERE question.user_id = {user_id}"
    sql_query = sql.SQL(sql_query).format(user_id=sql.Identifier(user_id))
    cursor.execute(sql_query)
    user_questions = cursor.fetchall()

    sql_query = """
                    SELECT answer.message, answer.id
                    FROM answer
                    """
    sql_query = sql_query + f" WHERE answer.user_id = {user_id}"
    sql_query = sql.SQL(sql_query).format(user_id=sql.Identifier(user_id))
    cursor.execute(sql_query)
    user_answers = cursor.fetchall()

    user_activities = {'questions': user_questions, 'answers': user_answers}

    return user_activities


@connection.connection_handler
def get_user_reputation(cursor, user_id):
    cursor.execute("""
                    SELECT reputation
                    FROM users
                    WHERE id = %(user_id)s
                    """,
                   {'user_id': user_id})

    user_reputation = cursor.fetchone()
    user_reputation = user_reputation['reputation']

    return user_reputation