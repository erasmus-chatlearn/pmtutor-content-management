from typing import List

from .survey_question import SurveyQuestion


class SurveySection:
    def __init__(self, reference_id, name, description, questions: List[SurveyQuestion]):
        self.referenceId = reference_id
        self.name = name
        self.description = description
        self.questions = questions
