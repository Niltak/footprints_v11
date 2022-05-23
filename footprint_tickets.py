import footprints_v11 as foot


def ticket_details(user, project_id, ticket_id, pwd=None):
    foot_connection = foot.Connection(
        'support.purdue.edu', user, pwd)
    return foot_connection.ticket_details(project_id, ticket_id)


def ticket_search(user, project_id, key, key_selected='title', pwd=None):
    foot_connection = foot.Connection(
        'support.purdue.edu', user, pwd)
    return foot_connection.ticket_search(project_id, key, key_selected=key_selected)


def ticket_create(user, project_id, title, details, pwd=None):
    foot_connection = foot.Connection(
        'support.purdue.edu', user, pwd)
    return foot_connection.ticket_create(project_id, title, details)


# def ticket_update(user, pwd, project_id, title, details):
#     foot_connection = foot.Connection(
#         'support.purdue.edu', user, pwd)
#     return foot_connection.ticket_create(project_id, title, details)


def ticket_close(
    user,
    project_id,
    ticket_number,
    pwd=None,
    priority=None,
    status='Resolved',
    assignees=None,
    ticket_type=None,
    category='Infrastructure',
    service='Network',
    service_offering='Custom Network Solutions',
    urgency='Working__bNormally',
    impact='Minimal',
    campus='West__bLafayette',
    tech_note='Closed with footprints automation',
    resolution='Completed',
    select_contact=None):
    '''
    '''
    foot_connection = foot.Connection(
        'support.purdue.edu', user, pwd)
    ticket_return = foot_connection.ticket_update(
        project_id,
        ticket_number,
        priority=priority,
        status=status,
        assignees=assignees,
        ticket_type=ticket_type,
        category=category,
        service=service,
        service_offering=service_offering,
        urgency=urgency,
        impact=impact,
        campus=campus,
        tech_note=tech_note,
        resolution=resolution,
        select_contact=select_contact)

    return ticket_return


def change_details(user, project_id, ticket_id, pwd=None):
    if not isinstance(ticket_id, list):
        ticket_id = [ticket_id]
    foot_connection = foot.Connection(
        'support.purdue.edu', user, pwd)

    ticket_list = []    
    for id in ticket_id:
        ticket_list.append(foot_connection.change_details(project_id, id))
    return ticket_list


def change_search(user, project_id, key, key_selected='title', pwd=None):
    foot_connection = foot.Connection(
        'support.purdue.edu', user, pwd)
    return foot_connection.change_search(project_id, key, key_selected=key_selected)


def change_create(user, project_id, title, details, pwd=None):
    foot_connection = foot.Connection(
        'support.purdue.edu', user, pwd)
    return foot_connection.change_create(project_id, title, details=details)


if __name__ == "__main__":
    pass
