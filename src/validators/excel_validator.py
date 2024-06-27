from .validation_message import ValidationMessage
import re
import pandas as pd
from utilities.regex_utilities import get_matching_column_names_by_regex


def check_excel_file_has_expected_sheets(all_sheets: dict, expected_sheet_names: tuple) -> ValidationMessage:
    print('\nCheck if the excel file has expected sheets...')
    result = ValidationMessage(True, 'It has all the expected sheets: ' + str(expected_sheet_names))
    for sheet_name in expected_sheet_names:
        if sheet_name not in all_sheets:
            result.is_valid = False
            result.message = '\n"' + sheet_name + '" sheet is missing from the excel file.'
            break
    return result


def check_a_sheet_has_expected_columns(sheet_name, dataframe, expected_column_names: tuple) -> ValidationMessage:
    result = ValidationMessage(True, 'It has all the expected columns.')
    for col_name in expected_column_names:
        if col_name not in dataframe.columns:
            result.is_valid = False
            result.message = '\nColumn "' + col_name + '" is missing from "' + sheet_name + '" sheet.'
            break
    return result


def check_required_columns_have_values(required_column_names: tuple, dataframe) -> ValidationMessage:
    result = ValidationMessage(True, 'The row(s) have all required values.')
    if len(dataframe) == 0:
        result.message = 'Skip checking required value as there is no row.'
    for required_column in required_column_names:
        col_values = dataframe.loc[:, required_column]
        if col_values.hasnans is True:
            result.is_valid = False
            result.message = '\nColumn "' + required_column + '" has an empty cell.'
            break
    return result


def check_values_in_column_are_unique(dataframe, column_name: str) -> ValidationMessage:
    result = ValidationMessage(True, 'The value(s) in column "' + column_name + '" are unique')
    if len(dataframe) == 0:
        result.message = 'Skip checking as there is no row'
    col_values = dataframe.loc[:, column_name]
    if not col_values.is_unique:
        result.is_valid = False
        result.message = '\nThe value(s) in column "' + column_name + '" are not unique'
    return result


def check_a_sheet_has_needed_columns_with_regex(sheet_name: str,
                                                dataframe, expected_column_regex: tuple) -> ValidationMessage:
    result = ValidationMessage(True, f'"{sheet_name}" has all the needed columns')
    for regex in expected_column_regex:
        pattern = re.compile(regex, re.IGNORECASE)
        if not any(pattern.search(column) for column in dataframe.columns):
            result.is_valid = False
            result.message = ('\nThe regex "' + regex + '" cannot find any matching column from "'
                              + sheet_name + '" sheet')
            break
    return result


def check_required_columns_have_values_by_regex(
        sheet_name, sheet_dataframe, regex_pattern, check_first_row_only: bool) -> ValidationMessage:
    result = ValidationMessage(False, None)
    pattern = re.compile(regex_pattern, re.IGNORECASE)
    filtered_columns = sheet_dataframe.filter(regex=pattern)
    if filtered_columns.empty:
        result.is_valid = True
        result.message = sheet_name + ' does not have required columns as no columns match the pattern: ' + regex_pattern
        return result
    for (column_name, column_data) in filtered_columns.items():
        if check_first_row_only:
            if pd.isnull(column_data[0]):
                result.message = ('The first row in required column ' + column_name + ' in ' + sheet_name +
                                  ' is empty!')
                return result
        else:
            if column_data.isna().sum() > 0:
                result.message = ('In sheet "' + sheet_name + '", a required column "' + column_name +
                                  '" has ' + str(column_data.isna().sum()) + ' empty cell(s)!')
                return result
    result.is_valid = True
    result.message = 'All required columns have value(s)'
    return result


def check_uniqueness_of_list_items_in_cell(sheet_data_frame, column_names: list, separator: str):
    for column in column_names:
        # print(sheet_data_frame[column])
        for value in sheet_data_frame[column]:
            # print(isinstance(value, str))
            if isinstance(value, str) and separator in value:
                items = [item.strip() for item in value.split(separator)]
                # print(items)
                assert len(items) == len(set(items)), f"Non-unique item found in column '{column}': {value}"


def check_cell_string_exists_in_another_sheet_column(current_sheet, column_names: list, separator: str,
                                                     referencing_sheet, referencing_column_name: str):
    """
    This function checks if a cell string exists in another sheet column.
    If the cell string does not exist, it raises an assertion error.
    """
    for column_name in column_names:
        for cell_value in current_sheet[column_name]:
            if pd.isnull(cell_value):
                continue
            try:
                split_items = [item.strip() for item in cell_value.split(separator)]
            except AttributeError:
                assert cell_value in referencing_sheet[referencing_column_name].values, \
                    f"{cell_value} does not exist in the referencing column"
            else:
                for item in split_items:
                    assert item in referencing_sheet[referencing_column_name].values, \
                        f"{item} does not exist in the referencing column"


def check_column_values_match_a_regex_pattern(sheet_data_frame, column_name, regex_pattern, allow_empty_values):
    """
    This function checks if the values in a specific column of a dataframe match a given regex pattern.
    If allow_empty_values is False, it also checks if there are any NaN or None values in the column.
    If the column does not exist, or if a value does not match the regex pattern, or if a value is NaN or None when allow_empty_values is False,
    it raises an assertion error.
    """
    assert column_name in sheet_data_frame.columns, f"the column '{column_name}' does not exist."

    for value in sheet_data_frame[column_name]:
        if pd.isnull(value):
            assert allow_empty_values, f"the column '{column_name}' has empty cell(s)."
        else:
            assert re.match(regex_pattern, str(value)), (f"The cell value '{value}' "
                                                         f"does not match the given regex pattern {regex_pattern}")


def check_referring_to_an_existing_parent_id(
        child_sheet, child_sheet_id_column_name, parent_id_pattern, parent_sheet, parent_sheet_id_column_name):
    """
    This function checks if the parent id extracted from the child sheet exists in the parent sheet.
    If the parent id does not exist in the parent sheet, it raises an error.
    """
    for child_id in child_sheet[child_sheet_id_column_name]:
        # Extract parent id using the parent id pattern
        # print(child_id)
        match = re.search(parent_id_pattern, str(child_id))
        if match is None:
            raise ValueError(f"Parent id cannot be extracted from {child_id} using the pattern {parent_id_pattern}")
        parent_id = match.group(0)
        # print(parent_id)
        # Check if the parent id exists in the parent sheet
        if parent_id not in parent_sheet[parent_sheet_id_column_name].values.astype(str):
            raise ValueError(f"Referenced parent id '{parent_id}' does not exist in the {parent_sheet_id_column_name}")


def check_ids_are_referred_by_child_ids_in_another_sheet(current_sheet_df, current_sheet_id_column_name: str,
                                                         parent_id_pattern: str, child_sheet_df,
                                                         child_sheet_id_column_name: str):
    """
    This function checks if the ids in the current sheet are referred by child ids in another sheet.
    It raises an error if a parent id cannot be extracted or if an id in the current sheet is not referred by any child ids.
    """
    # Loop through the id column in the current sheet
    for current_id in current_sheet_df[current_sheet_id_column_name]:
        # print(current_id)
        # Go through the child id in the child id column in the child sheet
        for child_id in child_sheet_df[child_sheet_id_column_name]:
            # print(child_id)
            # Extract the parent id using the parent id pattern
            parent_id = re.search(parent_id_pattern, child_id)
            # print(type(parent_id))
            if parent_id is None:
                raise ValueError(f"Parent id cannot be extracted from child id {child_id}")
            # Compare the id in the id column with the extracted parent id
            if str(current_id) == parent_id.group():
                break
        else:
            # If the id does not equal to any extracted parent id in the child ids, raise an error
            raise ValueError(f"The id '{current_id}' has not been referred by any child ids in "
                             f"{child_sheet_id_column_name}")


def check_column_y_has_value_given_column_x_values(
        current_sheet_df, column_x_name: str, column_y_name: str, given_x_values: tuple):
    """
    This function checks if column y has a value given column x values.
    If column x value is one of the given_x_values, it raises an error if column y is None or NaN.
    If column x value is not one of the given_x_values, it raises an error if column y is not None or NaN.
    """
    for index, row in current_sheet_df.iterrows():
        if row[column_x_name] in given_x_values and pd.isnull(row[column_y_name]):
            raise ValueError(f'In row {str(index + 1)}, column "{column_x_name}" has value "{row[column_x_name]}" '
                             f'so column "{column_y_name}" should have a value too.')
        elif row[column_x_name] not in given_x_values and not pd.isnull(row[column_y_name]):
            raise ValueError(f'In row {str(index + 1)}, column "{column_x_name}" is "{row[column_x_name]}" '
                             f'so column "{column_y_name}" should not have a value either.')


def check_values_of_columns_matching_given_regex(sheet_df, column_name_regex, value_regex, allow_empty: bool):
    column_names = get_matching_column_names_by_regex(sheet_df, column_name_regex)
    print(f'{str(len(column_names))} column(s) match {column_name_regex}', 'OK!')
    for name in column_names:
        check_column_values_match_a_regex_pattern(sheet_df, name, value_regex, allow_empty)
        print(f'Column "{name}" has values match {value_regex}', 'OK!')
