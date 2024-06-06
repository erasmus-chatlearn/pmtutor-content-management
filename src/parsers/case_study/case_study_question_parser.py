import pandas as pd
from utilities.regex_utilities import get_a_matching_column_name_by_regex
from cloudant_models.question_v2 import QuestionV2
from cloudant_models.option_without_annotation import OptionWithoutAnnotation
from parsers.parser_utilities import get_doc_ids_by_their_spreadsheet_ids


def parse_excel_to_case_study_exercise_question_by_exercise_id(excel_file, exercise_doc_id: str, learning_materials):
    df = pd.read_excel(excel_file, sheet_name='Questions', header=1)
    exercise_spreadsheet_id = exercise_doc_id.split(':')[1]
    # print(section_spreadsheet_id)
    pattern = f'^{exercise_spreadsheet_id}\.'
    col_id = get_a_matching_column_name_by_regex(df, r'question id')
    filtered_df = df[df[col_id].str.contains(pattern, na=False)]
    # print('\n')
    # print(filtered_df)

    col_desc = get_a_matching_column_name_by_regex(df, r'description')
    col_url = get_a_matching_column_name_by_regex(df, r'image url')
    col_option_header = get_a_matching_column_name_by_regex(df, r'option header')
    col_a = get_a_matching_column_name_by_regex(df, r'option a')
    col_b = get_a_matching_column_name_by_regex(df, r'option b')
    col_c = get_a_matching_column_name_by_regex(df, r'option c')
    col_d = get_a_matching_column_name_by_regex(df, r'option d')
    col_answer = get_a_matching_column_name_by_regex(df, r'^answer')
    col_feedback_for_correct_answer = get_a_matching_column_name_by_regex(df, r'feedback for correct')
    col_feedback_for_incorrect_answer = get_a_matching_column_name_by_regex(df, r'feedback for incorrect')
    col_learning_mat = get_a_matching_column_name_by_regex(df, r'additional learning material id')
    col_tags = get_a_matching_column_name_by_regex(df, r'tags')

    exercise_questions = []
    for index, row in filtered_df.iterrows():

        reference_id = row[col_id]
        desc = row[col_desc]
        image_url = None if pd.isnull(row[col_url]) else row[col_url]
        option_header = None if pd.isnull(row[col_option_header]) else row[col_option_header]
        feedback_for_correct_answer = row[col_feedback_for_correct_answer]
        feedback_for_incorrect_answer = None if pd.isnull(row[col_feedback_for_incorrect_answer]) \
            else row[col_feedback_for_incorrect_answer]
        # parse options and answer
        options = parse_options(row, col_a, col_b, col_c, col_d)
        answer = None if pd.isnull(row[col_answer]) else get_answer_option(options, row[col_answer])
        if len(options) > 0 and pd.isnull(option_header):
            option_header = 'Please select your answer:'
        # get additional learning material doc id
        additional_learning_material_id = None if pd.isnull(row[col_learning_mat]) else (
            get_doc_ids_by_their_spreadsheet_ids(row[col_learning_mat], learning_materials)[0])
        tags = None if pd.isnull(row[col_tags]) else [tag.strip() for tag in row[col_tags].split(',')]

        question = QuestionV2(
            reference_id=reference_id,
            description=desc,
            image_url=image_url,
            option_header=option_header,
            options=options,
            answer=answer,
            feedback_for_correct_answer=feedback_for_correct_answer,
            feedback_for_incorrect_answer=feedback_for_incorrect_answer,
            additional_learning_material_id=additional_learning_material_id,
            tags=tags
        )

        exercise_questions.append(question)

    exercise_questions.sort(reverse=False, key=return_spreadsheet_id)
    return exercise_questions


def return_spreadsheet_id(o: QuestionV2):
    return o.referenceId


def parse_options(df_row, col_a, col_b, col_c, col_d):
    col_options = [col_a, col_b, col_c, col_d]
    options = []
    for col_option in col_options:
        if not pd.isnull(df_row[col_option]):
            value = df_row[col_option]
            label = 'A'
            if col_option == col_b:
                label = 'B'
            elif col_option == col_c:
                label = 'C'
            elif col_option == col_d:
                label = 'D'

            o = OptionWithoutAnnotation(label, value)
            options.append(o)
    return options


def get_answer_option(options, answer):
    result = [option for option in options if option.label == answer]
    return result[0]








