import argparse
import re
import sys
import jsonpickle
import pandas as pd

from validators.excel_validator import check_a_sheet_has_needed_columns_with_regex, \
    check_required_columns_have_values_by_regex, check_values_in_column_are_unique, \
    check_uniqueness_of_list_items_in_cell, check_cell_string_exists_in_another_sheet_column, \
    check_column_values_match_a_regex_pattern, check_referring_to_an_existing_parent_id, \
    check_ids_are_referred_by_child_ids_in_another_sheet, check_column_y_has_value_given_column_x_values, \
    check_values_of_columns_matching_given_regex
from utilities.regex_utilities import get_a_matching_column_name_by_regex, get_matching_column_names_by_regex

from cloudant_models.documents import Documents
from parsers.case_study.case_study_config_parser import parse_excel_to_case_study_config
from parsers.case_study.additional_learning_material_parser import parse_excel_to_additional_learning_materials
from parsers.case_study.case_study_section_parser import parse_excel_to_case_study_sections
from parsers.case_study.case_study_exercise_parser import parse_excel_to_a_exercise_v2_list


def main():
    print("Start case study parser...")
    try:
        args = parse_args()
        validate_case_study_excel_file(args)
        docs = parse_excel_to_case_study_documents(args)
        doc_json = jsonpickle.encode(docs, unpicklable=False)
        file_path = "output/parsed-case-study-docs.json"
        with open(file_path, "w") as outfile:
             outfile.write(doc_json)
        sys.exit("\nParsing is completed, the parsed result is stored at " + file_path + '.')
    except (AssertionError, RuntimeError, ValueError) as e:
        print('\n\nError: ' + str(e))
        sys.exit('\nParsing is aborted. Please fix the error and try again.')


def parse_args():
    parser = argparse.ArgumentParser(description='The program parses \
        an excel file and attempts to convert it into a case study json object')
    parser.add_argument('excel_file', metavar='excel_file', nargs=1,
                        help='The excel file containing case study configuration')
    args = parser.parse_args()
    return args


# Validation functions
def validate_case_study_excel_file(args):
    print("\nValidate excel file...")
    file = args.excel_file[0]
    all_sheets = {}
    expected_sheet_names = ('Case Study', 'Section', 'Section Content', 'Exercises', 'Questions',
                            'Additional Learning Material')
    # It will raise a value error if the sheet is not in the file
    for sheet in expected_sheet_names:
        # most of the sheets show instruction in the first row
        header_row = 1
        if sheet == 'Case Study':
            header_row = 0
        all_sheets[sheet] = pd.read_excel(file, sheet_name=sheet, header=header_row)

    for expected_sheet in expected_sheet_names:

        print(f'\nInspect "{expected_sheet}" sheet...')

        expected_column_regex = get_expected_column_name_regexes(expected_sheet)
        check_expected_columns = check_a_sheet_has_needed_columns_with_regex(expected_sheet, all_sheets[expected_sheet],
                                                                             expected_column_regex)
        print('Check the sheet having all the needed columns:', end=' ')
        if check_expected_columns.is_valid is False:
            raise AssertionError(check_expected_columns.message)
        print(check_expected_columns.message, 'OK!')

        print('Check the number of rows in the sheet: ', end=' ')
        check_expected_row_number_in_case_study_excel_sheet(expected_sheet, all_sheets)

        pattern = r'^\*'
        print(f'Check if the required columns matching the regex pattern {pattern} have value(s):', end=' ')
        check_first_row_only = False if expected_sheet != 'Case Study' else True
        check_required_columns_have_values = check_required_columns_have_values_by_regex(expected_sheet,
                                                                                         all_sheets[expected_sheet],
                                                                                         pattern, check_first_row_only)
        if check_required_columns_have_values.is_valid is False:
            raise AssertionError(check_required_columns_have_values.message)
        print(check_required_columns_have_values.message, 'OK!')

        spreadsheet_id_column_name_regex = get_regex_for_spreadsheet_id_column_name(expected_sheet)
        if spreadsheet_id_column_name_regex is not None:
            column_name = get_a_matching_column_name_by_regex(all_sheets[expected_sheet],
                                                              spreadsheet_id_column_name_regex)
            id_pattern = get_regex_for_id_pattern_in_case_study(expected_sheet)

            print(f"Check if the ids match the expected pattern {id_pattern}:", end=' ')
            check_column_values_match_a_regex_pattern(
                all_sheets[expected_sheet], column_name, id_pattern, False)
            print(f'The value(s) in column "{column_name}" match the expected pattern', 'OK!')

            print('Check if ids are unique:', end=' ')
            check_spreadsheet_ids_uniqueness = check_values_in_column_are_unique(all_sheets[expected_sheet],
                                                                                 column_name)
            if check_spreadsheet_ids_uniqueness.is_valid is False:
                raise AssertionError(check_spreadsheet_ids_uniqueness.message)
            print(check_spreadsheet_ids_uniqueness.message, 'OK!')

        # check urls should contain a valid scheme and domain name pattern
        url_column_name_regex = r'^(?=.*(?:source url|image url)).*$'

        print(f'Check valid URLs if there is a url column:')
        url_pattern = r'^(https?://)([A-Za-z0-9-]+\.)+[A-Za-z]{2,6}'
        check_values_of_columns_matching_given_regex(all_sheets[expected_sheet],
                                                     url_column_name_regex,
                                                     url_pattern,
                                                     allow_empty=True)

        # check valid level
        print('Check if any column for Level:')
        check_values_of_columns_matching_given_regex(
            all_sheets[expected_sheet],
            r'level',
            r'^[1-5]$',
            allow_empty=False)
        # check if referenced learning material ids are unique and existing in the additional learning material
        if expected_sheet != "Additional Learning Material":

            print('Check if there are columns referencing additional learning material:')
            # pattern = r'^additional learning material ids'
            pattern = r'additional learning material id'
            columns_containing_additional_learning_material_ids = get_matching_column_names_by_regex(
                all_sheets[expected_sheet], pattern)
            print(f"{str(len(columns_containing_additional_learning_material_ids))} "
                  f"column(s) contain(s) additional learning material id(s)", 'OK!')

            if len(columns_containing_additional_learning_material_ids) > 0:
                # print(columns_containing_additional_learning_material_ids)
                print(f'Column(s) {columns_containing_additional_learning_material_ids} '
                      f'referencing additional learning materials', 'OK!')
                check_uniqueness_of_list_items_in_cell(all_sheets[expected_sheet],
                                                       columns_containing_additional_learning_material_ids,
                                                       ',')
                print('The referenced additional learning material ids are unique', 'OK!')
                learning_material_sheet = 'Additional Learning Material'
                # print(f'Check if the referencing ids exist in the {learning_material_sheet}:')
                pattern = get_regex_for_spreadsheet_id_column_name(learning_material_sheet)
                additional_learning_material_sheet_id_col = get_a_matching_column_name_by_regex(
                    all_sheets[learning_material_sheet], pattern)
                check_cell_string_exists_in_another_sheet_column(
                    all_sheets[expected_sheet],
                    columns_containing_additional_learning_material_ids,
                    ',',
                    all_sheets[learning_material_sheet],
                    additional_learning_material_sheet_id_col
                )
                print(f'The referenced additional learning material ids exist '
                      f'in the sheet "{learning_material_sheet}"', 'OK!')

        if expected_sheet == 'Section':
            print(f'Check specific logic for {expected_sheet}...')
            # print(f'Check specific logic for "{expected_sheet}"')
            # each section should at least have one section content
            child_sheet_name = 'Section Content'
            check_each_id_is_referred_in_another_sheet(expected_sheet, child_sheet_name, all_sheets)

        if expected_sheet == 'Section Content':
            print(f'Check specific logic for {expected_sheet}...')
            parent_sheet = "Section"
            check_each_child_ids_refer_to_existing_parent_id(expected_sheet, parent_sheet, all_sheets)
            independent_column_name_regex = r'\*section content format'

            print('Check valid section content formats:')
            valid_section_content_types = r'^(text|video|image|pdf|html|list of additional learning materials)$'
            check_values_of_columns_matching_given_regex(all_sheets[expected_sheet],
                                                         independent_column_name_regex,
                                                         valid_section_content_types,
                                                         allow_empty=False)
            # print('All section content formats are valid.', 'OK!')

            dependent_column_name_regex = r'source url'
            given_values_in_independent_column = ('video', 'image', 'pdf', 'html')
            check_the_dependency_between_two_columns(expected_sheet, independent_column_name_regex,
                                                     dependent_column_name_regex, given_values_in_independent_column,
                                                     all_sheets)

            dependent_column_name_regex = r'additional learning material ids'
            given_values_in_independent_column = ('list of additional learning materials',)
            check_the_dependency_between_two_columns(expected_sheet, independent_column_name_regex,
                                                     dependent_column_name_regex, given_values_in_independent_column,
                                                     all_sheets)

        if expected_sheet == 'Exercises':
            print(f'Check specific logic for {expected_sheet}...')
            parent_sheet = "Section"
            check_each_child_ids_refer_to_existing_parent_id(expected_sheet, parent_sheet, all_sheets)
            # Every exercise should have at least one question
            child_sheet_name = 'Questions'
            check_each_id_is_referred_in_another_sheet(expected_sheet, child_sheet_name, all_sheets)

        if expected_sheet == 'Questions':
            print(f'Check specific logic for {expected_sheet}...')
            parent_sheet = 'Exercises'
            check_each_child_ids_refer_to_existing_parent_id(expected_sheet, parent_sheet, all_sheets)
            # if there is an option header value, Option A should not be empty
            check_option_a_should_have_value_if_option_header_has_value(all_sheets[expected_sheet])
            # If has an answer, there should be a matching option
            # and the feedback for incorrect answer should not be empty
            print('Check answer:')
            independent_column_name_regex = r'^answer'
            valid_answer_values = r'^[ABCD]$'
            check_values_of_columns_matching_given_regex(all_sheets[expected_sheet], independent_column_name_regex,
                                                         valid_answer_values, allow_empty=True)
            check_answer_has_an_existing_option_and_value(all_sheets[expected_sheet], independent_column_name_regex)
            given_values_in_independent_column = ('A', 'B', 'C', 'D')
            dependent_column_name_regex = r'feedback for incorrect'
            check_the_dependency_between_two_columns(expected_sheet, independent_column_name_regex,
                                                     dependent_column_name_regex, given_values_in_independent_column,
                                                     all_sheets)
        if expected_sheet == 'Additional Learning Material':
            print(f'Check specific logic for {expected_sheet}...')
            parent_sheet = "Section"
            check_each_child_ids_refer_to_existing_parent_id(expected_sheet, parent_sheet, all_sheets)
            # check additional learning material formats are valid
            print(f'Check if the formats in {expected_sheet} are valid:')
            format_column_name_regex = r'format'
            format_value_regex = r'^(pdf|html|video)$'
            check_values_of_columns_matching_given_regex(
                all_sheets[expected_sheet], format_column_name_regex, format_value_regex, allow_empty=False)

        print(f'\nThe sheet "{expected_sheet}" seems OK.')

    print("\nComplete case study excel file validation.")


def get_expected_column_name_regexes(sheet_name: str):
    col_name_regexes = ('organization name', 'org id', 'case study id', r'\*name', 'description', 'objectives', 'tags')
    if sheet_name == 'Section':
        col_name_regexes = ('section name', 'section id')
    elif sheet_name == 'Section Content':
        col_name_regexes = ('section content format', 'description', 'source url', 'additional learning material ids',
                            'content id')
    elif sheet_name == 'Exercises':
        col_name_regexes = ('exercise name', 'description', 'objectives', 'level', 'solution id',
                            'additional learning material ids', 'exercise id')
    elif sheet_name == 'Questions':
        col_name_regexes = ('question id', 'description', 'image url', 'option header', 'option a', 'option b',
                            'option c', 'option d', 'answer', 'feedback for correct answer',
                            'feedback for incorrect answer', 'additional learning material id', 'tags')
    elif sheet_name == 'Additional Learning Material':
        col_name_regexes = ('learning material name', 'description', 'source url', 'format',
                            'additional learning material id')
    return col_name_regexes


def check_expected_row_number_in_case_study_excel_sheet(expected_sheet, all_sheets):
    actual_rows = len(all_sheets[expected_sheet])
    print('It has ' + str(actual_rows) + ' row(s)', 'OK!')
    # the Case Study sheet has one extra row as comment
    if expected_sheet == 'Case Study' and actual_rows != 2:
        raise AssertionError('\n"' + expected_sheet + '" should have 2 rows.')
    elif expected_sheet != 'Additional Learning Material' and actual_rows < 1:
        raise AssertionError('\n"' + expected_sheet + '" should have at least 1 row.')
    elif expected_sheet == 'Additional Learning Material':
        print('Inspect cells which reference learning materials in other sheets...')
        compare_additional_learning_material_rows_with_cells_referencing_learning_materials(actual_rows, all_sheets)


def compare_additional_learning_material_rows_with_cells_referencing_learning_materials(actual_rows, all_sheet):
    sheet_names = ('Section Content', 'Exercises', 'Questions')
    pattern = re.compile('learning material id', re.IGNORECASE)
    n_referencing_rows = 0
    for sheet in sheet_names:
        filtered_columns = all_sheet[sheet].filter(regex=pattern)
        n_referencing_rows += filtered_columns.notnull().any(axis=1).sum()

    print('There seem to be ' + str(n_referencing_rows) + ' rows in other sheets referencing learning materials.')
    if actual_rows == 0 and n_referencing_rows > 0:
        raise AssertionError("\nAdditional Learning Material has 0 row but there are " + str(n_referencing_rows) +
                             " cells in the file referencing additional learning materials."
                             "\nPlease make sure the referred learning materials "
                             "are in the Additional Learning Material sheet.")


def get_regex_for_spreadsheet_id_column_name(sheet_name: str):
    if sheet_name == "Section":
        return r'section id'
    elif sheet_name == "Section Content":
        return r'content id'
    elif sheet_name == "Exercises":
        return r'exercise id'
    elif sheet_name == "Questions":
        return r'question id'
    elif sheet_name == "Additional Learning Material":
        return r'learning material id'
    else:
        return None


def get_regex_for_id_pattern_in_case_study(sheet_name: str) -> str:
    """
    This function returns a regex pattern based on the sheet_name input.
    """
    if sheet_name == 'Section':
        return r"([1-9][0-9]|[1-9]|0[1-9])"
    elif sheet_name == 'Section Content':
        return r"([1-9][0-9]|[1-9]|0[1-9])-content-(0[1-9]|[1-9][0-9])"
    elif sheet_name == 'Exercises':
        return r"([1-9][0-9]|[1-9]|0[1-9])\.([1-9])"
    elif sheet_name == 'Questions':
        return r"([1-9][0-9]|[1-9]|0[1-9])\.([1-9])\.(0[1-9]|[1-9][0-9])"
    elif sheet_name == 'Additional Learning Material':
        return r"([1-9][0-9]|[1-9]|0[1-9])-mat-(0[1-9]|[1-9][0-9])"
    else:
        raise AssertionError(f'the given sheet name {sheet_name} is invalid.')


def check_each_child_ids_refer_to_existing_parent_id(child_sheet: str, parent_sheet: str, all_sheets):
    print(f'Check the ids in "{child_sheet}" refer to an existing parent id in "{parent_sheet}":', end=' ')

    parent_id_column_name_regex = get_regex_for_spreadsheet_id_column_name(parent_sheet)
    parent_id_column_name = get_a_matching_column_name_by_regex(all_sheets[parent_sheet],
                                                                parent_id_column_name_regex)
    parent_id_pattern = get_regex_for_id_pattern_in_case_study(parent_sheet)
    child_id_column_name_regex = get_regex_for_spreadsheet_id_column_name(child_sheet)
    child_id_column_name = get_a_matching_column_name_by_regex(all_sheets[child_sheet],
                                                               child_id_column_name_regex)
    check_referring_to_an_existing_parent_id(
        all_sheets[child_sheet], child_id_column_name, parent_id_pattern,
        all_sheets[parent_sheet], parent_id_column_name)

    print(f'All ids in "{child_sheet}" refer to an existing parent id in "{parent_sheet}"', 'OK!')


def check_each_id_is_referred_in_another_sheet(current_sheet_name: str, child_sheet_name: str, all_sheets):
    print(f'Check the ids in "{current_sheet_name}" are referred in "{child_sheet_name}":', end=' ')

    id_column_name_regex = get_regex_for_spreadsheet_id_column_name(current_sheet_name)
    id_column_name = get_a_matching_column_name_by_regex(all_sheets[current_sheet_name], id_column_name_regex)
    id_pattern = get_regex_for_id_pattern_in_case_study(current_sheet_name)
    child_id_column_regex = get_regex_for_spreadsheet_id_column_name(child_sheet_name)
    child_id_column_name = get_a_matching_column_name_by_regex(all_sheets[child_sheet_name], child_id_column_regex)

    check_ids_are_referred_by_child_ids_in_another_sheet(all_sheets[current_sheet_name], id_column_name, id_pattern,
                                                         all_sheets[child_sheet_name], child_id_column_name)

    print(f'All the ids in "{current_sheet_name}" are referred in "{child_sheet_name}"', 'OK!')


def check_the_dependency_between_two_columns(sheet_name, independent_col_name_regex, dependent_col_name_regex,
                                             given_values_in_independent_col, all_sheets):
    column_x_name = get_a_matching_column_name_by_regex(all_sheets[sheet_name], independent_col_name_regex)
    column_y_name = get_a_matching_column_name_by_regex(all_sheets[sheet_name], dependent_col_name_regex)
    print(f'Check the dependency between column "{column_x_name}" and column "{column_y_name}":')
    check_column_y_has_value_given_column_x_values(
        all_sheets[sheet_name], column_x_name, column_y_name, given_values_in_independent_col
    )
    print(f'If column "{column_x_name}" has {given_values_in_independent_col}, '
          f'column "{column_y_name}" should also have a value', 'OK!')


def check_answer_has_an_existing_option_and_value(questions_sheet_df, answer_column_regex):
    answer_column_name = get_a_matching_column_name_by_regex(questions_sheet_df, answer_column_regex)
    for index, row in questions_sheet_df.iterrows():
        if not pd.isnull(row[answer_column_name]):
            option_column_regex = f'option {row[answer_column_name]}'
            option_column_name = get_a_matching_column_name_by_regex(questions_sheet_df, option_column_regex)
            if pd.isnull(row[option_column_name]):
                raise AssertionError(f'In row {str(index + 1)}, answer is {row[answer_column_name]} '
                                     f'but {option_column_name} is empty.')


def check_option_a_should_have_value_if_option_header_has_value(question_sheet_df):
    print('Check option header and options:')
    option_header_regex = r'^option header'
    option_header_col_name = get_a_matching_column_name_by_regex(question_sheet_df, option_header_regex)
    option_a_regex = r'^option a'
    option_a_col_name = get_a_matching_column_name_by_regex(question_sheet_df, option_a_regex)
    for index, row in question_sheet_df.iterrows():
        if not pd.isnull(row[option_header_col_name]):
            assert not pd.isnull(row[option_a_col_name]), \
                (f'In row {str(index + 1)}, "{option_header_col_name}" has value "{row[option_header_col_name]}", '
                 f'therefore column "{option_a_col_name}" should not be empty!')
    print(f'If column "{option_header_col_name}" has value, column "{option_a_col_name}" also has value', 'OK!')


def check_is_level_column_valid(sheet_name, level_col_name_regex, sheet_df):
    # does the sheet has a column for level
    print(f'Check if the sheet "{sheet_name}" has a column for level:', end=' ')
    matching_columns = get_matching_column_names_by_regex(sheet_df, level_col_name_regex)
    if len(matching_columns) > 1:
        raise AssertionError(f'If a sheet contains level, it should only have one column for it, '
                             f'instead there are {str(len(matching_columns))} columns!')
    if len(matching_columns) == 0:
        print('It does not have a column for level', 'OK!')
    if len(matching_columns) == 1:
        level_pattern = r'[1-5]$'
        # print(f'Check if there is a column for level and if its values match {level_pattern}:')
        check_values_of_columns_matching_given_regex(sheet_df, level_col_name_regex, level_pattern, allow_empty=False)


# Parser functions
def parse_excel_to_case_study_documents(args) -> Documents:
    """
    It takes a loaded case study excel file
    and returns documents based on the data models
    """
    print('\nParse the case study file into objects...')
    documents = Documents([])

    # parse "Case Study" sheet into CoseStudyConfig
    case_study_config = parse_excel_to_case_study_config(args)
    documents.docs.append(case_study_config)

    # parse "Additional Learning Material" sheet into a list of LearningMaterialV2
    learning_materials = parse_excel_to_additional_learning_materials(args, case_study_config._id)
    documents.docs.extend(learning_materials)

    # parse "Section" and "Section Content" sheet into a list of CaseStudySection
    sections = parse_excel_to_case_study_sections(args, case_study_config._id, learning_materials)
    documents.docs.extend(sections)

    # parse "Exercises" and "Questions" sheet into a list of ExerciseV2
    exercises = parse_excel_to_a_exercise_v2_list(args, sections, learning_materials)
    documents.docs.extend(exercises)

    return documents


if __name__ == '__main__':
    main()
