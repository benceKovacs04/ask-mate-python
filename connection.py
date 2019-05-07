import csv

def get_all_questions(file_name):
    with open(file_name, "r") as file:
        all_questions = list(csv.DictReader(file))

    return all_questions