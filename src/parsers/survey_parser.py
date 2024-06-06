from cloudant_models.survey import Survey
from parsers.parser_utilities import get_now_in_unix_milliseconds


def parse_survey_sheet_to_survey(dataframe, expected_column_names: tuple) -> Survey:
    org_id = survey_type = name = description = sections = updated_at = None
    for i, row in dataframe.iterrows():
        org_id = row[expected_column_names[0]]
        survey_type = row[expected_column_names[1]]
        name = row[expected_column_names[2]]
        description = row[expected_column_names[3]]
    created_at = get_now_in_unix_milliseconds()
    doc_id = org_id + '-' + survey_type + ':' + str(created_at)
    return Survey(doc_id, org_id, survey_type, name, description, sections, created_at, updated_at)

