from flask import Flask, render_template, redirect, request
import data_handler
import connection

app = Flask(__name__)


@app.route('/')
@app.route('/list')
def route_list():
    all_questions = connection.get_all_questions()

    return render_template('list.html', all_questions=all_questions)


@app.route('/question/<question_id>')
def route_question(question_id):
    question = data_handler.show_question(question_id)

    return render_template('question_details.html', question=question)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )