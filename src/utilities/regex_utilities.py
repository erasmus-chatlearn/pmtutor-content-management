import re


def get_a_matching_column_name_by_regex(data_frame, regex: str) -> str:
    pattern = re.compile(regex, re.IGNORECASE)
    matching_columns = [col for col in data_frame.columns if re.search(pattern, col)]

    assert len(matching_columns) != 0, "No matching column found"
    assert len(matching_columns) == 1, f"Multiple matching columns found: {matching_columns}"

    return matching_columns[0]


def get_matching_column_names_by_regex(data_frame, regex: str) -> list:
    pattern = re.compile(regex, re.IGNORECASE)
    matching_columns = [col for col in data_frame.columns if re.search(pattern, col)]
    return matching_columns
