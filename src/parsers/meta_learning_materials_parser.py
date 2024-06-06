from typing import List
import pandas
from intermediate_models.meta_learning_material import MetaLearningMaterial
from cloudant_models.learning_material import LearningMaterial
from cloudant_models.topic_config import TopicConfig
from cloudant_models.learning_module import LearningModule


def parse_excel_meta_learning_materials(args, topic_config) -> List[MetaLearningMaterial]:
    meta_learning_materials: List[MetaLearningMaterial] = []
    file = args.excel_file[0]
    config_df = pandas.read_excel(file, sheet_name='Learning Materials', header=1)


    for i, row in config_df.iterrows():
        
        name = row['*Learning Material Name']
        description = row['*Description to Be Displayed']
        source_url = row['*Source Url']
        level = row['*Level (1 to 5, 1 being the easiest, whereas 5 being the most advanced)']
        format = row['*Format (pdf, html, or video)']
        reference_id = row['*Reference ID (<Learning Module Ref. ID>-mat-<order in the module, 1-9>)']
        _id = topic_config.orgId + '-' + topic_config.topicId + ':' + row['*Reference ID (<Learning Module Ref. ID>-mat-<order in the module, 1-9>)']
        topic_config_id = topic_config._id
        
        learning_module_reference_id = None
        for index, lm in enumerate(topic_config.learningModules):
            if lm.referenceId.endswith(reference_id.split("-")[0]):
                learning_module_reference_id = lm.referenceId
                # print(learning_module_reference_id)
                break

        lm = LearningMaterial(_id, format, source_url, level, name, description, learning_module_reference_id, topic_config_id )

        meta_learning_material = MetaLearningMaterial(reference_id, lm)

        meta_learning_materials.append(meta_learning_material)

    meta_learning_materials.sort(reverse=False, key=return_ref_id)
    return meta_learning_materials


def return_ref_id(m: MetaLearningMaterial):
    return m.reference_id

