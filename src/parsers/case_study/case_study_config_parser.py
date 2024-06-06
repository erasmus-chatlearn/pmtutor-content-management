import pandas as pd
from cloudant_models.case_study_config import CaseStudyConfig
from utilities.regex_utilities import get_a_matching_column_name_by_regex


def parse_excel_to_case_study_config(args) -> CaseStudyConfig:
    file = args.excel_file[0]
    df = pd.read_excel(file, sheet_name='Case Study')
    row_index = 0
    org_name = get_value_by_col_name_regex_and_index(df, r'organization name', row_index)
    org_id = get_value_by_col_name_regex_and_index(df, r'org id', row_index)
    case_study_id = get_value_by_col_name_regex_and_index(df, r'case study id', row_index)
    case_study_name = get_value_by_col_name_regex_and_index(df, r'^\*name', row_index)
    case_study_desc = get_value_by_col_name_regex_and_index(df, r'description', row_index)
    case_study_objectives = get_value_by_col_name_regex_and_index(df, r'objective', row_index)
    tags_string = get_value_by_col_name_regex_and_index(df, r'tags', row_index)
    case_study_tags = None if pd.isnull(tags_string) else [tag.strip() for tag in tags_string.split(',')]
    doc_id = f'{org_id.strip()}-{case_study_id.strip()}:caseStudyConfig'
    # print(doc_id, org_name, org_id, case_study_id, case_study_name, case_study_desc, case_study_objectives, case_study_tags, sep=', ')
    case_study_config = CaseStudyConfig(
        _id=doc_id,
        organization_name=org_name,
        org_id=org_id,
        spread_sheet_ref_id=case_study_id,
        name=case_study_name,
        description=case_study_desc,
        objectives=None if pd.isnull(case_study_objectives) else case_study_objectives,
        tags=None if pd.isnull(tags_string) else case_study_tags
    )
    return case_study_config


def get_value_by_col_name_regex_and_index(df, col_name_regex, index):
    col_name = get_a_matching_column_name_by_regex(df, col_name_regex)
    cell_value = df.loc[df.index[index], col_name]
    return cell_value






