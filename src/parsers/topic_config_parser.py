from typing import List
import pandas
from cloudant_models.topic_config import TopicConfig


def parse_excel_to_topic_config(args) -> TopicConfig:
    file = args.excel_file[0]
    config_df = pandas.read_excel(file, sheet_name='Topic')

    if pandas.isna(config_df.loc[config_df.index[0], '*Organization Name']):
        raise TypeError("The value of Organization Name is missing in the Topic sheet")

    if pandas.isna(config_df.loc[config_df.index[0], '*Org ID']):
        raise TypeError("The value of Org ID is missing in the Topic sheet")

    if pandas.isna(config_df.loc[config_df.index[0], '*Topic ID']):
        raise TypeError("The value of Topic ID is missing in the Topic sheet")

    if pandas.isna(config_df.loc[config_df.index[0], '*Topic Name']):
        raise TypeError("The value of Topic Name is missing in the Topic sheet")

    organization_name = config_df.loc[config_df.index[0], '*Organization Name']
    org_id = config_df.loc[config_df.index[0], '*Org ID']
    topic_id = config_df.loc[config_df.index[0], '*Topic ID']
    _id = org_id + '-' + topic_id + ':topicConfig'
    name = config_df.loc[config_df.index[0], '*Topic Name']

    description = None
    objectives = None
    learning_modules = []
    is_available = True
    tags = None

    if not pandas.isna(config_df.loc[config_df.index[0], 'Topic Description to be Displayed by the Bot']):
        description = config_df.loc[config_df.index[0], 'Topic Description to be Displayed by the Bot']

    if not pandas.isna(config_df.loc[config_df.index[0], 'Topic Objectives to Be Displayed']):
        objectives = config_df.loc[config_df.index[0], 'Topic Objectives to Be Displayed']

    if not pandas.isna(config_df.loc[config_df.index[0], 'Is the Topic Available for the Bot to Offer to the Learner']):
        is_available = bool(
            config_df.loc[config_df.index[0], 'Is the Topic Available for the Bot to Offer to the Learner'])
            
    if not pandas.isna(
        config_df.loc[config_df.index[0], 'Tags (optional, nouns separated by comma, attributes that do not exist in the columns of this sheet, for future query purposes)']):
            tags = config_df.loc[config_df.index[0], 'Tags (optional, nouns separated by comma, attributes that do not exist in the columns of this sheet, for future query purposes)']        
    

    return TopicConfig(
        _id,
        organization_name,
        org_id,
        topic_id,
        name,
        description,
        objectives,
        learning_modules,
        is_available,
        tags)