class ContentElement:
    def __init__(self,
                 parent_id,
                 spread_sheet_ref_id,
                 content_element_type,
                 description,
                 source_url,
                 additional_learning_material_ids):
        self.parentId = parent_id
        self.spreadSheetRefId = spread_sheet_ref_id
        self.contentElementType = content_element_type
        self.description = description
        self.sourceUrl = source_url
        self.additionalLearningMaterialIds = additional_learning_material_ids

