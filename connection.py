import csv

HEADER = ['id','submission_time','view_number','vote_number','title','message','image']


def get_all_questions():
    with open('sample_data/question.csv', "r") as file:
        all_questions = list(csv.DictReader(file))

    return all_questions


def write_to_csv(file_name, data):
    with open(file_name, "w") as file:
        dict_writer = csv.DictWriter(file, HEADER)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def add_question():
    pass