import pandas
from typing import List
from cloudant_models.survey_question import SurveyQuestion
from cloudant_models.option_without_annotation import OptionWithoutAnnotation


def parse_questions_sheet_to_survey_questions(df, expected_col_names: tuple) -> List[SurveyQuestion]:
    survey_questions = []
    for i, row in df.iterrows():
        ref_id = row[expected_col_names[0]]
        description = row[expected_col_names[1]]
        question_type = row[expected_col_names[2]]
        expected_input_type = row[expected_col_names[3]]
        option_header = None
        options = None
        is_self_assessment = False
        if question_type == 'singleSelect':
            option_header = row[expected_col_names[4]]
            options = []
            for j in range(5, len(expected_col_names)):
                if not pandas.isna(row[expected_col_names[j]]):
                    label = row[expected_col_names[j]]
                    value = row[expected_col_names[j]]
                    options.append(OptionWithoutAnnotation(label, value))
        survey_question = SurveyQuestion(ref_id,
                                         question_type,
                                         description,
                                         expected_input_type,
                                         option_header,
                                         options,
                                         is_self_assessment)
        survey_questions.append(survey_question)
    survey_questions.sort(reverse=False, key=return_ref_id)
    return survey_questions


def return_ref_id(q: SurveyQuestion):
    return q.referenceId
