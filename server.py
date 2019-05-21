from flask import Flask, render_template, redirect, request
import data_handler
import connection
import time

app = Flask(__name__)


@app.route('/')
@app.route('/list')
def route_list():
    if str(request.url_rule) == '/list':
        limit = None
    else:
        limit = 5

    order = request.args.get('order')
    order_dir = request.args.get('order_dir')
    if order and order_dir:
        all_questions = data_handler.get_all_questions(limit, order, order_dir)
    else:
        all_questions = data_handler.get_all_questions(limit)

    return render_template('list.html', questions=all_questions, limit=limit, order=order, order_dir=order_dir)


@app.route('/search', methods=["POST"])
def route_search():
    searched_question = request.form
    found_questions = data_handler.search_question(searched_question)

    return render_template('list.html', questions=found_questions)


@app.route('/question/<question_id>')
@app.route('/question/<question_id>/vote')
def route_question(question_id):
    url = request.url_rule
    question_details = data_handler.get_question_details(question_id)
    answers_to_question = data_handler.get_answers_to_question(question_id)

    if "vote" not in url.rule:
        data_handler.increase_view_number(question_id)

    return render_template('question_details.html', question=question_details, answers_to_question=answers_to_question)


@app.route('/add-question', methods=['GET', 'POST'])
def route_add_question():

    if request.method == 'POST':
        story_details = request.form
        new_question_id = data_handler.add_new_question_and_return_its_id(story_details)
        return redirect(f'/question/{new_question_id}')

    return render_template("add_question.html")


@app.route('/edit-question/<question_id>', methods=['GET', 'POST'])
def route_edit_question(question_id):
    if request.method == 'POST':
        updated_question = request.form
        data_handler.update_question(question_id, updated_question)

        return redirect(f'/question/{question_id}')

    question_to_edit = data_handler.get_question_details(question_id)
    return render_template('edit_question.html', question_to_edit=question_to_edit)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def route_new_answer(question_id):
    if request.method == 'POST':
        new_answer = request.form
        data_handler.add_new_answer(question_id, new_answer)

        return redirect(f'/question/{question_id}')

    return render_template('add_answer.html', question_id=question_id)


@app.route('/question/<question_id>/delete')
def route_delete_question(question_id):
    data_handler.delete_question(question_id)
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    else:
        return redirect('/')


@app.route('/question/<question_id>/edit-answer/<answer_id>')
def render_edit_answer_form(answer_id, question_id):
    answer_to_edit = data_handler.get_single_answer_by_id(answer_id)
    return render_template('edit_answer.html', answer_to_edit=answer_to_edit[0], question_id=question_id)


@app.route('/question/<question_id>/edit-answer/<answer_id>/editing', methods=['POST'])
def edit_answer(question_id, answer_id):
    updated_message = request.form.get('message')
    updated_image = request.form.get('image')
    data_handler.edit_answer(answer_id, updated_message, updated_image)

    return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/vote-up')
@app.route('/question/<question_id>/vote-down')
@app.route('/question/<question_id>/answer/<answer_id>/vote-up')
@app.route('/question/<question_id>/answer/<answer_id>/vote-down')
def voting(question_id, answer_id=None):
    url = request.url_rule
    vote = 0

    if "vote-up" in url.rule:
        vote = 1
    elif "vote-down" in url.rule:
        vote = -1

    if "answer" in url.rule:
        table = 'answer'
        data_handler.change_vote_number(table, vote, answer_id)

    elif "answer" not in url.rule:
        table = 'question'
        data_handler.change_vote_number(table, vote, question_id)

    return redirect(f'/question/{question_id}/vote')


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )