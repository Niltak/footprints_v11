import requests
import xmltodict
from base64 import b64decode
from getpass import getpass


class Connection(object):
    def __init__(
        self,
        hostname,
        user,
        pwd) -> None:
        '''
        Starts a connection to the foot prints server.
        '''
        if not pwd:
            pwd = getpass()
        self.url = f'https://{hostname}/MRcgi/MRWebServices.pl'
        self.user = user
        self.pwd = pwd


    def requesting(self, data, action) -> requests.request:
        '''
        Submits request to the footprints server.
        Returns response.
        '''
        data = data.encode('utf-8')
        headers = {
            'SOAPAction' : f'MRWebServices#MRWebServices__{action}',
            'Content-Type' : 'text/xml; charset=utf-8',
            'Content-Length' : f'{len(data)}'
        }
        return requests.request('POST', self.url, headers=headers, data=data)


    def requesting_dict(self, data, action) -> dict:
        '''
        Converts requested response to a dictionary for easier manipulation.
        Returns a filtered response
        '''
        response = xmltodict.parse(self.requesting(data, action).text)
        return response['soap:Envelope']['soap:Body'][f'namesp1:MRWebServices__{action}Response']['return']


    def soap_envelope(self, data) -> str:
        '''
        Template of the required information around the data requested.
        Returns data inside the template.
        '''
        return f'''
            <SOAP-ENV:Envelope
                xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:namesp2="http://xml.apache.org/xml-soap"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
                    <SOAP-ENV:Header/>
                    <SOAP-ENV:Body>{data}</SOAP-ENV:Body>
            </SOAP-ENV:Envelope>
        '''


    def ticket_details(self, project_id, ticket_id) -> object:
        '''
        Requests information about a ticket.
        Returns Ticket(class).
        '''
        action = 'getIssueDetails'
        data = f'''
            <namesp1:MRWebServices__{action} xmlns:namesp1="MRWebServices">
                <user xsi:type="xsd:string">{self.user}</user>
                <password xsi:type="xsd:string">{self.pwd}</password>
                <extrainfo xsi:type="xsd:string"/>
                <projectnumber xsi:type="xsd:int">{project_id}</projectnumber>
                <mrid xsi:type="xsd:int">{ticket_id}</mrid>
            </namesp1:MRWebServices__{action}>
        '''
        data = self.soap_envelope(data)
        ticket_dict = self.requesting_dict(data, action)
        if not ticket_dict:
            return False
        
        ticket = Ticket(ticket_id)
        ticket.title = ticket_dict['title']['#text']
        ticket.status = ticket_dict['status']['#text']
        if '#text' in ticket_dict['First__bName'].keys():
            ticket.contact_fullname = f"{ticket_dict['First__bName']['#text']} {ticket_dict['Last__bName']['#text']}"
        ticket_details = [
            {'field': 'Position__bTitle', 'name': 'contact_title'},
            {'field': 'assignees', 'name': 'assigned'},
            {'field': 'Campus__bBuilding', 'name': 'building'},
            {'field': 'description', 'name': 'notes'},
            {'field': 'Tech__bNotes', 'name': 'tech_notes'},
            {'field': 'alldescs', 'name': 'full_notes'}
        ]
        for detail in ticket_details:
            if '#text' in ticket_dict[detail['field']].keys():
                ticket_text = ticket_dict[detail['field']]['#text']
                if 'xsd:base64Binary' in ticket_dict[detail['field']].values():
                    ticket_text = str(b64decode(ticket_text))
                setattr(ticket, detail['name'], ticket_text)

        if ticket.assigned: # Turn ticket.assigned into a list and remove cc'ed users
            ticket.assigned = ticket.assigned.split(' ')
            for assigned in ticket.assigned[:]:
                if 'CC:' in assigned:
                    ticket.assigned.remove(assigned)

        return ticket


    def search_tickets(self, project_id, key, key_selected='title') -> list:
        '''
        Requests information about a key word in the title of all the tickets.
        Returns a list of Tickets(class).
        '''
        if key_selected.lower() == 'title':
            key_selected = 'mrtitle'
        if key_selected.lower() == 'assignee':
            key_selected = 'mrassignees'

        query_where = f"{key_selected} LIKE '%{key}%'"
        query = f"SELECT mrid, mrtitle, mrstatus, mrassignees, mrsubmitdate, mrupdatedate, Ticket__bType from MASTER{project_id} WHERE {query_where}"

        action = 'search'
        data = f'''
            <namesp1:MRWebServices__{action} xmlns:namesp1="MRWebServices">
                <user xsi:type="xsd:string">{self.user}</user>
                <password xsi:type="xsd:string">{self.pwd}</password>
                <extrainfo xsi:type="xsd:string"/>
                <query xsi:type="xsd:string">{query}</query>
            </namesp1:MRWebServices__{action}>
        '''
        data = self.soap_envelope(data)
        ticket_list_raw = self.requesting_dict(data, action)

        ticket_list = []
        for ticket_raw in ticket_list_raw['item']:
            if key_selected == "mrassignees":
                ticket_assigned = ticket_raw['mrassignees']['#text'].split(' ')
                for assigned in ticket_assigned[:]:
                    if 'CC:' in assigned:
                        ticket_assigned.remove(assigned)
                if key not in ticket_assigned:
                    continue
            ticket = Ticket(ticket_raw['mrid']['#text'])
            ticket.title = ticket_raw['mrtitle']['#text']
            ticket.status = ticket_raw['mrstatus']['#text']
            if '#text' in ticket_raw['ticket__btype'].keys():
                ticket.type = ticket_raw['ticket__btype']['#text']
            ticket.date = ticket_raw['mrsubmitdate']['#text']
            ticket.last_update = ticket_raw['mrupdatedate']['#text']
            ticket_list.append(ticket)

        return ticket_list


    def ticket_create(
        self,
        project_id,
        title,
        details,
        priority='5',
        status='Assigned',
        assignees=['ITAP_NETWORKING'],
        ticket_type='Incident',
        category='Infrastructure',
        service='Network',
        service_offering='Wired__bCampus__bNetwork__bServices',
        urgency='Working__bNormally',
        impact='Minimal',
        campus='West__bLafayette'):
        '''
        '''
        submitter_id = self.user    # Temp
        assignees_data = f'<assignees xsi:type="SOAP-ENC:Array" SOAP-ENC:arrayType="xsd:string[{len(assignees)}]">'
        for assignee in assignees:
            assignees_data += f'<item xsi:type="xsd:string">{assignee}</item>'
        assignees_data += '</assignees>'

        action = 'createIssue'
        data = f'''
            <namesp1:MRWebServices__{action} xmlns:namesp1="MRWebServices">
                <user xsi:type="xsd:string">{self.user}</user>
                <password xsi:type="xsd:string">{self.pwd}</password>
                <extrainfo xsi:type="xsd:string"/>
                <args xsi:type="namesp2:SOAPStruct">
                    <projectID xsi:type="xsd:int">{project_id}</projectID>
                    <title xsi:type="xsd:string">{title}</title>
                    <description xsi:type="xsd:string">{details}</description>
                    <status xsi:type="xsd:string">{status}</status>
                    <priorityNumber xsi:type="xsd:string">{priority}</priorityNumber>
                    {assignees_data}
                    <abfields xsi:type="namesp2:SOAPStruct">
                        <User__bID xsi:type="xsd:string">{submitter_id}</User__bID>
                    </abfields>
                    <projfields xsi:type="namesp2:SOAPStruct">
                        <Ticket__bType xsi:type="xsd:string">{ticket_type}</Ticket__bType>
                        <Category xsi:type="xsd:string">{category}</Category>
                        <Service xsi:type="xsd:string">{service}</Service>
                        <Service__bOffering xsi:type="xsd:string">{service_offering}</Service__bOffering>
                        <Urgency xsi:type="xsd:string">{urgency}</Urgency>
                        <Impact xsi:type="xsd:string">{impact}</Impact>
                        <Campus xsi:type="xsd:string">{campus}</Campus>
                    </projfields>
                    <selectContact xsi:type="xsd:string">{submitter_id}</selectContact>
                </args>
            </namesp1:MRWebServices__{action}>
        '''
        data = self.soap_envelope(data)
        return self.requesting_dict(data, action)['#text']


    def ticket_update(
        self,
        project_id,
        ticket_number,
        priority=None,
        status=None,
        assignees=None,
        ticket_type=None,
        category=None,
        service=None,
        service_offering=None,
        urgency=None,
        impact=None,
        campus=None,
        tech_note=None,
        resolution=None,
        select_contact=None):
        '''
        '''
        ticket_args = ''
        if assignees:
            assignees_data = f'<assignees xsi:type="SOAP-ENC:Array" SOAP-ENC:arrayType="xsd:string[{len(assignees)}]">'
            for assignee in assignees:
                assignees_data += f'<item xsi:type="xsd:string">{assignee}</item>'
            assignees_data += '</assignees>'
            ticket_args += assignees_data
        if status:
            ticket_args += f'<status xsi:type="xsd:string">{status}</status>'
        if priority:
            ticket_args += f'<priorityNumber xsi:type="xsd:string">{priority}</priorityNumber>'
        if select_contact:
            ticket_args += f'<selectContact xsi:type="xsd:string">{select_contact}</selectContact>'

        ticket_fields = ''
        if ticket_type:
            ticket_fields += f'<Ticket__bType xsi:type="xsd:string">{ticket_type}</Ticket__bType>'
        if category:
            ticket_fields += f'<Category xsi:type="xsd:string">{category}</Category>'
        if service:
            ticket_fields += f'<Service xsi:type="xsd:string">{service}</Service>'
        if service_offering:
            ticket_fields += f'<Service__bOffering xsi:type="xsd:string">{service_offering}</Service__bOffering>'
        if urgency:
            ticket_fields += f'<Urgency xsi:type="xsd:string">{urgency}</Urgency>'
        if impact:
            ticket_fields += f'<Impact xsi:type="xsd:string">{impact}</Impact>'
        if campus:
            ticket_fields += f'<Campus xsi:type="xsd:string">{campus}</Campus>'
        if tech_note:
            ticket_fields += f'<Tech__bNotes xsi:type="xsd:string">{tech_note}</Tech__bNotes>'
        if resolution:
            ticket_fields += f'<Resolution__bNotice xsi:type="xsd:string">{resolution}</Resolution__bNotice>'
        

        action = 'editIssue'
        data = f'''
            <namesp1:MRWebServices__{action} xmlns:namesp1="MRWebServices">
                <user xsi:type="xsd:string">{self.user}</user>
                <password xsi:type="xsd:string">{self.pwd}</password>
                <extrainfo xsi:type="xsd:string"/>
                <args xsi:type="namesp2:SOAPStruct">
                    <projectID xsi:type="xsd:int">{project_id}</projectID>
                    <mrID xsi:type="xsd:int">{ticket_number}</mrID>
                    {ticket_args}
                    <projfields xsi:type="namesp2:SOAPStruct">
                        {ticket_fields}
                    </projfields>
                </args>
            </namesp1:MRWebServices__{action}>
        '''
        data = self.soap_envelope(data)
        return self.requesting(data, action)


    def ticket_close(
        self,
        project_id,
        ticket_number,
        status='Resolved',
        resolution='Completed',
        assignees=None,
        ticket_type=None,
        category='Infrastructure',
        service='Network',
        service_offering='Custom Network Solutions',
        urgency='Working__bNormally',
        impact='Minimal',
        campus='West__bLafayette',
        tech_note='Closed with footprints automation',
        select_contact=None):
        '''
        '''        
        ticket_number = self.ticket_update(
            project_id,
            ticket_number,
            status=status,
            resolution=resolution,
            assignees=assignees,
            ticket_type=ticket_type,
            category=category,
            service=service,
            service_offering=service_offering,
            urgency=urgency,
            impact=impact,
            campus=campus,
            tech_note=tech_note,
            select_contact=select_contact)
        return ticket_number


class Ticket(dict):
    def __init__(self, id):
        self.id = id
    
    def info(self):
        '''
        Returns a dictionary of the class.
        '''
        return self.__dict__


if __name__ == "__main__":
    pass