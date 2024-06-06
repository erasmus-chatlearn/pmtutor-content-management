import time


def get_now_in_unix_milliseconds():
    return round(time.time() * 1000)


def get_doc_ids_by_their_spreadsheet_ids(spreadsheet_ids: str, list_objects):
    doc_ids = []
    ref_ids = [spreadsheet_id.strip() for spreadsheet_id in spreadsheet_ids.split(',')]
    for ref_id in ref_ids:
        result = [object._id for object in list_objects if object.spreadSheetRefId == ref_id]
        # print(result)
        doc_ids.append(result[0])
    return doc_ids
