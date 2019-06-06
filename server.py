from flask import Flask, render_template, redirect, request, session, flash, url_for
import data_handler
import utility


app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
@app.route('/list')
def route_list():
    if str(request.url_rule) == '/':
        limit = 5
    else:
        limit = None

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
    selected_answer = data_handler.get_selected_answer(question_id)

    question_tags = data_handler.get_tag_name_by_question_id(question_id)

    return render_template('answers.html',
                           question=question_details,
                           answers_to_question=answers_to_question,
                           question_tags=question_tags,
                           selected_answer=selected_answer)


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
    data_handler.change_reputation(target_table, vote_direction, entity_id)

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

    question_tags = data_handler.get_tag_name_by_question_id(question_id)
    all_question_tags = data_handler.get_all_question_tags()
    question = data_handler.get_question_details(question_id)

    return render_template('add_new_tag.html', question_tags=question_tags, all_question_tags = all_question_tags, question=question)


@app.route('/add-question')
def route_new_question():
    return render_template("add_question.html", title='add new question')


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
    return render_template('edit_question.html', question_to_edit=question_to_edit, title='edit question')


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def route_new_answer(question_id):
    try:
        if session['username']:
            if request.method == 'POST':
                new_answer = request.form
                data_handler.add_new_answer(question_id, new_answer)

                return redirect(f'/question/{question_id}')

            return render_template('add_answer.html', question_id=question_id, title='add new answer')
    except KeyError:
        return redirect(url_for('route_list'))


@app.route('/delete-answer/<answer_id>')
def route_delete_answer(answer_id):
    try:
        answer_to_delete = data_handler.get_single_answer_by_id(answer_id)
        if session['username'] and session['userid'] == answer_to_delete['user_id']:
            referrer = request.referrer
            data_handler.delete_answer(answer_id)

            return redirect(referrer)
        else:
            return url_for('route_list')
    except KeyError:
        return redirect(url_for('route_list'))


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
    try:
        answer_to_edit = data_handler.get_single_answer_by_id(answer_id)
        if session['username'] and session['userid'] == answer_to_edit['user_id']:
            return render_template('edit_answer.html', answer_to_edit=answer_to_edit, question_id=question_id, title='edit answer')
        else:
            return redirect(url_for('route_list'))
    except KeyError:
        return redirect(url_for('route_list'))


@app.route('/question/<question_id>/edit-answer/<answer_id>/editing', methods=['POST'])
def edit_answer(question_id, answer_id):
    answer_to_update = data_handler.get_single_answer_by_id(answer_id)
    if session['username'] and session['userid'] == answer_to_update['user_id']:
        updated_message = request.form.get('message')
        updated_image = request.form.get('image')
        data_handler.edit_answer(answer_id, updated_message, updated_image)

        return redirect(f'/question/{question_id}')
    else:
        return redirect(url_for('route_list'))


@app.route('/registration')
def route_registration():
    return render_template('registration_template.html')


@app.route('/registration', methods=['POST'])
def route_register_user():
    username = request.form['username']
    password = request.form['password']
    username2 = request.form['username2']
    password2 = request.form['password2']
    if username == username2 and password == password2:
        hashed_password = utility.hash_password(password)
        try:
            data_handler.save_registration(username, hashed_password)
        except:
            return render_template('registration_template.html', invalid_username=True, background_color="e53935")

        return redirect('/')
    else:
        return render_template('registration_template.html', not_matching=True, background_color="e53935")


@app.route('/login', methods=['POST'])
def route_login():
    referrer = request.referrer
    try:
        userinput_username = request.form['username']
        userinput_password = request.form['password']
        user_to_verify = data_handler.get_hashed_pw(userinput_username)
        verify_user = utility.verify_password(userinput_password, user_to_verify['pw_hash'])
        if verify_user:
            session['userid'] = user_to_verify['id']
            session['username'] = userinput_username
            return redirect(referrer)
        else:
            flash("Invalid username/password")
            return redirect(referrer)
    except (TypeError, NameError) as error:
        print(error)
        flash("Username and password fields cannot be empty!")
        return redirect(referrer)


@app.route('/logout')
def route_logout():
    referrer = request.referrer
    session.clear()
    return redirect(referrer)


@app.route('/list_all_users')
def render_all_users():
    all_user_and_id = data_handler.get_all_user()

    return render_template('all_user.html', all_user=all_user_and_id)


@app.route('/user/<user_id>')
def render_user_profile(user_id):
    user_activities = data_handler.get_user_activities(user_id)
    user_reputation = data_handler.get_user_reputation(user_id)

    return render_template('user_profile.html',
                           user_activities=user_activities,
                           user_reputation=user_reputation)


@app.route('/accept-answer/<question_id>/<answer_id>')
def route_accept_answer(question_id, answer_id):
    question = data_handler.get_question_details(question_id)
    referrer = request.referrer
    try:
        if question['user_id'] == session['userid']:
            try:
                data_handler.save_accepted_answer(int(question_id), int(answer_id))
            except:
                flash("You are not allowed to do that :)")
                return redirect(referrer)

            return redirect(referrer)
        else:
            flash("It's not your question")
            return redirect(url_for('route_list'))
    except KeyError:
        flash("It's not your question")
        return redirect(referrer)

@app.route('/delete-accepted-answer/<question_id>/<answer_id>')
def route_delete_accepted_answer(question_id, answer_id):
    referrer = request.referrer
    question = data_handler.get_question_details(question_id)
    try:
        if question['user_id'] == session['userid']:
            data_handler.delete_accepted_answer(int(question_id), int(answer_id))
    except KeyError:
        flash("It's not your question")
        return redirect(url_for('route_list'))
    return redirect(referrer)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )