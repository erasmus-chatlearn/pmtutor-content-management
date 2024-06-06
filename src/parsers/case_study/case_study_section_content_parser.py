import pandas as pd
from utilities.regex_utilities import get_a_matching_column_name_by_regex
from cloudant_models.content_element import ContentElement
from parsers.parser_utilities import get_doc_ids_by_their_spreadsheet_ids


def parse_excel_to_case_study_section_content_by_section_id(excel_file, section_doc_id: str, learning_materials):
    df = pd.read_excel(excel_file, sheet_name='Section Content', header=1)
    section_spreadsheet_id = section_doc_id.split('section-')[1]
    # print(section_spreadsheet_id)
    pattern = f'^{section_spreadsheet_id}-content-'
    col_id = get_a_matching_column_name_by_regex(df, r'content id')
    filtered_df = df[df[col_id].str.contains(pattern, na=False)]
    # print('\n')
    # print(filtered_df)

    col_format = get_a_matching_column_name_by_regex(df, r'\*section content format')
    col_desc = get_a_matching_column_name_by_regex(df, r'description')
    col_url = get_a_matching_column_name_by_regex(df, r'source url')
    col_learning_mat = get_a_matching_column_name_by_regex(df, r'additional learning material ids')

    section_contents = []
    for index, row in filtered_df.iterrows():

        parent_id = section_doc_id
        spreadsheet_ref_id = row[col_id]
        content_type = row[col_format]
        desc = row[col_desc]
        url = None if pd.isnull(row[col_url]) else row[col_url]
        # get additional learning material doc ids
        additional_mat = None if pd.isnull(row[col_learning_mat]) else (
            get_doc_ids_by_their_spreadsheet_ids(row[col_learning_mat], learning_materials))

        content = ContentElement(
            parent_id=parent_id,
            spread_sheet_ref_id=spreadsheet_ref_id,
            content_element_type=content_type,
            description=desc,
            source_url=url,
            additional_learning_material_ids=additional_mat
        )

        section_contents.append(content)

    section_contents.sort(reverse=False, key=return_spreadsheet_id)
    return section_contents


def parse_excel_to_case_study_section_content_by_section_spreadsheet_id(excel_file, section_doc_id: str,
                                                                        section_spreadsheet_id: str,
                                                                        learning_materials):
    df = pd.read_excel(excel_file, sheet_name='Section Content', header=1)
    # section_spreadsheet_id = section_doc_id.split('section-')[1]
    # print(section_spreadsheet_id)
    pattern = f'^{section_spreadsheet_id}-content-'
    col_id = get_a_matching_column_name_by_regex(df, r'content id')
    filtered_df = df[df[col_id].str.contains(pattern, na=False)]
    # print('\n')
    # print(filtered_df)

    col_format = get_a_matching_column_name_by_regex(df, r'\*section content format')
    col_desc = get_a_matching_column_name_by_regex(df, r'description')
    col_url = get_a_matching_column_name_by_regex(df, r'source url')
    col_learning_mat = get_a_matching_column_name_by_regex(df, r'additional learning material ids')

    section_contents = []
    for index, row in filtered_df.iterrows():

        parent_id = section_doc_id
        spreadsheet_ref_id = row[col_id]
        content_type = row[col_format]
        desc = row[col_desc]
        url = None if pd.isnull(row[col_url]) else row[col_url]
        # get additional learning material doc ids
        additional_mat = None if pd.isnull(row[col_learning_mat]) else (
            get_doc_ids_by_their_spreadsheet_ids(row[col_learning_mat], learning_materials))

        content = ContentElement(
            parent_id=parent_id,
            spread_sheet_ref_id=spreadsheet_ref_id,
            content_element_type=content_type,
            description=desc,
            source_url=url,
            additional_learning_material_ids=additional_mat
        )

        section_contents.append(content)

    section_contents.sort(reverse=False, key=return_spreadsheet_id)
    return section_contents


def return_spreadsheet_id(o: ContentElement):
    return o.spreadSheetRefId









