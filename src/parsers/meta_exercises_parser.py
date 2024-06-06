from typing import List
import pandas
from cloudant_models.exercise import Exercise
from cloudant_models.question import Question
from intermediate_models.meta_exercise import MetaExercise
from parsers.meta_questions_parser import get_reference_id_from_question_id
from cloudant_models.topic_config import TopicConfig
from cloudant_models.learning_module import LearningModule


def parse_excel_to_meta_exercises(args, topic_config) -> List[MetaExercise]:
    meta_exercise_list: List[MetaExercise] = []
    file = args.excel_file[0]
    config_df = pandas.read_excel(file, sheet_name='Exercises', header=1)


    for i, row in config_df.iterrows():
        description = row['Description to Be Displayed Before the Exercise']
        if pandas.isna(description):
            description = None
        objectives = row['Objective to Be Displayed Before the Exercise']
        if pandas.isna(objectives):
            objectives = None

        questions = []
        reference_id = row['*Reference ID (<Learning Module Ref. ID>.<order in the module, 1-9>)']
        _id = topic_config.orgId + '-' + topic_config.topicId + ':' + str(reference_id)
        topic_config_id = topic_config._id
        learning_module_reference_id = topic_config.orgId + '-' + topic_config.topicId + ':module-' + str(reference_id)[0].split(".")[0]
        # print(learning_module_reference_id)
        
        
        exercise = Exercise(
            _id,
            row['*Exercise Name'],
            description,
            objectives,
            row['*Level'],
            questions,
            learning_module_reference_id,
            topic_config_id,
        )

        meta_exercise = MetaExercise(reference_id, exercise)

        meta_exercise_list.append(meta_exercise)
    meta_exercise_list.sort(reverse=False, key=return_ref_id)
    return meta_exercise_list


def add_questions_to_exercises(questions: List[Question], exercises: List[Exercise]):
    for q in questions:
        ref_id = get_reference_id_from_question_id(q.questionId)
        for e in exercises:
            if e.referenceId == ref_id:
                e.questions.append(q)


def get_level_from_reference_id(reference_id: str) -> int:
    level = 0
    if reference_id == '1.2':
        level = 1
    elif reference_id == '1.3':
        level = 2
    elif reference_id == '1.4':
        level = 3
    return level


def return_ref_id(e: MetaExercise):
    return e.referenceId    
