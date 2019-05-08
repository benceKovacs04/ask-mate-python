import csv

HEADER = ['id','submission_time','view_number','vote_number','title','message','image']

def get_all_data_from_file(file_name):
    with open(file_name, "r") as file:
        all_data = list(csv.DictReader(file))

    return all_data

def write_to_csv(file_name, data):
    #writeable_format = []
    #writeable_format.append(data)      this two line needed if the input data is just 1 dictionary

    with open(file_name, "w") as file:
        dict_writer = csv.DictWriter(file, HEADER)
        dict_writer.writeheader()
        dict_writer.writerows(data)
