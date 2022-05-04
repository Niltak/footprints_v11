import re
import logging as log
import footprints_v11 as foot


def automate_ticket_queue():
    pass


def automate_PAL_Gaming(
    ticket_id,
    user,
    pwd=None,
    project_id=17,
    foot_connection=None):
    '''
    '''
    if not foot_connection:
        foot_connection = foot.Connection(
            'support.purdue.edu', user, pwd)
    ticket = foot_connection.ticket_details(project_id, ticket_id)
    
    try:
        ticket.info()
    except AttributeError:
        return False

    if 'PAL Gaming'.lower() in ticket.title.lower():
        if hasattr(ticket, 'tech_notes') and hasattr(ticket, 'full_notes'):
            ticket.full_notes = ticket.full_notes + ticket.tech_notes
        elif not hasattr(ticket, 'full_notes'):
            ticket.full_notes = ticket.tech_notes

        reg_colon = r'&#58;'
        regex_mac1 = fr'..{reg_colon}..{reg_colon}..{reg_colon}..{reg_colon}..{reg_colon}..'
        regex_mac2 = fr'..-..-..-..-..-..'
        mac = False
        try: 
            mac = re.search(regex_mac1, ticket.full_notes).group(0)
            mac = re.sub(reg_colon, ':', mac)
        except Exception:
            pass
        try:
            mac = re.search(regex_mac2, ticket.full_notes).group(0)
            mac = re.sub('-', ':', mac)
        except Exception:
            pass

        return {'id': ticket.id, 'mac': mac}


def search_PAL_Gaming(
    user,
    pwd=None,
    project_id=17,
    foot_connection=None,
    debug=None):
    '''
    '''
    if not foot_connection:
        foot_connection = foot.Connection(
            'support.purdue.edu', user, pwd)

    ticket_list = foot_connection.ticket_search(
        project_id, 'PAL Gaming')

    output_ticket_list = []
    for ticket in ticket_list:
        if ticket.status != 'Closed':
            if debug:
                print(ticket.info())
            output_ticket_list.append(ticket)

    if not output_ticket_list:
        return False

    return output_ticket_list


def automate_PAL_Gaming_tickets(
    user,
    pwd=None,
    project_id=17,
    debug=None):
    '''
    '''
    foot_connection = foot.Connection(
        'support.purdue.edu', user, pwd)
    
    try:
        ticket_list = search_PAL_Gaming(
            user, pwd=pwd, foot_connection=foot_connection)
    except:
        log.debug('No new tickets found!')
        return False

    ticket_mac_list = []
    for ticket in ticket_list:
        ticket_details = automate_PAL_Gaming(
            ticket.id, user, pwd=pwd, foot_connection=foot_connection)
        ticket_mac_list.append(ticket_details)
    
    return ticket_mac_list


def auto_close(
    user,
    project_id,
    ticket_id_list,
    pwd=None,
    status='Resolved',
    ticket_type='Incident',
    category='Infrastructure',
    service='Network',
    service_offering='Wired__bCampus__bNetwork__bServices',
    urgency='Working__bNormally',
    impact='Minimal',
    campus='West__bLafayette',
    tech_note='Closed with footprints automation',
    resolution='Completed',
    select_contact='jpublic'):
    '''
    '''
    if not isinstance(ticket_id_list, list):
        ticket_id_list = [ticket_id_list]

    foot_connection = foot.Connection(
        'support.purdue.edu', user, pwd)
    
    ticket_return_list = []
    for ticket_id in ticket_id_list:
        ticket_return_list.append(
            foot_connection.ticket_update(
                project_id,
                ticket_id,
                status=status,
                ticket_type=ticket_type,
                category=category,
                service=service,
                service_offering=service_offering,
                urgency=urgency,
                impact=impact,
                campus=campus,
                tech_note=tech_note,
                resolution=resolution,
                select_contact=select_contact))

    return ticket_return_list


def auto_close_WAN(
    user,
    project_id,
    ticket_id_list,
    pwd=None,
    service_offering='WAN__bInternet__bServices'):
    '''
    '''
    return auto_close(
        user, project_id, ticket_id_list, pwd=pwd,
        service_offering=service_offering)


def auto_close_iLight(
    user,
    project_id,
    ticket_id_list,
    pwd=None,
    service_offering='iLight'):
    '''
    '''
    return auto_close(
        user, project_id, ticket_id_list, pwd=pwd,
        service_offering=service_offering)


def auto_close_general_wired(
    user,
    project_id,
    ticket_id_list,
    pwd=None,
    service_offering='Wired__bCampus__bNetwork__bServices'):
    '''
    '''
    return auto_close(
        user, project_id, ticket_id_list, pwd=pwd,
        service_offering=service_offering)


def auto_close_general_wireless(
    user,
    project_id,
    ticket_id_list,
    pwd=None,
    service_offering='Wireless__bNetwork__bServices'):
    '''
    '''
    return auto_close(
        user, project_id, ticket_id_list, pwd=pwd,
        service_offering=service_offering)


if __name__ == "__main__":
    pass
