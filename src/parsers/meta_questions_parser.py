import re
from typing import List
import pandas
from cloudant_models.question import Question
from cloudant_models.option import Option
from intermediate_models.meta_question import MetaQuestion


def parse_excel_to_meta_questions(args) -> List[MetaQuestion]:
    file = args.excel_file[0]
    excel_data_df = pandas.read_excel(file, sheet_name='Questions')

    question_list = []
    for index, row in excel_data_df.iterrows():
        if pandas.notna(row['*Reference ID (<Exercise Ref. ID>.<order in the exercise, 01-99>)']):
            reference_id = row['*Reference ID (<Exercise Ref. ID>.<order in the exercise, 01-99>)']
            description = row['*Description']
            image_url = row['Image URL']
            option_header = row[
                'Option Header to Be Displayed (leave blank to use the default text, "Please select your answer:")']
            options = create_options(row)
            answer = create_answer(row['*Answer'], options)
            feedback_for_correct_answer = row['*Feedback for Correct Answer']
            feedback_for_incorrect_answer = row['*Feedback for Incorrect Answer']

            q = Question(
                description,
                image_url,
                option_header,
                options,
                answer,
                feedback_for_correct_answer,
                feedback_for_incorrect_answer,
                reference_id)

            mq = MetaQuestion(reference_id, q)

            question_list.append(mq)

    question_list.sort(reverse=False, key=return_ref_id)
    return question_list


def create_question(subject_name, uuid, row) -> Question:
    # res = get_cloudant_uuids(1)
    # print(res)
    options = create_options(row)
    answer_option = create_answer(row[7], options)
    question = Question(
        _id=subject_name + "-question:" + uuid,
        questionId=row[0],
        docType='question',
        description=row[1],
        imageUrl=row[2],
        optionHeader="Please select your answer:",
        options=options,
        answer=answer_option,
        feedbackForCorrectAnswer=row[8],
        feedbackForIncorrectAnswer=row[9]
    )
    print(question)
    return question


def create_options(row) -> List[Option]:
    option_list = list(filter(pandas.notna, [row.iloc[4], row.iloc[5], row.iloc[6], row.iloc[7]]))
    options = []
    for i in range(len(option_list)):
        option_value = str(option_list[i]).strip()
        o = Option("A", remove_question_label(option_value))
        if i == 1:
            o.label = "B"
        elif i == 2:
            o.label = "C"
        elif i == 3:
            o.label = "D"
        options.append(o)
    return options


def create_answer(answer_str, options=List[Option]) -> Option:
    answer_option = options[0]
    if answer_str == 'B':
        answer_option = options[1]
    elif answer_str == 'C':
        answer_option = options[2]
    elif answer_str == 'D':
        answer_option = options[3]
    return answer_option


def remove_question_label(question: str) -> str:
    match = re.search("^[A,B,C,D]\)", question)
    if match:
        # print("match found")
        question = question[3:]
    # else:
        # print("match not found")
    return question


def get_reference_id_from_question_id(question_id) -> str:
    question_id = str(question_id)
    question_id_list = question_id.split('.')
    return question_id_list[0] + '.' + question_id_list[1]


def return_ref_id(q: MetaQuestion):
    return q.reference_id
