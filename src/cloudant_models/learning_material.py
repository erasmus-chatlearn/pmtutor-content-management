import pandas as pd


class LearningMaterial:
    def __init__(self, _id, format, source_url, level, name, description, learning_module_reference_id, topic_config_id):
        self._id = _id
        self.format = format
        self.docType = 'learningMaterial'
        self.sourceUrl = source_url
        self.level = level
        self.name = name
        
        if pd.isna(description):
            self.description = None
        else:
            self.description = description
        
        self.learningModuleReferenceId = learning_module_reference_id
        self.topicConfigId = topic_config_id
