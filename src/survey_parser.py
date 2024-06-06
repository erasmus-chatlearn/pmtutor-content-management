import argparse
import sys
from typing import List

import jsonpickle
import pandas
import re

from cloudant_models.survey import Survey
from cloudant_models.survey_question import SurveyQuestion
from cloudant_models.option_without_annotation import OptionWithoutAnnotation
from validators.excel_validator import check_excel_file_has_expected_sheets, check_a_sheet_has_expected_columns, \
    check_required_columns_have_values, check_values_in_column_are_unique
from validators.validation_message import ValidationMessage
from parsers.survey_parser import parse_survey_sheet_to_survey
from parsers.survey_sections_parser import parse_sections_sheet_to_survey_sections
from parsers.survey_questions_parser import parse_questions_sheet_to_survey_questions
from cloudant_db.utilities import get_db_name_from_env, get_active_docs_by_doc_type_and_scope, \
    get_all_topic_config_id_and_name

topic_db_name = get_db_name_from_env()


def main():
    print("Start survey parser...")
    try:
        args = parse_args()
        validate_survey_excel_file(args)
        doc = parse_excel_to_survey(args)
        doc_json = jsonpickle.encode(doc, unpicklable=False)
        file_path = "output/parsed-survey.json"
        with open(file_path, "w") as outfile:
            outfile.write(doc_json)
        sys.exit("\nParsing is completed, the parsed result is stored at " + file_path + '.')
    except (AssertionError, RuntimeError) as e:
        print('\nError: ' + str(e))
        sys.exit('Parsing is aborted.')


def parse_args():
    parser = argparse.ArgumentParser(description='The program parses \
        an excel file and attempts to convert it into a survey json object')
    parser.add_argument('excel_file', metavar='excel_file', nargs=1,
                        help='The excel file containing survey configuration')
    args = parser.parse_args()
    return args


def parse_excel_to_survey(args) -> Survey:
    print('\nParse the excel file...')
    file = args.excel_file[0]
    all_sheets = pandas.read_excel(file, sheet_name=None)

    print('\nParse "Survey" sheet...')
    expected_column_names, *_ = get_expected_column_names_and_row_number('Survey')
    survey = parse_survey_sheet_to_survey(all_sheets['Survey'], expected_column_names)

    print('\nParse "Sections" sheet...')
    expected_column_names, *_ = get_expected_column_names_and_row_number('Sections')
    sections_required_sas = all_sheets['Sections'].loc[all_sheets['Sections'][expected_column_names[5]] == True]
    survey.sections = parse_sections_sheet_to_survey_sections(all_sheets['Sections'], expected_column_names)

    print('\nParse "Questions" sheet...')
    expected_column_names, *_ = get_expected_column_names_and_row_number('Questions')
    all_excel_survey_questions = parse_questions_sheet_to_survey_questions(all_sheets['Questions'],
                                                                           expected_column_names)
    for section in survey.sections:
        section.questions = list(filter(lambda q: (q.referenceId.split('.')[0] == section.referenceId),
                                        all_excel_survey_questions))
        if len(section.questions) > 0:
            print('\nAdd parsed survey questions to section ' + section.referenceId + '...')

    print('\nThere is(are) ' + str(len(sections_required_sas)) + ' section(s) required creating SA questions from SAS.')
    if len(sections_required_sas) > 0:
        print('\nCreate self-assessment survey questions from existing self-assessment statements...')
        expected_column_names, *_ = get_expected_column_names_and_row_number('Sections')
        self_assessment_questions = create_survey_questions_from_self_assessment_statements()
        assign_sas_questions_to_sas_sections(survey, sections_required_sas, expected_column_names,
                                             self_assessment_questions)
    return survey


def validate_survey_excel_file(args):
    print("\nValidate excel file...")
    file = args.excel_file[0]
    all_sheets = pandas.read_excel(file, sheet_name=None)

    expected_sheet_names = ('Survey', 'Sections', 'Questions')
    has_all_expected_sheets = check_excel_file_has_expected_sheets(all_sheets, expected_sheet_names)

    if has_all_expected_sheets.is_valid is False:
        raise AssertionError(has_all_expected_sheets.message)
    else:
        print(has_all_expected_sheets.message)

    for expected_sheet in expected_sheet_names:
        print('\nInspect "' + expected_sheet + '" sheet...')

        expected_column_names, required_columns, expected_rows = \
            get_expected_column_names_and_row_number(expected_sheet)

        has_all_expected_columns = check_a_sheet_has_expected_columns(expected_sheet, all_sheets[expected_sheet],
                                                                      expected_column_names)
        if has_all_expected_columns.is_valid is False:
            raise AssertionError(has_all_expected_columns.message)
        else:
            print(has_all_expected_columns.message)

        check_expected_rows_in_survey_excel_sheet(expected_sheet, all_sheets, expected_rows)

        has_missing_value = check_if_missing_required_values_in_survey_excel_sheet(expected_sheet,
                                                                                   all_sheets[expected_sheet],
                                                                                   expected_column_names,
                                                                                   required_columns)
        if has_missing_value.is_valid is False:
            raise AssertionError(has_missing_value.message)
        else:
            print(has_missing_value.message)

        if expected_sheet == 'Sections' or expected_sheet == 'Questions':
            check_ref_id_uniqueness_for_sections_or_questions(expected_sheet, all_sheets, required_columns)

        print('The sheet seems ok.')


def get_expected_column_names_and_row_number(sheet_name: str):
    expected_column_names = ('Organization Id', 'Survey Type', 'Name (show to users)', 'Description (show to users)')
    required_columns = expected_column_names
    expected_rows = 1
    if sheet_name == 'Sections':
        expected_column_names = ('Name (show to users)',
                                 'Description (show to users)',
                                 'Is Self-Assessment (SA)',
                                 'SA Scope (required if Is Self-Assessment is true; '
                                 'should be one of the following value: "all" or "topic")',
                                 'SA Scope Name (required if SA Scope is not "all", e.g., topic name)',
                                 'Create Questions from Existing SA Statements '
                                 '(If true, do not provide questions in the Questions sheet)',
                                 'Reference Id')
        required_columns = ('Name (show to users)',
                            'Is Self-Assessment (SA)',
                            'Reference Id')
    elif sheet_name == 'Questions':
        expected_column_names = ('Reference Id (<Section Reference Id.xx>)',
                                 'Description (show to users)',
                                 'Question Type (If it is open, options are ignored)',
                                 'Expected Input Type (string / number / boolean, convert input to true or false)',
                                 'Option Header (If blank, default "Please select your answer below:" '
                                 'is shown to users)',
                                 'Option 1 (options will be shown to users)', 'Option 2', 'Option 3', 'Option 4',
                                 'Option 5', 'Option 6', 'Option 7', 'Option 8', 'Option 9', 'Option 10')
        required_columns = ('Reference Id (<Section Reference Id.xx>)',
                            'Description (show to users)',
                            'Question Type (If it is open, options are ignored)',
                            'Expected Input Type (string / number / boolean, convert input to true or false)')
    return expected_column_names, required_columns, expected_rows


def check_expected_rows_in_survey_excel_sheet(expected_sheet, all_sheets, expected_rows):
    actual_rows = len(all_sheets[expected_sheet])
    print('It has ' + str(actual_rows) + ' row(s).')
    if expected_sheet == 'Survey' and actual_rows != expected_rows:
        raise AssertionError('\n"' + expected_sheet + '" should have ' + str(expected_rows) + ' row.')
    elif expected_sheet == 'Sections' and actual_rows < expected_rows:
        raise AssertionError('\n"' + expected_sheet + '" should have at least ' + str(expected_rows) + ' row.')
    elif expected_sheet == 'Questions':
        inspect_rows_in_questions_sheet(actual_rows, all_sheets)


def inspect_rows_in_questions_sheet(actual_rows, all_sheets):
    df = all_sheets['Sections']
    section_expected_questions = df.loc[df['Create Questions from Existing SA Statements '
                                           '(If true, do not provide questions '
                                           'in the Questions sheet)'] != True, 'Reference Id']
    if len(section_expected_questions) == 0 and actual_rows > 0:
        raise AssertionError('\n"Questions" should have 0 row because the questions are expected '
                             'to be created from other sources.')
    elif len(section_expected_questions) > 0 and actual_rows == 0:
        raise AssertionError('\n"Questions" should have rows because 1 or more survey sections '
                             'requires questions.')
    elif len(section_expected_questions) > 0 and actual_rows > 0:
        question_ref_ids = all_sheets['Questions'].loc[:, "Reference Id (<Section Reference Id.xx>)"]
        check_if_a_survey_section_has_question(section_expected_questions, question_ref_ids)


def check_if_a_survey_section_has_question(section_expected_questions, question_ref_ids):
    for s in section_expected_questions:
        regex = '^' + s
        has_at_least_one_question = False
        for q_ref_id in question_ref_ids:
            if re.search(regex, q_ref_id):
                has_at_least_one_question = True
                break
        if has_at_least_one_question is False:
            raise AssertionError('\nSection "' + s + '" should have at least 1 row in "Questions".')


def check_if_missing_required_values_in_survey_excel_sheet(sheet_name, dataframe, expected_columns: tuple,
                                                           required_columns: tuple) -> ValidationMessage:
    result = check_required_columns_have_values(required_columns, dataframe)
    if result.is_valid is False:
        return result
    if sheet_name == 'Sections':
        result = inspect_rows_in_sections_sheet(dataframe, required_columns, expected_columns)
    if sheet_name == 'Questions':
        result = inspect_missing_value_in_questions_sheet(dataframe, required_columns)
    # print(result.message)
    return result


def inspect_rows_in_sections_sheet(dataframe, required_columns: tuple, expected_columns: tuple) -> ValidationMessage:
    result = ValidationMessage(True, 'The row(s) have all required values.')
    for index, row in dataframe.iterrows():
        if row[required_columns[1]] and pandas.isna(row[expected_columns[3]]):
            result.is_valid = False
            result.message = '\nRow ' + str(index + 1) + ' has a missing value. When column "' \
                             + required_columns[1] + '" is true, column "' + expected_columns[3] \
                             + '" should not be empty.'
            break
        elif row[required_columns[1]] and row[expected_columns[3]] != 'all' and \
                pandas.isna(row[expected_columns[4]]):
            result.is_valid = False
            result.message = '\nRow ' + str(index + 1) + ' has a missing value. When column "' \
                             + expected_columns[3] + '" has a value other than "all", column "' + \
                             expected_columns[4] + '" should not be empty.'
            break
    return result


def inspect_missing_value_in_questions_sheet(dataframe, required_columns: tuple) -> ValidationMessage:
    result = ValidationMessage(True, 'The row(s) have all required values.')
    for index, row in dataframe.iterrows():
        if row[required_columns[2]] == 'singleSelect' and pandas.isna(row[5]):
            result.is_valid = False
            result.message = '\nRow ' + str(index + 1) + ' has a missing value. When column "' \
                             + required_columns[2] + '" is singleSelect, column "Option 1" should not be empty.'
            break
    return result


def check_ref_id_uniqueness_for_sections_or_questions(expected_sheet, all_sheets, required_columns: tuple):
    are_ref_ids_unique = None
    if expected_sheet == 'Sections':
        ref_id_column_name = required_columns[2]
        are_ref_ids_unique = check_values_in_column_are_unique(all_sheets[expected_sheet], ref_id_column_name)
    elif expected_sheet == 'Questions':
        ref_id_column_name = required_columns[0]
        are_ref_ids_unique = check_values_in_column_are_unique(all_sheets[expected_sheet], ref_id_column_name)
    if are_ref_ids_unique is not None and are_ref_ids_unique.is_valid:
        print(are_ref_ids_unique.message)
    elif are_ref_ids_unique is not None and not are_ref_ids_unique.is_valid:
        raise AssertionError(are_ref_ids_unique.message)


def create_survey_questions_from_self_assessment_statements() -> List[SurveyQuestion]:
    topic_db = get_db_name_from_env()
    self_assessment_statements = get_active_docs_by_doc_type_and_scope(topic_db, 'selfAssessmentStatement', 'exercise')
    survey_questions = []

    if 'docs' in self_assessment_statements:
        if len(self_assessment_statements['docs']) == 0:
            msg = 'Found no self-assessment statements in the database. Please check if the target database name is ' \
                  'set correctly in the .env file. Or create those questions to the excel file.'
            raise AssertionError(msg)

        survey_questions = []
        for sas in self_assessment_statements['docs']:
            survey_questions.append(create_survey_question_from_self_assessment_statement(sas))

    elif 'error' in self_assessment_statements:
        raise AssertionError(self_assessment_statements['error'])

    return survey_questions


def create_survey_question_from_self_assessment_statement(self_assessment_statement) -> SurveyQuestion:
    is_sas = True
    ref_id = self_assessment_statement['_id']
    question_type = 'singleSelect'
    description = self_assessment_statement['description']
    option_header = 'Regarding the statement, please select from Strongly disagree to Strongly agreed (1-5):'
    likert_labels = ('Strongly disagree (1)', 'Disagree (2)', 'Neither agree nor disagree (3)', 'Agree (4)',
                     'Strongly agree (5)')
    options = create_likert_options(likert_labels)
    expected_input_type = 'number'
    return SurveyQuestion(ref_id,
                          question_type,
                          description,
                          expected_input_type,
                          option_header,
                          options,
                          is_sas)


def create_likert_options(likert_labels: tuple) -> List[OptionWithoutAnnotation]:
    options = []
    for i in range(len(likert_labels)):
        option = OptionWithoutAnnotation(likert_labels[i], str(i+1))
        options.append(option)
    return options


def assign_sas_questions_to_sas_sections(survey: Survey, sas_sections_df, expected_columns: tuple,
                                         sas_questions: [SurveyQuestion]):
    print('\nGet existing topic config ids and names from database "' + topic_db_name + '"...')
    all_topic_ids_and_names = get_all_topic_config_id_and_name(topic_db_name)
    if 'error' in all_topic_ids_and_names:
        raise AssertionError(all_topic_ids_and_names['error'])
    if len(all_topic_ids_and_names['docs']) == 0:
        raise AssertionError('No topics are found in the database')

    for i, row in sas_sections_df.iterrows():
        print('\nAssign SA survey questions to SA section ' + row[expected_columns[6]] + '...')
        section_ref_id = row[expected_columns[6]]
        survey_section_index = next((i for i, s in enumerate(survey.sections) if s.referenceId == section_ref_id), -1)
        if survey_section_index != -1 and row[expected_columns[3]].lower().strip() == 'all':
            survey.sections[survey_section_index].questions = sas_questions
        elif survey_section_index != -1 and row[expected_columns[3]].lower().strip() == 'topic':
            scope_name = row[expected_columns[4]]
            topic_config_id = get_topic_config_id_by_topic_name(all_topic_ids_and_names['docs'], scope_name)
            # print(topic_config_id)
            if topic_config_id is None:
                msg = 'The section SA scope is topic but the SA scope name "' + scope_name + \
                      '" cannot be found in the existing topic names. Please update the section SA scope name.'
                raise AssertionError(msg)
            topic_config_partition_key = topic_config_id.split(':')[0]
            survey.sections[survey_section_index].questions = \
                filter_sa_questions_by_partition_key(sas_questions, topic_config_partition_key)
            if len(survey.sections[survey_section_index].questions) == 0:
                msg = 'There is no SA questions for the section "' + scope_name + \
                      '", please create SA statements first or remove the survey section from the survey excel file.'
                raise AssertionError(msg)


def get_topic_config_id_by_topic_name(topic_ids_names, scope_name) -> str:
    topic_config_id = None
    for item in topic_ids_names:
        if item['name'].lower().strip() == scope_name.lower().strip():
            topic_config_id = item['_id']
            break
    return topic_config_id


def filter_sa_questions_by_partition_key(sa_questions, partition_key) -> List[SurveyQuestion]:
    return list(filter(lambda q: (q.referenceId.split(':')[0] == partition_key), sa_questions))


if __name__ == '__main__':
    main()
