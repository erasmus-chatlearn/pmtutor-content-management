class LearningMaterialV2:
    def __init__(self, _id, material_format, source_url, level, name, description,
                 learning_module_reference_id, topic_config_id, parent_id, spread_sheet_ref_id):
        self.docType = "learningMaterial"
        self._id = _id
        self.format = material_format
        self.sourceUrl = source_url
        self.level = level
        self.name = name
        self.description = description
        self.learningModuleReferenceId = learning_module_reference_id
        self.topicConfigId = topic_config_id
        self.parentId = parent_id
        self.spreadSheetRefId = spread_sheet_ref_id
