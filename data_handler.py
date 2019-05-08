import connection


def get_question(id):
    all_questions = connection.get_all_questions()

    for question in all_questions:
        if question['id'] == id:
            return question


def update_question_in_data(updated_question, id):
    all_questions = connection.get_all_questions()

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