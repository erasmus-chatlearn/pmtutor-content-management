import pandas as pd
from utilities.regex_utilities import get_a_matching_column_name_by_regex
from cloudant_models.case_study_section import CaseStudySection
from .case_study_section_content_parser import parse_excel_to_case_study_section_content_by_section_spreadsheet_id
from utilities.case_study_parser_utilities import add_zero_to_section_ref_id


def parse_excel_to_case_study_sections(args, case_study_config_id: str, learning_materials):
    file = args.excel_file[0]
    df = pd.read_excel(file, sheet_name='Section', header=1)

    col_name = get_a_matching_column_name_by_regex(df, r'section name')
    col_spreadsheet_id = get_a_matching_column_name_by_regex(df, r'section id')

    case_study_partition_key = case_study_config_id.split(':')[0]
    sections = []
    for index, row in df.iterrows():
        section_name = row[col_name]
        spreadsheet_id = str(row[col_spreadsheet_id])
        parent_id = case_study_config_id
        description = None
        objectives = None
        has_exercises = check_if_a_section_has_exercise(file, spreadsheet_id)
        doc_id = f'{case_study_partition_key}:section-{add_zero_to_section_ref_id(spreadsheet_id)}'
        content_elements = parse_excel_to_case_study_section_content_by_section_spreadsheet_id(
            file, doc_id, spreadsheet_id, learning_materials)

        sect = CaseStudySection(
            _id=doc_id,
            parent_id=parent_id,
            spread_sheet_ref_id=spreadsheet_id,
            name=section_name,
            description=description,
            objectives=objectives,
            has_exercises=has_exercises,
            content_elements=content_elements
        )
        sections.append(sect)

    sections.sort(reverse=False, key=return_spreadsheet_id)
    return sections


def return_spreadsheet_id(o: CaseStudySection):
    return o._id


def check_if_a_section_has_exercise(excel_file, section_id):
    df = pd.read_excel(excel_file, sheet_name='Exercises', header=1)
    exercise_id_col_name = get_a_matching_column_name_by_regex(df, r'exercise id')
    section_has_exercise = False
    for index, row in df.iterrows():
        if str(row[exercise_id_col_name]).split(".")[0] == section_id:
            # print(f'{row[exercise_id_col_name]} belongs to section {section_id}')
            section_has_exercise = True
            break
    return section_has_exercise


