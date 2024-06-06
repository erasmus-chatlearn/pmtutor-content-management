import pandas
from typing import List

from cloudant_models.survey_section import SurveySection


def parse_sections_sheet_to_survey_sections(dataframe, expected_col_names: tuple) -> List[SurveySection]:
    sections = []
    for i, row in dataframe.iterrows():
        section_ref_id = row[expected_col_names[6]]
        section_name = row[expected_col_names[0]]
        section_description = None if pandas.isna(row[expected_col_names[1]]) else row[expected_col_names[1]]
        sections.append(SurveySection(section_ref_id, section_name, section_description, None))
    sections.sort(reverse=False, key=return_ref_id)
    return sections


def return_ref_id(s: SurveySection):
    return s.referenceId

