from flask import Flask, render_template, redirect, request, url_for
import data_handler


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
def route_question(question_id):
    voted = request.args.get('voted')

    if voted != 'yes':
        data_handler.increase_view_number(question_id)

    question_details = data_handler.get_question_details(question_id)
    answers_to_question = data_handler.get_answers_to_question(question_id)

    tag_ids_dict = data_handler.get_question_tag_ids(question_id)
    tag_ids_list = [tag['tag_id'] for tag in tag_ids_dict]
    question_tags = data_handler.get_question_tag_names(tag_ids_list)

    return render_template('answers.html',
                           question=question_details,
                           answers_to_question=answers_to_question,
                           question_tags=question_tags)


@app.route('/question/<question_id>/voting')
@app.route('/question/<question_id>/answer/<answer_id>/voting')
def voting(question_id, answer_id=None):
    target_table = request.args.get('target')
    vote_direction = request.args.get('direction')

    if target_table == 'question':
        entity_id = question_id
    elif target_table == 'answer':
        entity_id = answer_id

    data_handler.change_vote_number(target_table, vote_direction, entity_id)

    return redirect(f'/question/{question_id}?voted=yes')


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def route_new_tag(question_id):
    if request.method == 'POST':
        form_values = request.form
        try:
            data_handler.add_question_tag_handler(question_id, form_values)
        except:
            pass
        return redirect(f'/question/{question_id}')

    tag_ids_dict = data_handler.get_question_tag_ids(question_id)
    tag_ids_list = [tag['tag_id'] for tag in tag_ids_dict]
    question_tags = data_handler.get_question_tag_names(tag_ids_list)
    all_question_tags = data_handler.get_all_question_tags()

    question = data_handler.get_question_details(question_id)

    return render_template('add_new_tag.html', question_tags=question_tags, all_question_tags = all_question_tags, question=question)


@app.route('/add-question')
def route_new_question():
    return render_template("add_question.html")


@app.route('/add-question', methods=['POST'])
def route_create_question():
    story_details = request.form
    new_question_id = data_handler.add_new_question_and_return_its_id(story_details)
    return redirect(f'/question/{new_question_id}')


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



if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )