import pandas as pd
from utilities.regex_utilities import get_a_matching_column_name_by_regex
from cloudant_models.learning_material_v2 import LearningMaterialV2
from utilities.case_study_parser_utilities import add_zero_to_section_ref_id


def parse_excel_to_additional_learning_materials(args, case_study_config_id: str) -> list:
    file = args.excel_file[0]
    df = pd.read_excel(file, sheet_name='Additional Learning Material', header=1)

    col_format = get_a_matching_column_name_by_regex(df, r'format')
    col_url = get_a_matching_column_name_by_regex(df, r'source url')
    col_level = get_a_matching_column_name_by_regex(df, r'level')
    col_name = get_a_matching_column_name_by_regex(df, r'name')
    col_desc = get_a_matching_column_name_by_regex(df, r'description')
    col_row_id = get_a_matching_column_name_by_regex(df, r'learning material id')
    # print(col_name, col_desc, col_url, col_level, col_format, col_row_id, sep='\n')

    case_study_partition_key = case_study_config_id.split(":")[0]
    learning_materials = []
    for index, row in df.iterrows():
        name = row[col_name]
        description = row[col_desc]
        source_url = row[col_url]
        level = row[col_level]
        mat_format = row[col_format]
        module_ref_id = None
        topic_ref_id = None
        spreadsheet_ref_id = row[col_row_id].strip()
        parent_id = f'{case_study_partition_key}:section-{add_zero_to_section_ref_id(spreadsheet_ref_id.split("-")[0])}'
        doc_id = f'{case_study_partition_key}:{spreadsheet_ref_id}'
        lm = LearningMaterialV2(
            _id=doc_id,
            name=name,
            description=None if pd.isnull(description) else description,
            source_url=source_url,
            level=level,
            material_format=mat_format,
            learning_module_reference_id=module_ref_id,
            topic_config_id=topic_ref_id,
            parent_id=parent_id,
            spread_sheet_ref_id=spreadsheet_ref_id
        )
        learning_materials.append(lm)

    learning_materials.sort(reverse=False, key=return_spreadsheet_id)
    return learning_materials


def return_spreadsheet_id(o: LearningMaterialV2):
    return o.spreadSheetRefId





