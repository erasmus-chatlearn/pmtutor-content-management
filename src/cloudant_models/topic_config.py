class TopicConfig:
    def __init__(
            self,
            _id,
            organization_name,
            org_id,
            topic_id,
            name,
            description,
            objectives,
            learning_modules,
            is_available,
            tags):
        self.docType = 'topicConfig'
        self._id = _id
        self.organizationName = organization_name
        self.orgId = org_id
        self.topicId = topic_id
        self.name = name
        self.description = description
        self.objectives = objectives
        self.learningModules = learning_modules
        self.isAvailable = is_available
        self.tags = tags
