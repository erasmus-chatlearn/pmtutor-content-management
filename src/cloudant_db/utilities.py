import json
import os
from ibmcloudant.cloudant_v1 import CloudantV1, Document, BulkDocs
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv

load_dotenv()
authenticator = IAMAuthenticator(os.getenv('CLOUDANT_APIKEY'))
service = CloudantV1(authenticator=authenticator)
service.set_service_url(os.getenv('CLOUDANT_URL'))


def get_db_name_from_env() -> str:
    return os.getenv('DATABASE_NAME')


def print_cloudant_env_variables():
    print(os.getenv('CLOUDANT_URL'))
    print(os.getenv('CLOUDANT_APIKEY'))
    print(os.getenv('DATABASE_NAME'))


def print_capacity_throughput_information():
    response = service.get_capacity_throughput_information().get_result()
    print(json.dumps(response, indent=2))


def print_all_dbs_info():
    db_list = service.get_all_dbs().get_result()
    response = service.post_dbs_info(keys=db_list).get_result()
    print(json.dumps(response, indent=2))


def create_cloudant_database(new_db_name, is_partitioned):
    return service.put_database(db=new_db_name, partitioned=is_partitioned).get_result()


def get_database_info(db_name):
    return service.get_database_information(db=db_name).get_result()


def create_search_index(db_name, design_doc_name, index_name, index_fields, is_partitioned_index):
    index = {'fields': index_fields}
    return service.post_index(
        db=db_name, ddoc=design_doc_name, name=index_name, index=index, type='json', partitioned=is_partitioned_index)


def post_documents_to_topic_db(db_name, docs) -> []:
    response = service.post_bulk_docs(
        db=db_name,
        bulk_docs=docs
    ).get_result()
    return response


def get_docs_by_partition_key(db_name, partition_key, include_docs) -> []:
    response = service.post_partition_all_docs(
        db=db_name,
        partition_key=partition_key,
        include_docs=include_docs
    ).get_result()
    return response


def create_bulk_docs_from_docs_result_rows_for_deletion(docs_result_rows) -> BulkDocs:
    bulk_docs = BulkDocs(docs=[])
    for row in docs_result_rows['rows']:
        doc = Document(
            id=row['id'],
            rev=row['value']['rev'],
            deleted=True
        )
        bulk_docs.docs.append(doc)
    return bulk_docs


def get_docs_by_partition_key_excluding_a_given_doc_type(db_name, partition_key, excluding_doc_type):
    response = service.post_partition_find(
        db=db_name,
        partition_key=partition_key,
        selector={
            "$not": {
                "docType": excluding_doc_type
            }
        }
    ).get_result()
    return response


def create_bulk_docs_for_deletion_from_database_result(db_result) -> BulkDocs:
    bulk_docs = BulkDocs(docs=[])

    if 'rows' in db_result:
        for row in db_result['rows']:
            doc = Document(
                id=row['id'],
                rev=row['value']['rev'],
                deleted=True
            )
            bulk_docs.docs.append(doc)
    if 'docs' in db_result:
        for document in db_result['docs']:
            doc = Document(
                id=document['_id'],
                rev=document['_rev'],
                deleted=True
            )
            bulk_docs.docs.append(doc)
    return bulk_docs


def get_docs_by_partition_key_and_a_given_doc_type(db_name, partition_key, doc_type):
    response = service.post_partition_find(
        db=db_name,
        partition_key=partition_key,
        selector={
            "docType": doc_type
        }
    ).get_result()
    return response


def get_active_docs_by_doc_type_and_scope(db_name, doc_type, scope):
    response = service.post_find(
        db=db_name,
        selector={
            "docType": doc_type,
            "scope": scope,
            "isActive": True
        }
    ).get_result()
    return response


def get_docs_by_doc_type(db_name, doc_type):
    return service.post_find(
        db=db_name,
        selector={
            "docType": doc_type
        }
    ).get_result()


def get_all_topic_config_id_and_name(db_name):
    return service.post_find(
        db=db_name,
        fields=['_id', 'name'],
        selector={'docType': 'topicConfig'}
    ).get_result()


def get_active_surveys_by_partition_key(db_name, partition_key, survey_type):
    return service.post_partition_find(
        db=db_name,
        partition_key=partition_key,
        selector={
            'surveyType': survey_type,
            'isActive': True
        }
    ).get_result()


def put_a_document(db_name, doc):
    return service.post_document(
        db=db_name,
        document=doc
    ).get_result()


def confirm_database_environment_variable():
    print(f'\nThe environment variable for database name is "{get_db_name_from_env()}"')
    expected_input = 'YES'
    sys_msg = (f'Is it the correct database you want to manage the documents? '
               f'Enter {expected_input} to proceed, other keys to abort.\n')
    err_msg = "You can change to a different database by updating the DATABASE_NAME in .env"
    user_input = input(sys_msg)
    assert user_input == expected_input, err_msg

