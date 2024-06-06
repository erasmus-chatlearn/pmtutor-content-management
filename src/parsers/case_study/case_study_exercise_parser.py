import pandas as pd
from utilities.regex_utilities import get_a_matching_column_name_by_regex
from cloudant_models.exercise_v2 import ExerciseV2
from parsers.parser_utilities import get_doc_ids_by_their_spreadsheet_ids
from .case_study_question_parser import parse_excel_to_case_study_exercise_question_by_exercise_id
from utilities.case_study_parser_utilities import add_zero_to_assignment_ref_id


def parse_excel_to_a_exercise_v2_list(args, list_parents, list_learning_material_v2):
    # parent_spreadsheet_ref_ids = [parent.spreadSheetRefId for parent in list_parents]
    # print(parent_spreadsheet_ref_ids)
    file = args.excel_file[0]
    df = pd.read_excel(file, sheet_name='Exercises', header=1)
    col_exercise_id = get_a_matching_column_name_by_regex(df, r'exercise id')
    col_exercise_name = get_a_matching_column_name_by_regex(df, r'exercise name')
    col_description = get_a_matching_column_name_by_regex(df, r'description')
    col_objectives = get_a_matching_column_name_by_regex(df, r'objectives')
    col_level = get_a_matching_column_name_by_regex(df, r'level')
    col_solution_id = get_a_matching_column_name_by_regex(df, r'solution id')
    col_learning_materials = get_a_matching_column_name_by_regex(df, r'learning material ids')

    exercises = []
    for index, row in df.iterrows():
        exercise_name = row[col_exercise_name]
        description = None if pd.isnull(row[col_description]) else row[col_description]
        objectives = None if pd.isnull(row[col_objectives]) else row[col_objectives]
        level = row[col_level]
        spread_sheet_ref_id = str(row[col_exercise_id])
        # find parent doc id by finding exercise spreadsheet id
        parent_id = find_parent_doc_id_by_exercise_spreadsheet_id(spread_sheet_ref_id, list_parents)

        topic_config_id = None
        learning_module_reference_id = None
        # get solution id which is a learning material id
        solution_id = None if pd.isnull(row[col_solution_id]) else (
            get_doc_ids_by_their_spreadsheet_ids(row[col_solution_id], list_learning_material_v2)[0])
        # get learning material ids
        additional_learning_material_ids = None if pd.isnull(row[col_learning_materials]) else (
            get_doc_ids_by_their_spreadsheet_ids(row[col_learning_materials], list_learning_material_v2))
        doc_id = f'{parent_id.split(":")[0]}:{add_zero_to_assignment_ref_id(spread_sheet_ref_id)}'
        # get questions by exercise
        # minimum fix without have to update the question ref id in the excel file
        old_doc_id = f'{parent_id.split(":")[0]}:{spread_sheet_ref_id}'
        questions = parse_excel_to_case_study_exercise_question_by_exercise_id(
            file, old_doc_id, list_learning_material_v2)

        exercise = ExerciseV2(
            _id=doc_id,
            name=exercise_name,
            description=description,
            objectives=objectives,
            level=level,
            questions=questions,
            parent_id=parent_id,
            spread_sheet_ref_id=spread_sheet_ref_id,
            topic_config_id=topic_config_id,
            learning_module_reference_id=learning_module_reference_id,
            solution_id=solution_id,
            additional_learning_material_ids=additional_learning_material_ids
        )

        exercises.append(exercise)

    exercises.sort(reverse=False, key=return_spreadsheet_id)
    return exercises


def return_spreadsheet_id(o: ExerciseV2):
    return o.spreadSheetRefId


def find_parent_doc_id_by_exercise_spreadsheet_id(exercise_spreadsheet_id, list_parents):
    parent_spreadsheet_id = exercise_spreadsheet_id.split('.')[0]
    result = [parent._id for parent in list_parents if parent.spreadSheetRefId == parent_spreadsheet_id]
    return result[0]







