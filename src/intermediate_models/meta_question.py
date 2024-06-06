from cloudant_models.question import Question


class MetaQuestion:
    def __init__(self, reference_id, question: Question):
        self.reference_id = reference_id
        self.question = question
