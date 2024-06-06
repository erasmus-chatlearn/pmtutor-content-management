from typing import List
import pandas
from cloudant_models.learning_module import LearningModule
from cloudant_models.topic_config import TopicConfig


def parse_excel_to_learning_modules(args, topic_config) -> List[LearningModule]:
    learning_module_list: List[LearningModule] = []
    file = args.excel_file[0]
    config_df = pandas.read_excel(file, sheet_name='Learning Modules')
    ref_id_col_name = '*Reference ID (1-9 if less than 10 modules, otherwise 01-xx, ' \
                      'for ordering the modules and for referencing in the subsequent sheets)'

    for index, row in config_df.iterrows():
        if pandas.isna(row['*Learning Module Name']):
            raise TypeError('Learning Module Name is missing at row ' + str(index + 2))
        if pandas.isna(row[ref_id_col_name]):
            raise TypeError('Reference ID is missing at row ' + str(index + 2))

        name = row['*Learning Module Name']
        reference_id = topic_config.orgId + '-' + topic_config.topicId + ':module-' + str(row[ref_id_col_name])
        description = None
        objectives = None

        if not pandas.isna(row['Description to Be Displayed']):
            description = row['Description to Be Displayed']

        if not pandas.isna(row['Objectives to Be Displayed']):
            objectives = row['Objectives to Be Displayed']

        module = LearningModule(reference_id, name, description, objectives)

        learning_module_list.append(module)

    learning_module_list.sort(reverse=False, key=return_ref_id)
    return learning_module_list


def return_ref_id(m: LearningModule):
    return m.referenceId
