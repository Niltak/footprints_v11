import csv
import datetime
import logging as log
import Footprints_Python.footprints_v11 as foot
import nil_lib as ks


def audit_user(
    foot_connection,
    project_id,
    name,
    day_range=365,
    ticket_type=None):
    '''
    '''
    try:
        full_ticket_list = foot_connection.search_tickets(
            project_id, name, key_selected='assignee')
    except:
        log.debug('No new tickets found!')
        return False

    ticket_list = []
    for ticket in full_ticket_list:
        if ticket.status == 'Closed' or ticket.status == 'Resolved':
            ticket_date = datetime.datetime.strptime(
                ticket.date[:10], '%Y-%m-%d')
            time_diff = datetime.datetime.today() - ticket_date
            if day_range >= time_diff.days:
                if not ticket_type:
                    ticket_list.append(ticket.info())
                    continue
                if ticket.type == 'Incident':
                    ticket_list.append(ticket.info())

    ticket_list = sorted(ticket_list, key=lambda i: i['title'])

    return ticket_list


def audit_network_team(
    user,
    pwd,
    project_id=17,
    day_range=365,
    ticket_type=None,
    debug=None):
    '''
    '''
    network_team = [
        'kvsampso',
        'skfoley',
        'dekkyb',
        'peercy',
        'richar96',
        'mskvarek',
        'montgo59',
        'huffb',
        'caseb',
        'rolanda',
        'jandres',
        'jone1513',
        'jehimes']

    foot_connection = foot.Connection(
        'support.purdue.edu', user, pwd)
    team_list = []
    for team_member in network_team:
        ticket_list = audit_user(
            foot_connection,
            project_id,
            team_member,
            day_range=day_range,
            ticket_type=ticket_type)
        team_list.append({'user': team_member, 'tickets':len(ticket_list), 'ticket_list': ticket_list})

    team_list_numbers = []
    for team_member in team_list:
        team_list_numbers.append({team_member['user']: team_member['tickets']})
    team_list_full = {'user_list': team_list_numbers, 'ticket_details': team_list}   

    if not debug:
        with open('test.csv', 'w', newline='') as csv_file:
            fieldnames = ['id', 'title', 'status', 'type', 'date', 'last_update']
            writer = csv.DictWriter(csv_file, fieldnames, dialect='excel')
            for team_member in team_list:
                csv_file.write(f"{team_member['user']}\n")
                writer.writeheader()
                writer.writerows(team_member['ticket_list'])
                csv_file.write('\n')

    if debug:
        ks.file_create(
            f'audit_team_tickets--{datetime.date.today().strftime("%m-%d-%Y")}',
            'logs/audit_tickets/',
            team_list_full,
            'yml',
        )


if __name__ == "__main__":
    pass
