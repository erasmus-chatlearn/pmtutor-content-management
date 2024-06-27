import argparse
import json
import sys
from validators.cloudant_docs_validator import (check_docs_have_given_properties,
                                                check_expected_doc_exists_with_given_property_and_value,
                                                check_all_docs_share_given_partition_key)
from cloudant_db.utilities import (get_db_name_from_env, confirm_database_environment_variable,
                                   get_docs_by_partition_key, post_documents_to_topic_db,
                                   create_bulk_docs_for_deletion_from_database_result)


def main():
    print('\nStart Case Study Uploader...')

    try:
        args = parse_args()
        with open(args.json_file[0], 'r') as file:
            file_dict = json.loads(file.read())
        # Check if the json is about case study:
        # All docs should have _id and docType.
        # Check there is one and only one doc with docType caseStudyConfig.
        # Check each document share a partition key,
        #  so they can be deleted together by the partition key if needed
        print('\nCheck case study json...')
        validate_case_study_dict(file_dict)

        confirm_database_environment_variable()

        topic_db_name = get_db_name_from_env()
        case_study_partition_key = get_case_study_partition_key(file_dict)
        # check if there are existing documents sharing the same partition key
        print(f'\nCheck if there are existing cloudant documents '
              f'sharing the partition key "{case_study_partition_key}"...')
        has_existing_docs = check_if_there_are_existing_case_study_docs_with_given_partition_key(
            topic_db_name, case_study_partition_key)

        if has_existing_docs:
            # Ask if the user want to delete the existing documents and create new ones.
            # Abort if the user doesn't want to delete existing ones and create new documents.
            # If the user proceeds, delete existing case study documents, i.e., docs sharing the same partition key
            # and create new docs.
            result = replace_all_existing_case_study_documents(topic_db_name, file_dict, case_study_partition_key)
        else:
            # Ask the user and if the user confirms,
            # create new case study documents if no existing documents sharing the same key.
            result = create_new_case_study_documents(topic_db_name, file_dict)

        print_final_result(result)

        sys.exit('\nCase Study Uploader is completed.')
    except (AssertionError, AttributeError) as e:
        print(f'\n\nCase Study Uploader has aborted due to {e.__class__.__name__}: {e}')
        sys.exit()


def parse_args():
    parser = argparse.ArgumentParser(
        description='Case Study Uploader uploads a valid case study JSON to the topic database.'
    )
    parser.add_argument('json_file', metavar='json_file', nargs=1,
                        help='The resulted json file from case_study_parser.py')
    args = parser.parse_args()
    return args


def validate_case_study_dict(case_study_dict):

    print('Check if each doc has _id and docType:', end=' ')
    expected_properties = ('_id', 'docType')
    check_docs_have_given_properties(case_study_dict, expected_properties)
    print('OK!')

    doc_property = 'docType'
    expected_value = 'caseStudyConfig'
    n_expected_docs = 1
    if n_expected_docs <= 1:
        print(f'Check if there is {n_expected_docs} doc whose {doc_property} is "{expected_value}":', end=' ')
    else:
        print(f'Check if there are {n_expected_docs} docs whose {doc_property} is "{expected_value}":', end=' ')
    check_expected_doc_exists_with_given_property_and_value(
        case_study_dict, doc_property, expected_value, n_expected_docs)
    print('OK!')

    case_study_config_id = [doc['_id'] for doc in case_study_dict['docs'] if doc['docType'] == 'caseStudyConfig'][0]
    case_study_partition_key = case_study_config_id.split(':')[0]
    print(f'Check if all docs share the same partition key "{case_study_partition_key}":', end=' ')
    check_all_docs_share_given_partition_key(case_study_dict, case_study_partition_key)
    print('OK!')


def check_if_there_are_existing_case_study_docs_with_given_partition_key(topic_db, p_key) -> bool:
    db_result = get_docs_by_partition_key(topic_db, p_key, False)
    assert 'rows' in db_result, f'Something went wrong when querying the database, got {db_result}'
    has_existing_docs = False
    msg = f'There are no documents in "{topic_db}" matching the partition key.'
    if len(db_result['rows']) == 1:
        has_existing_docs = True
        msg = f'There is {str(len(db_result["rows"]))} document in "{topic_db}" matching the partition key.'
    elif len(db_result['rows']) > 1:
        has_existing_docs = True
        msg = f'There are {str(len(db_result["rows"]))} documents in "{topic_db}" matching the partition key.'
    print(msg)

    if has_existing_docs:
        msg = 'The id of existing document is listed below:' \
            if len(db_result['rows']) == 1 else 'The ids of existing documents are listed below:'
        print(msg)
        for row in db_result['rows']:
            print(row['id'])

    return has_existing_docs


def get_case_study_partition_key(case_study_dict):
    case_study_config_doc_id = [doc['_id'] for doc in case_study_dict['docs'] if doc['docType'] == 'caseStudyConfig'][0]
    return case_study_config_doc_id.split(':')[0]


def create_new_case_study_documents(topic_db, case_study_dict):
    p_key = get_case_study_partition_key(case_study_dict)

    print('\n*********************************************************************************************************')
    msg = (f'You are about to create {str(len(case_study_dict["docs"]))} '
           f'new document(s) on "{topic_db}" for a case study using the partition key "{p_key}".')
    print(msg)
    print('*********************************************************************************************************')

    msg = '\nAre you ready? Type YES to proceed, other keys to abort.\n'
    user_input = input(msg)

    msg = 'You aborted the process, nothing has been uploaded.'
    assert user_input == 'YES', msg

    print('\nCreate new documents based on the json file...')
    return post_documents_to_topic_db(topic_db, case_study_dict)


def replace_all_existing_case_study_documents(topic_db, case_study_dict, partition_key):
    print('\n*********************************************************************************************************')
    msg = (f'You are about to replace all existing documents using the partition key "{partition_key}" on "{topic_db}" '
           f'with {str(len(case_study_dict["docs"]))} document(s) from your json file.')
    print(msg)
    print('*********************************************************************************************************')

    msg = '\nAre you ready? Type YES to proceed, other keys to abort.\n'
    user_input = input(msg)

    msg = 'You aborted the process, no changes have been made.'
    assert user_input == 'YES', msg

    print(f'\nDelete existing documents by the partition key "{partition_key}"...')
    # return post_documents_to_topic_db(topic_db, case_study_dict)
    existing_docs = get_docs_by_partition_key(topic_db, partition_key, False)
    bulk_doc_for_deletion = create_bulk_docs_for_deletion_from_database_result(existing_docs)
    deletion_result = post_documents_to_topic_db(topic_db, bulk_doc_for_deletion)
    msg = f'{str(len(deletion_result))} document is deleted.' if len(deletion_result) == 1 \
        else f'{str(len(deletion_result))} are deleted.'
    print(msg)

    print('\nCreate new documents based on the json file...')
    return post_documents_to_topic_db(topic_db, case_study_dict)


def print_final_result(result):
    n_created_docs = len(result)
    if n_created_docs == 0:
        print(f'No document is created.')
    elif n_created_docs == 1:
        print(f'Document "{result[0]["id"]}" is created.')
    else:
        print(f'{str(len(result))} documents are created, ids are listed below:')
        for doc in result:
            print(doc['id'])


if __name__ == '__main__':
    main()
