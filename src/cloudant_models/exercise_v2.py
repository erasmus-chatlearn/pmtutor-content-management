class ExerciseV2:
    def __init__(self,
                 _id,
                 name,
                 description,
                 objectives,
                 level,
                 questions: list,
                 parent_id,
                 spread_sheet_ref_id,
                 topic_config_id,
                 learning_module_reference_id,
                 solution_id,
                 additional_learning_material_ids):
        self.docType = "exercise"
        self._id = _id
        self.name = name
        self.description = description
        self.objectives = objectives
        self.level = level
        self.questions = questions
        self.parentId = parent_id
        self.spreadSheetRefId = spread_sheet_ref_id
        self.topicConfigId = topic_config_id
        self.learningModuleReferenceId = learning_module_reference_id
        self.solutionId = solution_id
        self.additionalLearningMaterialIds = additional_learning_material_ids

