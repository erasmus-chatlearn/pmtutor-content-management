from cloudant_models.learning_material import LearningMaterial


class MetaLearningMaterial:
    def __init__(self, reference_id, learning_material: LearningMaterial):
        self.reference_id = reference_id
        self.learning_material = learning_material
