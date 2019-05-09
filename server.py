from flask import Flask, render_template, redirect, request
import data_handler
import connection
import time

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
@app.route('/list')
def route_list():
    all_questions = connection.get_all_data_from_file('sample_data/question.csv')

    return render_template('list.html', all_questions=all_questions)


@app.route('/question/<question_id>')
def route_question(question_id):
    question = data_handler.show_question(question_id)
    answers_to_question = data_handler.get_answers_to_question(question_id)

    return render_template('question_details.html', question=question, answers_to_question=answers_to_question)


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    file_name = 'sample_data/question.csv'
    id = data_handler.generate_id(file_name)
    time_stamp = data_handler.add_time_stamp()

    if request.method == 'POST':
        new_question = dict(request.form)
        question_id = new_question['id']
        connection.add_question(new_question, file_name)
        return redirect(f'/question/{question_id}')

    return render_template("add_question.html", id=id, time_stamp=time_stamp)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def route_new_answer(question_id):
    if request.method == 'GET':
        new_id = data_handler.get_new_answer_id(question_id)
        timestamp = time.time()

        return render_template('add_answer.html',question_id=question_id, new_id=new_id, timestamp=timestamp)

    if request.method == 'POST':
        new_answer = dict(request.form)

        connection.append_to_csv('sample_data/answer.csv', new_answer)

        return redirect(f'/question/{new_answer["question_id"] }')

@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    question_to_delete = data_handler.get_question(question_id)
    data_handler.delete_question_from_data(question_to_delete)

    return redirect('/')


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )