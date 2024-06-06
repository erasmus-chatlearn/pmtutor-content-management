def add_zero_to_section_ref_id(section_ref_id):
    s_id = int(section_ref_id)
    if s_id < 10:
        return f'0{str(s_id)}'
    else:
        return str(s_id)


def add_zero_to_assignment_ref_id(assignment_ref_id):
    a_id = float(assignment_ref_id)
    if a_id < 10:
        return f'0{str(a_id)}'
    else:
        return str(assignment_ref_id)
