def check_docs_have_given_properties(documents, properties: tuple):
    for index, doc in enumerate(documents['docs']):
        for p in properties:
            assert p in doc, f'Property {p} is missing in docs[{str(index)}]'


def check_expected_doc_exists_with_given_property_and_value(
        documents, doc_property: str, expected_value, n_expected_docs: int):
    result = [doc for doc in documents['docs'] if doc[doc_property] == expected_value]
    assert len(result) == n_expected_docs, \
        (f'Expect {str(n_expected_docs)} doc(s) with doc["{doc_property}"] == {str(expected_value)}, '
         f'but found {str(len(result))}')


def check_all_docs_share_given_partition_key(documents, expected_partition_key):
    for index, doc in enumerate(documents['docs']):
        doc_partition_key = doc['_id'].split(':')[0]
        assert doc_partition_key == expected_partition_key, \
            (f'Expect partition key "{expected_partition_key}", '
             f'but found "{doc_partition_key}" instead in docs[{str(index)}]')

