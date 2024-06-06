class Exercise:
    def __init__(self, _id, name, description, objectives, level, questions, learning_module_reference_id, topic_config_id):
        self._id = _id
        self.docType = 'exercise'
        self.name = name
        self.description = description
        self.objectives = objectives
        self.level = level
        self.questions = questions
        self.learningModuleReferenceId = learning_module_reference_id
        self.topicConfigId = topic_config_id
