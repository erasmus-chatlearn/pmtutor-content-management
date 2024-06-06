from typing import List
from parsers.meta_questions_parser import get_reference_id_from_question_id
from cloudant_models.learning_module import LearningModule
from cloudant_models.topic_config import TopicConfig
from intermediate_models.meta_exercise import MetaExercise
from intermediate_models.meta_question import MetaQuestion


def add_questions_to_exercises(questions: List[MetaQuestion], exercises: List[MetaExercise]):
    for q in questions:
        exercise_ref_id = get_reference_id_from_question_id(q.reference_id)
        for e in exercises:
            if exercise_ref_id == str(e.referenceId):
                e.exercise.questions.append(q.question)
