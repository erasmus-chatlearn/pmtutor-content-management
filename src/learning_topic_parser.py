import argparse
import sys

import jsonpickle

from parsers.meta_questions_parser import parse_excel_to_meta_questions
from cloudant_models.documents import Documents
from parsers.meta_exercises_parser import parse_excel_to_meta_exercises
from parsers.learning_modules_parser import parse_excel_to_learning_modules
from parsers.associations_parser import add_questions_to_exercises
from parsers.topic_config_parser import parse_excel_to_topic_config
from parsers.meta_learning_materials_parser import parse_excel_meta_learning_materials
from parsers.self_assessment_statements_parser import parse_excel_to_self_assessment_statements


def main():
    print("Starting learning topic parser...")
    try:
        args = parse_args()
        docs = parse_excel_to_documents(args)
        docs_json = jsonpickle.encode(docs, unpicklable=False)
        with open("output/parsed-result.json", "w") as outfile:
            outfile.write(docs_json)
        # print(f"Program terminating with exit code {res}")
        sys.exit("done")
    except RuntimeError as e:
        # Errors from argument parsing and ui creation are caught here
        print(e)


def parse_args():
    parser = argparse.ArgumentParser(description='The program parses \
        an excel file and attempts to convert it into a json object')
    parser.add_argument('excel_file', metavar='excel_file', nargs=1,
                        help='The excel file containing questions')
    args = parser.parse_args()
    return args


def parse_excel_to_documents(args) -> Documents:
    documents = Documents([])

    topic_config = parse_excel_to_topic_config(args)
    topic_config.learningModules = parse_excel_to_learning_modules(args, topic_config)

    meta_learning_materials = parse_excel_meta_learning_materials(args, topic_config)

    meta_exercises = parse_excel_to_meta_exercises(args, topic_config)
    meta_questions = parse_excel_to_meta_questions(args)
    add_questions_to_exercises(meta_questions, meta_exercises)

    self_assessment_statements = parse_excel_to_self_assessment_statements(args, topic_config)

    documents.docs.append(topic_config)

    for lm in meta_learning_materials:
        documents.docs.append(lm.learning_material)

    for e in meta_exercises:
        documents.docs.append(e.exercise)

    documents.docs.extend(self_assessment_statements)

    return documents


if __name__ == '__main__':
    main()
