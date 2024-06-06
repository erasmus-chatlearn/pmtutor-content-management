import argparse
import json
import sys
from cloudant_db.utilities import get_db_name_from_env, post_documents_to_topic_db, get_docs_by_partition_key, \
    create_bulk_docs_for_deletion_from_database_result, get_docs_by_partition_key_excluding_a_given_doc_type, \
    get_docs_by_partition_key_and_a_given_doc_type
from parsers.parser_utilities import get_now_in_unix_milliseconds

topic_db_name = get_db_name_from_env()


def main():
    print("Topic Uploader is started...")

    try:
        # load the json file from argument
        args = parse_args()
        with open(args.json_file[0], 'r') as file:
            docs_str = file.read()
            docs_dict = json.loads(docs_str)

        input_validation(docs_dict)

        partition_key = docs_dict['docs'][0]['_id'].split(':')[0]
        existing_docs = get_docs_by_partition_key(topic_db_name, partition_key, include_docs=False)

        if len(existing_docs['rows']) > 0:
            print('\nFound existing document(s) from the database:')
            print(json.dumps(existing_docs, indent=2))
            print('\nThere are totally ' + str(len(existing_docs['rows'])) +
                  ' documents in the database using the same partition key: ' + partition_key)
            # ask if the user want to abort the action or continue to replace all non SAS-type documents and
            # to update existing SAS documents
            user_input = input('\nWould you like to replace all existing non-SAS documents and '
                               'update all existing SAS documents of the same partition key? '
                               '(Type "yes" to continue or any other key to abort)\n')

            if user_input.lower() == 'yes':
                replace_existing_non_sas_documents_of_same_partition_key(partition_key, docs_dict)
                # create or update SAS documents
                create_or_update_sas_documents_of_same_partition_key(partition_key, docs_dict)
            else:
                print('\nAborting the process...')
                print('\nNo documents are changed.')
        else:
            # upload the json to the database if it passes the validation
            print('\nPost the json object to the topic database...')
            post_results = post_documents_to_topic_db(topic_db_name, docs_str)
            print_db_result(post_results, 'created', 'new')

        sys.exit('\nTopic Uploader is finished.')

    except (AssertionError, TypeError) as e:
        print('\nTopic Uploader has exited due to an error:')
        sys.exit(e)


def parse_args():
    parser = argparse.ArgumentParser(description='Topic Uploader uploads a valid JSON to the topic database.')
    parser.add_argument('json_file', metavar='json_file', nargs=1,
                        help='The resulted json file from learning_topic_parser.py')
    args = parser.parse_args()
    return args


def input_validation(dict_object):
    print('\nInput validation...')

    if 'docs' not in dict_object:
        raise AssertionError('"docs" is missing from the json')

    if type(dict_object['docs']) is not list:
        raise AssertionError('"docs" should be an array')

    print('The input object seems valid.')


def replace_existing_non_sas_documents_of_same_partition_key(partition_key, json_dict):
    print('\nReplacing the existing non-SAS documents...')

    excluding_doc_type = 'selfAssessmentStatement'

    # get all existing non-SAS documents using the same partition key
    existing_docs_result = get_docs_by_partition_key_excluding_a_given_doc_type(topic_db_name, partition_key,
                                                                                excluding_doc_type)
    # delete the documents
    bulk_doc = create_bulk_docs_for_deletion_from_database_result(existing_docs_result)
    deletion_result = post_documents_to_topic_db(topic_db_name, bulk_doc)
    print('\nDeleted ' + str(len(deletion_result)) + ' existing documents of the same partition key which are not '+
          excluding_doc_type + '.')

    # create documents using the json dict
    print('\nCreating non-SAS documents...')
    docs_excluding_sas = {'docs': list(filter(lambda doc: doc['docType'] != excluding_doc_type, json_dict['docs']))}
    creation_result = post_documents_to_topic_db(topic_db_name, docs_excluding_sas)
    print_db_result(creation_result, 'created', 'non-SAS')


def create_or_update_sas_documents_of_same_partition_key(partition_key, json_dict):
    print('\nCreate or update SAS documents...')
    # filter parsed sas documents
    sas_doc_type = 'selfAssessmentStatement'
    parsed_sas_docs = {'docs': list(filter(lambda doc: doc['docType'] == sas_doc_type, json_dict['docs']))}
    existing_sas_docs = get_docs_by_partition_key_and_a_given_doc_type(topic_db_name, partition_key, sas_doc_type)
    print('\nThere are ' + str(len(existing_sas_docs['docs'])) + ' existing SAS documents in the database.')
    # create or update SAS documents
    prepared_sas_docs = prepare_sas_docs(parsed_sas_docs, existing_sas_docs)
    if len(prepared_sas_docs['docs']) > 0:
        update_result = post_documents_to_topic_db(topic_db_name, prepared_sas_docs)
        print_db_result(update_result, 'updated or created', 'SAS')
    else:
        print('There is no SAS document to be created or updated.')


def prepare_sas_docs(parsed_sas_docs, existing_sas_docs):
    sas_docs = {'docs': []}
    if len(parsed_sas_docs['docs']) == 0 and len(existing_sas_docs['docs']) == 0:
        return sas_docs
    if len(parsed_sas_docs['docs']) > 0 and len(existing_sas_docs['docs']) == 0:
        return parsed_sas_docs
    if len(parsed_sas_docs['docs']) == 0 and len(existing_sas_docs['docs']) > 0:
        for existing_doc in existing_sas_docs['docs']:
            existing_doc['isActive'] = False
            existing_doc['updatedAt'] = get_now_in_unix_milliseconds()
        return existing_sas_docs
    # if an existing SAS is found in the parsed SAS docs, it is an update by the parsed SAS doc
    # if an existing SAS cannot be found in the docs, the existing SAS should be marked isActive False
    for existing_doc in existing_sas_docs['docs']:
        found_parsed_doc = next(
            (d for d in parsed_sas_docs['docs'] if d['scopeRefId'] == existing_doc['scopeRefId']),
            None
        )
        if found_parsed_doc is not None:
            found_parsed_doc['_id'] = existing_doc['_id']
            found_parsed_doc['_rev'] = existing_doc['_rev']
            found_parsed_doc['updatedAt'] = found_parsed_doc['createdAt']
            found_parsed_doc['createdAt'] = existing_doc['createdAt']
            sas_docs['docs'].append(found_parsed_doc)
        else:
            existing_doc['isActive'] = False
            existing_doc['updatedAt'] = get_now_in_unix_milliseconds()
            sas_docs['docs'].append(existing_doc)
    # if a parsed SAS is found in the sas_docs, it is an update and should not be appended again
    # if a parsed SAS is not found, it is a new document and should be appended to the sas_docs
    for parsed_sas_doc in parsed_sas_docs['docs']:
        found_sas_doc = next(
            (d for d in sas_docs['docs'] if d['scopeRefId'] == parsed_sas_doc['scopeRefId']),
            None
        )
        if found_sas_doc is not None:
            continue
        else:
            sas_docs['docs'].append(parsed_sas_doc)
    return sas_docs


def print_db_result(db_result, action_str, doc_type_str):
    print('\nThe result of ' + action_str + ' ' + doc_type_str + ' document(s):')
    print(json.dumps(db_result, indent=2))
    print('\nTotally ' + str(len(db_result)) + ' ' + doc_type_str + ' document(s) is/are ' + action_str + '.')


if __name__ == '__main__':
    main()
