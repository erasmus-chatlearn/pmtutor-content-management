class QuestionV2:
    def __init__(self,
                 reference_id,
                 description,
                 image_url,
                 option_header,
                 options,
                 answer,
                 feedback_for_correct_answer,
                 feedback_for_incorrect_answer,
                 additional_learning_material_id,
                 tags):
        self.referenceId = reference_id
        self.description = description
        self.imageUrl = image_url
        self.optionHeader = option_header
        self.options = options
        self.answer = answer
        self.feedbackForCorrectAnswer = feedback_for_correct_answer
        self.feedbackForIncorrectAnswer = feedback_for_incorrect_answer
        self.additionalLearningMaterialId = additional_learning_material_id
        self.tags = tags
