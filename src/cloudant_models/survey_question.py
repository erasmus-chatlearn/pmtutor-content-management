from typing import List
from .option_without_annotation import OptionWithoutAnnotation
import pandas


class SurveyQuestion:
    def __init__(self,
                 reference_id,
                 question_type,
                 description,
                 expected_input_type,
                 option_header,
                 options: List[OptionWithoutAnnotation],
                 is_self_assessment_statement):
        self.questionType = question_type
        self.description = description
        self.referenceId = reference_id
        self.isSelfAssessmentStatement = is_self_assessment_statement
        self.expectedInputType = expected_input_type
        if self.questionType == 'open':
            self.optionHeader = None
            self.options = None
        else:
            if pandas.isna(option_header):
                self.optionHeader = 'Please select an answer below:'
            else:
                self.optionHeader = option_header
            self.options = options


