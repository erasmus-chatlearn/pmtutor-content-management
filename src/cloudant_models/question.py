import pandas as pd
from typing import List
from .option import Option


class Question:
    def __init__(
            self,
            description,
            image_url,
            option_header,
            options: List[Option],
            answer: Option,
            feedback_for_correct_answer,
            feedback_for_incorrect_answer,
            reference_id):
        self.description = description

        if type(image_url) == str:
            self.imageUrl = image_url
        else:
            self.imageUrl = None

        if pd.isna(option_header):
            self.optionHeader = 'Please select your answer:'
        else:
            self.optionHeader = option_header

        self.options = options
        self.answer = answer

        self.feedbackForCorrectAnswer = None if pd.isna(feedback_for_correct_answer) else feedback_for_correct_answer

        if pd.isna(feedback_for_incorrect_answer):
            self.feedbackForIncorrectAnswer = None
        else:
            self.feedbackForIncorrectAnswer = feedback_for_incorrect_answer
        
        self.referenceId = reference_id
