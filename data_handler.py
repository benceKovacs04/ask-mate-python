import csv

field = ['id','submission_time','view_number','vote_number','title','message','image']


def get_all_questions():
    with open("sample_data/question.csv", "r") as file:
        all_questions = list(csv.DictReader(file))

    return all_questions


def get_question(all_questions, id):
    for question in all_questions:
        if question['id'] == id:
            return question