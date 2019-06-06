create table accepted_answers
(
	question_id int
		constraint accepted_answers_question_id_fk
			references question
				on delete cascade,
	answer_id int
		constraint accepted_answers_answer_id_fk
			references answer
				on delete cascade
);

create unique index accepted_answers_answer_id_uindex
	on accepted_answers (answer_id);

create unique index accepted_answers_question_id_uindex
	on accepted_answers (question_id);