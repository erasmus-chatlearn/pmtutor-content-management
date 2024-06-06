from cloudant_models.exercise import Exercise


class MetaExercise:
    def __init__(self, reference_id, exercise: Exercise):
        self.referenceId = reference_id
        self.exercise = exercise
