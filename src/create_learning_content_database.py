import argparse
import json
from cloudant_db.utilities import create_cloudant_database, create_search_index, get_database_info
from ibm_cloud_sdk_core import ApiException

def main():
    args = parse_args()
    db_name = args.new_database_name
    print(f"Start creating a cloudant database for learning topics, case studies, and self-assessment surveys: {db_name}")
    try:
        create_cloudant_database(db_name, True)

        design_doc_name = 'globalIndexes'
        index_name = 'byDocType'
        fields = ['docType']
        is_partitioned_index = False
        create_search_index(db_name, design_doc_name,index_name,fields,is_partitioned_index)

        design_doc_name = 'partitionedIndexes'
        index_name = 'partitionedIndexByDocType'
        is_partitioned_index = True
        create_search_index(db_name, design_doc_name, index_name, fields, is_partitioned_index)

        design_doc_name = 'partitionedIndexes'
        index_name = 'partitionedIndexByIsActive'
        fields = ['isActive']
        is_partitioned_index = True
        create_search_index(db_name, design_doc_name, index_name, fields, is_partitioned_index)

        db_info = get_database_info(db_name)
        db_info = json.dumps(db_info, indent=4)
        print(f'\nDatabase {db_name} and search indexes are created:')
        print(db_info)
    except ApiException as api_err:
        print('\nGot an ApiException, please see the details below.')
        print(api_err)


def parse_args():
    parser = argparse.ArgumentParser(description='This script creates a new partitioned cloudant database with needed \
                                                 design documents for the configurations of learning topics, \
                                                 case studies, and self-assessment surveys')
    parser.add_argument('new_database_name', help='Give the name of the new database')
    return parser.parse_args()


if __name__ == '__main__':
    main()
