import argparse
import json
import sys
from json import JSONDecodeError

import pandas

from validators.validation_message import ValidationMessage
from cloudant_db.utilities import get_db_name_from_env, put_a_document, \
    post_documents_to_topic_db, get_docs_by_partition_key
from parsers.parser_utilities import get_now_in_unix_milliseconds

topic_db_name = get_db_name_from_env()


def main():
    print('\nStart Survey Uploader...')
    try:
        args = parse_args()
        with open(args.json_file[0], 'r') as file:
            file_dict = json.loads(file.read())

        input_validation(file_dict)

        print('\n******************** '
              'Check if there is any existing survey sharing the same partition key'
              ' ********************')
        partition_key = file_dict['_id'].split(':')[0]
        print('Partition key in json survey id: "' + partition_key + '"')
        existing_surveys = get_docs_by_partition_key(topic_db_name, partition_key, True)
        if 'error' in existing_surveys:
            raise AssertionError(existing_surveys['error'])
        elif 'rows' in existing_surveys and len(existing_surveys['rows']) == 0:
            print('There is no document sharing the same partition key.')
            create_a_new_survey_document(topic_db_name, file_dict)
        elif 'rows' in existing_surveys and len(existing_surveys['rows']) > 0:
            doc_with_same_id, other_active_surveys = analyze_existing_survey_documents(existing_surveys['rows'],
                                                                                       file_dict['_id'])
            user_input = input('\nWhat would you like to do?'
                               + create_prompt(doc_with_same_id, other_active_surveys) +
                               '\nenter other key to abort the process.\n')
            handle_user_input(user_input, file_dict, doc_with_same_id, other_active_surveys)
        sys.exit('\nSurvey Uploader is completed.')
    except (AssertionError, JSONDecodeError) as e:
        print('\nSurvey Uploader has aborted due to ' + e.__class__.__name__ + ':')
        sys.exit(e)


def parse_args():
    parser = argparse.ArgumentParser(description='Survey Uploader uploads a valid survey JSON to the topic database.')
    parser.add_argument('json_file', metavar='json_file', nargs=1,
                        help='The resulted json file from survey_parser.py')
    args = parser.parse_args()
    return args


def validate_survey_dictionary(survey_dict) -> ValidationMessage:
    survey_properties, section_properties, question_properties, option_properties = get_expected_survey_properties()

    print('\nCheck survey properties...')
    result = check_has_expected_properties(survey_dict, survey_properties)

    if result.is_valid:
        print('ok')
        print('\nCheck survey missing values...')
        result = check_survey_missing_values(survey_dict, survey_properties)

    if result.is_valid:
        print('ok')
        print('\nCheck survey sections...')
        for i, section in enumerate(survey_dict[survey_properties[6]]):
                print('\nCheck survey sections[' + str(i) + ']...')
                result = check_survey_section(section, section_properties, question_properties, option_properties)
                if result.is_valid is False:
                    break
                print('\nSurvey sections[' + str(i) + '] ok')

    return result


def get_expected_survey_properties():
    survey_properties = ('_id', 'docType', 'orgId', 'surveyType', 'name', 'description', 'sections', 'isActive',
                         'createdAt', 'updatedAt')
    section_properties = ('referenceId', 'name', 'description', 'questions')
    question_properties = ('questionType', 'description', 'optionHeader', 'options', 'referenceId',
                           'isSelfAssessmentStatement', 'expectedInputType')
    option_properties = ('label', 'value')
    return survey_properties, section_properties, question_properties, option_properties


def check_has_expected_properties(dictionary, expected_properties) -> ValidationMessage:
    result = ValidationMessage(True, 'It has all expected properties.')
    for p in expected_properties:
        if p not in dictionary:
            result.is_valid = False
            result.message = 'Property "' + p + '" is missing.'
            break
    return result


def check_list_items_have_expected_properties(list_name, list_items, expected_properties) -> ValidationMessage:
    if list_items is None or len(list_items) == 0:
        return ValidationMessage(False, 'There is no ' + list_name)

    result = None
    i = 0
    for item in list_items:
        print('\nCheck ' + list_name + '[' + str(i) + ']...')
        result = check_has_expected_properties(item, expected_properties)
        if result.is_valid is False:
            return result
        i += 1

    return result


def check_survey_missing_values(survey, expected_survey_properties) -> ValidationMessage:
    result = ValidationMessage(True, 'Survey has all the required values')
    if pandas.isna(survey[expected_survey_properties[0]]):
        result.is_valid = False
        result.message = 'Survey ' + expected_survey_properties[0] + ' property has missing value.'
    elif pandas.isna(survey[expected_survey_properties[1]]):
        result.is_valid = False
        result.message = 'Survey ' + expected_survey_properties[1] + ' property has missing value.'
    elif pandas.isna(survey[expected_survey_properties[2]]):
        result.is_valid = False
        result.message = 'Survey ' + expected_survey_properties[2] + ' property has missing value.'
    elif pandas.isna(survey[expected_survey_properties[3]]):
        result.is_valid = False
        result.message = 'Survey ' + expected_survey_properties[3] + ' property has missing value.'
    elif pandas.isna(survey[expected_survey_properties[4]]):
        result.is_valid = False
        result.message = 'Survey ' + expected_survey_properties[4] + ' property has missing value.'
    elif pandas.isna(survey[expected_survey_properties[5]]):
        result.is_valid = False
        result.message = 'Survey ' + expected_survey_properties[5] + ' property has missing value.'
    elif survey[expected_survey_properties[6]] is None or \
            type(survey[expected_survey_properties[6]]) is not list or len(survey[expected_survey_properties[6]]) == 0:
        result.is_valid = False
        result.message = 'Survey should have at least one section.'
    elif pandas.isna(survey[expected_survey_properties[7]]):
        result.is_valid = False
        result.message = 'Survey ' + expected_survey_properties[7] + ' property has missing value.'
    elif pandas.isna(survey[expected_survey_properties[8]]):
        result.is_valid = False
        result.message = 'Survey ' + expected_survey_properties[8] + ' property has missing value.'
    return result


def check_survey_section(section, expected_section_properties,
                         expected_question_properties, expected_option_properties) -> ValidationMessage:
    result = check_has_expected_properties(section, expected_section_properties)
    if result.is_valid:
        if pandas.isna(section[expected_section_properties[0]]):
            result.is_valid = False
            result.message = 'Section ' + expected_section_properties[0] + ' property has missing value.'
        elif pandas.isna(section[expected_section_properties[1]]):
            result.is_valid = False
            result.message = 'Section ' + expected_section_properties[1] + ' property has missing value.'
        elif section[expected_section_properties[3]] is None or \
                type(section[expected_section_properties[3]]) is not list or \
                len(section[expected_section_properties[3]]) == 0:
            result.is_valid = False
            result.message = 'A survey section should have questions.'
        else:
            for i, question in enumerate(section[expected_section_properties[3]]):
                print('\nCheck questions[' + str(i) + ']...')
                result = check_survey_question(question, expected_question_properties, expected_option_properties)
                if result.is_valid is False:
                    break
    return result


def check_survey_question(question, expected_question_properties,
                          expected_option_properties) -> ValidationMessage:
    result = check_has_expected_properties(question, expected_question_properties)
    if result.is_valid:
        result = check_question_missing_values(question, expected_question_properties)
        if result.is_valid and question[expected_question_properties[0]] == 'singleSelect':
            print('It is a single-select question.')
            for i, option in enumerate(question[expected_question_properties[3]]):
                print('Check options[' + str(i) + ']...')
                result = check_option(option, expected_option_properties)
                if result.is_valid is False:
                    break
    return result


def check_question_missing_values(question, expected_question_properties) -> ValidationMessage:
    result = ValidationMessage(True, 'The question has all required values')
    if pandas.isna(question[expected_question_properties[0]]):
        result.is_valid = False
        result.message = 'Question ' + expected_question_properties[0] + ' property has missing value.'
    elif pandas.isna(question[expected_question_properties[1]]):
        result.is_valid = False
        result.message = 'Question ' + expected_question_properties[1] + ' property has missing value.'
    elif pandas.isna(question[expected_question_properties[4]]):
        result.is_valid = False
        result.message = 'Question ' + expected_question_properties[4] + ' property has missing value.'
    elif pandas.isna(question[expected_question_properties[5]]):
        result.is_valid = False
        result.message = 'Question ' + expected_question_properties[5] + ' property has missing value.'
    elif pandas.isna(question[expected_question_properties[6]]):
        result.is_valid = False
        result.message = 'Question ' + expected_question_properties[6] + ' property has missing value.'
    elif question[expected_question_properties[0]] == 'singleSelect' and \
            (question[expected_question_properties[3]] is None or
             type(question[expected_question_properties[3]]) is not list or
             len(question[expected_question_properties[3]]) == 0):
        result.is_valid = False
        result.message = 'Single-select question should have at least one option.'
    return result


def check_option(option, expected_properties) -> ValidationMessage:
    result = check_has_expected_properties(option, expected_properties)
    if result.is_valid is True and pandas.isna(option[expected_properties[0]]):
        result.is_valid = False
        result.message = 'Option ' + expected_properties[0] + ' property has missing value.'
    elif result.is_valid is True and pandas.isna(option[expected_properties[1]]):
        result.is_valid = False
        result.message = 'Option ' + expected_properties[1] + ' property has missing value.'
    return result


def deactivate_survey_documents(documents):
    print('\n******************** '
          'Deactivate active survey document(s)'
          ' ********************')
    for doc in documents:
        doc['isActive'] = False
        doc['updatedAt'] = get_now_in_unix_milliseconds()
    result = post_documents_to_topic_db(topic_db_name, {'docs': documents})
    if 'error' in result:
        raise AssertionError('Encountered an error when updating active survey documents: ' + result['error'])
    print(result)


def analyze_existing_survey_documents(doc_list, json_survey_id):
    doc_with_same_id = None
    other_active_surveys = []

    for doc in doc_list:
        if doc['doc']['_id'] == json_survey_id:
            doc_with_same_id = doc['doc']
        elif doc['doc']['isActive']:
            other_active_surveys.append(doc['doc'])

    if doc_with_same_id is not None:
        print('There is a survey document with the same id: "' + json_survey_id + '"')
        if doc_with_same_id['isActive']:
            print('The document is active.')
        else:
            print('The document is inactive.')

    if len(other_active_surveys) > 0:
        print('There is ' + str(len(other_active_surveys)) +
              ' other active document(s) sharing the same partition key.')
    else:
        print('There is no other active document sharing the same partition key.')

    return doc_with_same_id, other_active_surveys


def create_prompt(same_id_doc, other_active_surveys) -> str:
    prompt = '\nType "create" to create a new survey document, '
    if same_id_doc is None and len(other_active_surveys) > 0:
        prompt += '\ntype "update" to update the latest active survey document with the json input, '
    elif same_id_doc is not None and len(other_active_surveys) == 0:
        prompt = '\nType "update" to update the existing document, '
    elif same_id_doc is not None and len(other_active_surveys) > 0:
        prompt = '\nType "update" to update the existing document and deactivate other active document(s), '
    return prompt


def prepare_json_dict_for_update(json_dict, existing_doc):
    # print(existing_doc)
    json_dict['_id'] = existing_doc['_id']
    json_dict['_rev'] = existing_doc['_rev']
    json_dict['createdAt'] = existing_doc['createdAt']
    json_dict['updatedAt'] = get_now_in_unix_milliseconds()
    return json_dict


def input_validation(file_dict):
    print('\n******************** Validate input file ********************')
    validation_result = validate_survey_dictionary(file_dict)
    if validation_result.is_valid is False:
        raise AssertionError(validation_result.message)
    print('\nThe input file seems valid.')


def create_a_new_survey_document(db_name, file_dict):
    print('\n******************** '
          'Create a new survey document'
          ' ********************')
    db_result = put_a_document(db_name, file_dict)
    print('A new survey document is created.')
    print(db_result)


def update_survey_document(file_dict, doc_with_same_id, other_active_surveys):
    print('\n******************** '
          'Update an existing survey document'
          ' ********************')
    if doc_with_same_id is not None:
        file_dict = prepare_json_dict_for_update(file_dict, doc_with_same_id)
    elif len(other_active_surveys) == 1:
        file_dict = prepare_json_dict_for_update(file_dict, other_active_surveys[0])
    elif len(other_active_surveys) > 1:
        raise AssertionError('There are more than one active surveys!')
    else:
        raise AssertionError('There is no document to be updated!')
    db_result = put_a_document(topic_db_name, file_dict)
    print(db_result)


def handle_user_input(user_input, file_dict, doc_with_same_id, other_active_surveys):
    if user_input == 'update':
        update_survey_document(file_dict, doc_with_same_id, other_active_surveys)
    elif user_input == 'create':
        if doc_with_same_id is not None:
            raise AssertionError('There is a document with the same id!')
        if len(other_active_surveys) > 0:
            deactivate_survey_documents(other_active_surveys)
            create_a_new_survey_document(topic_db_name, file_dict)
    else:
        print('\nYou chose to abort the process.')
        print('No document is created or updated.')


if __name__ == '__main__':
    main()
