from typing import List

import pandas
from cloudant_models.self_assessment_statement import SelfAssessmentStatement
from parsers.parser_utilities import get_now_in_unix_milliseconds


def parse_excel_to_self_assessment_statements(args, topic_config) -> List[SelfAssessmentStatement]:
    sas_list: List[SelfAssessmentStatement] = []
    file = args.excel_file[0]
    exercise_df = pandas.read_excel(file, sheet_name='Exercises', header=1)

    for i, row in exercise_df.iterrows():
        statement = row['Self-Assessment Statement']
        scope_name = row['*Exercise Name']
        exercise_reference_id = row['*Reference ID (<Learning Module Ref. ID>.<order in the module, 1-9>)']

        if pandas.isna(statement) or pandas.isna(scope_name) or pandas.isna(exercise_reference_id):
            continue

        scope = 'exercise'
        exercise_id = topic_config.orgId + '-' + topic_config.topicId + ':' + str(exercise_reference_id)
        created_at = get_now_in_unix_milliseconds()
        doc_id = topic_config.orgId + '-' + topic_config.topicId + ':sas_' + scope + '_' + \
            exercise_id + '_' + str(created_at)
        updated_at = None
        is_active = True

        sas = SelfAssessmentStatement(
            doc_id,
            statement,
            scope,
            exercise_id,
            scope_name,
            created_at,
            updated_at,
            is_active
        )

        sas_list.append(sas)
    return sas_list
