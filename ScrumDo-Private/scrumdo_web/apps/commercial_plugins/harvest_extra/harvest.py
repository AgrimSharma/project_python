#!/usr/bin/env python
'''
See http://www.getharvest.com/api

'''
import urllib2
from base64 import b64encode
from dateutil.parser import parse as parseDate
from xml.dom.minidom import parseString
import elementtree.ElementTree as ET
import re
import time
import logging

logger = logging.getLogger(__name__)

TIME_BETWEEN_REQUESTS = 0.6
MAX_RETRY_COUNT = 30

instance_classes = []
class HarvestItemGetterable(type):
    def __init__( klass, name, bases, attrs ):
        super(HarvestItemGetterable,klass).__init__(name,bases,attrs)
        instance_classes.append( klass )


class HarvestItemBase(object):
    def __init__( self, harvest, data ):
        self.harvest = harvest
        for key,value in data.items():
            key = key.replace('-','_').replace(' ','_')
            try:
                setattr( self, key, value )
            except AttributeError:
                pass


class User(HarvestItemBase):
    __metaclass__ = HarvestItemGetterable

    base_url = '/people'
    element_name = 'user'
    plural_name = 'users'

    def __str__(self):
        return u'User: %s %s' % (self.first_name, self.last_name)

    def entries(self,start,end):
        return self.harvest._time_entries( '%s/%d/' % (self.base_url, self.id), start, end )


class Project(HarvestItemBase):
    __metaclass__ = HarvestItemGetterable

    base_url = '/projects'
    element_name = 'project'
    plural_name = 'projects'

    def __str__(self):
        return 'Project: ' + self.name

    def entries(self,start,end):
        return self.harvest._time_entries( '%s/%d/' % (self.base_url, self.id), start, end )

    @property
    def client(self):
        return self.harvest.client( self.client_id )

    @property
    def task_assignments(self):
        url = '%s/%d/task_assignments' % (self.base_url, self.id)
        for element in self.harvest._get_element_values( url, 'task-assignment' ):
            yield TaskAssignment( self.harvest, element )

    @property
    def user_assignments(self):
        url = '%s/%d/user_assignments' % (self.base_url, self.id)
        for element in self.harvest._get_element_values( url, 'user-assignment' ):
            yield UserAssignment( self.harvest, element )


class Client(HarvestItemBase):
    __metaclass__ = HarvestItemGetterable

    base_url = '/clients'
    element_name = 'client'
    plural_name = 'clients'

    @property
    def contacts(self):
        url = '%s/%d/contacts' % (self.base_url, self.id)
        for element in self.harvest._get_element_values( url, 'contact' ):
            yield Contact( self.harvest, element )

    def invoices(self):
        url = '%s?client=%s' % (Invoice.base_url, self.id)
        for element in self.harvest._get_element_values( url, Invoice.element_name ):
            yield Invoice( self.harvest, element )

    def __str__(self):
        return 'Client: ' + self.name


class Contact(HarvestItemBase):
    __metaclass__ = HarvestItemGetterable

    base_url = '/contacts'
    element_name = 'contact'
    plural_name = 'contacts'

    def __str__(self):
        return 'Contact: %s %s' % (self.first_name, self.last_name)


class Task(HarvestItemBase):
    __metaclass__ = HarvestItemGetterable

    base_url = '/tasks'
    element_name = 'task'
    plural_name = 'tasks'

    def __str__(self):
        return 'Task: ' + self.name


class UserAssignment(HarvestItemBase):
    def __str__(self):
        return 'user %d for project %d' % (self.user_id, self.project_id)

    @property
    def project(self):
        return self.harvest.project( self.project_id )

    @property
    def user(self):
        return self.harvest.user( self.user_id )


class TaskAssignment(HarvestItemBase):
    def __str__(self):
        return 'task %d for project %d' % (self.task_id, self.project_id)

    @property
    def project(self):
        return self.harvest.project( self.project_id )

    @property
    def task(self):
        return self.harvest.task( self.task_id )


class Entry(HarvestItemBase):
    def __str__(self):
        return '%0.02f hours for project %d' % (self.hours, self.project_id)

    @property
    def project(self):
        return self.harvest.project( self.project_id )

    @property
    def task(self):
        return self.harvest.task( self.task_id )


class Invoice(HarvestItemBase):
    __metaclass__ = HarvestItemGetterable

    base_url = '/invoices'
    element_name = 'invoice'
    plural_name = 'invoices'

    def __str__(self):
        return 'invoice %d for client %d' % (self.id, self.client_id)

    @property
    def csv_line_items(self):
        '''
        Invoices from lists omit csv-line-items

        '''
        if not hasattr(self, '_csv_line_items'):
            url = '%s/%s' % (self.base_url, self.id)
            self._csv_line_items = self.harvest._get_element_values( url, self.element_name ).next().get('csv-line-items', '')
        return self._csv_line_items

    @csv_line_items.setter
    def csv_line_items(self, val):
        self._csv_line_items = val

    def line_items(self):
        import csv
        return csv.DictReader(self.csv_line_items.split('\n'))


class Harvest(object):
    def __init__(self,uri,email,password):        
        self.uri = uri
        self.retry_count = 0
        
        if self.uri[-1] == "/":
            # remove trailing slash
            self.uri = self.uri[0:-1]
            
        self.headers={
            'Authorization':'Basic '+b64encode('%s:%s' % (email,password)),
            'Accept':'application/xml',
            'Content-Type':'application/xml',
            'User-Agent':'ScrumDo.com (scrumdo@scrumdo.com)',
        }

        # create getters
        for klass in instance_classes:
            self._create_getters( klass )

    def _create_getters(self,klass):
        '''
        This method creates both the singular and plural getters for various
        Harvest object classes.

        '''
        flag_name = '_got_' + klass.element_name
        cache_name = '_' + klass.element_name

        setattr( self, cache_name, {} )
        setattr( self, flag_name, False )

        cache = getattr( self, cache_name )

        def _get_item(id):
            if id in cache:
                return cache[id]
            else:
                url = '%s/%d' % (klass.base_url, id)
                item = self._get_element_values( url, klass.element_name ).next()
                item = klass( self, item )
                cache[id] = item
                return item

        setattr( self, klass.element_name, _get_item )

        def _get_items():
            if getattr( self, flag_name ):
                for item in cache.values():
                    yield item
            else:
                for element in self._get_element_values( klass.base_url, klass.element_name ):
                    item = klass( self, element )
                    cache[ item.id ] = item
                    yield item

                setattr( self, flag_name, True )

        setattr( self, klass.plural_name, _get_items )

    def find_user(self, first_name, last_name):
        for person in self.users():
            if first_name.lower() in person.first_name.lower() and last_name.lower() in person.last_name.lower():
                return person

        return None

    def updateTask(self, taskID, taskName):
        req = ET.Element('task')
        ET.SubElement( req, "name").text = unicode( taskName )        
        body = ET.tostring(req)        
        self._put("/tasks/%s" % str(taskID), body )
        return True

    def createTaskInProject( self, taskName , projectId):
        # /projects/#{project_id}/task_assignments/add_with_create_new_task
        # <task>
        #   <name>Server Admninistration</name>
        # </task>
        
        # First, Create the task/assignment
        req = ET.Element('task')
        ET.SubElement( req, "name").text = unicode( taskName[:254] )        
        body = ET.tostring(req)        
        body, info = self._post("/projects/%s/task_assignments/add_with_create_new_task" % projectId, body)
        location = info.getheader("location") # Location: /projects/1252860/task_assignments/12462832                
        m = re.search("/projects/[0-9]+/task_assignments/([0-9]+)", location)
        assignment_id = m.group(1)
        # logger.debug("New harvest task assignment id: %s" % assignment_id )
        
        # Next, retrieve the assignment so we can get the task ID that was generated.
        # for i in range(20): (quota debug)
        xmlResult = self._request("/projects/%s/task_assignments/%s" % (projectId, assignment_id))
        task_id = xmlResult.getElementsByTagName("task-id")[0].childNodes[0].data
        active =  (xmlResult.getElementsByTagName("deactivated")[0].childNodes[0].data == "false" )
        # logger.debug("New harvest task id: %s" % task_id )
        
        if not active:
            # If the task was previously created and archived, we need to unarchive it
            self._post("/tasks/%s/activate" % task_id)
            # and mark the assignment active.
            req = ET.Element('task-assignment')
            ET.SubElement( req, "billable").text = "true"
            ET.SubElement( req, "deactivated").text = "false"
            body = ET.tostring(req)
            self._put("/projects/%s/task_assignments/%s" % (projectId, assignment_id), body)
        
        return (assignment_id, task_id, self.uri + location)  

    def removeTask(self, task_id):
        body, info = self._delete("/tasks/%s" % task_id )
        return (body,info)

    def removeTaskAssignmentFromProject(self, task_assignment_id, project_id):
         body, info = self._delete("/projects/%s/task_assignments/%s" % (project_id, task_assignment_id), "" )
         return (body,info)
        
    def _time_entries(self,root,start,end):
        url = root + 'entries?from=%s&to=%s' % (start.strftime('%Y%m%d'), end.strftime('%Y%m%d'))
        for element in self._get_element_values( url, 'day-entry' ):
            yield Entry( self, element )

    def _delete(self, url, body=""):
        try:
            request = urllib2.Request( url=self.uri+url, data=body, headers=self.headers )
            request.get_method = lambda: 'DELETE'  
            r = urllib2.urlopen(request)
            body = r.read()
            info = r.info()
            time.sleep(TIME_BETWEEN_REQUESTS) # Add in a delay so we never hit the harvest rate throttling threshold of 40/15 sec  (0.375 is exactly that, went a little higher)
            return (body, info)
        except urllib2.HTTPError as err:
            if (err.code == 503) and (self.retry_count < MAX_RETRY_COUNT):
                # API Throttle
                self.retry_count += 1
                logger.info("Harvest API Throttling, retrying in %d seconds." % (self.retry_count * 4))
                logger.info( self._request("/account/rate_limit_status", retry=False).toxml() )
                time.sleep(self.retry_count * 4) # sleep for self.retry_count*4 minutes and try again.
                logger.info("Retrying...")
                return self._delete(url,body)
            raise
            
            
    def _put(self, url, body=""):
        try:
            request = urllib2.Request( url=self.uri+url, data=body, headers=self.headers )
            request.get_method = lambda: 'PUT'            
            r = urllib2.urlopen(request)
            body = r.read()
            info = r.info()
            time.sleep(TIME_BETWEEN_REQUESTS) # Add in a delay so we never hit the harvest rate throttling threshold of 40/15 sec  (0.375 is exactly that, went a little higher)
            return (body, info)
        except urllib2.HTTPError as err:
            if (err.code == 503) and (self.retry_count < MAX_RETRY_COUNT):
                # API Throttle
                self.retry_count += 1
                logger.info("Harvest API Throttling, retrying in %d seconds." % (self.retry_count * 4))
                logger.info( self._request("/account/rate_limit_status", retry=False).toxml() )
                time.sleep(self.retry_count * 4) # sleep for self.retry_count*4 minutes and try again.
                return self._put(url,body)
            raise            
            
    def _post(self, url, body=""):
        
        try:
            request = urllib2.Request( url=self.uri+url, data=body, headers=self.headers )
            r = urllib2.urlopen(request)
            body = r.read()
            info = r.info()
            time.sleep(TIME_BETWEEN_REQUESTS) # Add in a delay so we never hit the harvest rate throttling threshold of 40/15 sec  (0.375 is exactly that, went a little higher)
            return (body, info)
        except urllib2.HTTPError as err:
            if (err.code == 503) and (self.retry_count < MAX_RETRY_COUNT):
                # API Throttle
                self.retry_count += 1
                logger.info("Harvest API Throttling, retrying in %d seconds." % (self.retry_count * 4))
                logger.info( self._request("/account/rate_limit_status", retry=False).toxml() )
                time.sleep(self.retry_count * 4) # sleep for self.retry_count*4 minutes and try again.
                return self._post(url,body)
            raise        
        
    def _request(self,url,retry=True):
        
        try:
            request = urllib2.Request( url=self.uri+url, headers=self.headers )
            r = urllib2.urlopen(request)
            xml = r.read()
            time.sleep(TIME_BETWEEN_REQUESTS) # Add in a delay so we never hit the harvest rate throttling threshold of 40/15 sec  (0.375 is exactly that, went a little higher)
            return parseString( xml )
        except urllib2.HTTPError as err:
            if (err.code == 503) and (self.retry_count < MAX_RETRY_COUNT):
                # API Throttle
                self.retry_count += 1
                logger.info("Harvest API Throttling, retrying in %d seconds." % (self.retry_count * 4))
                time.sleep(self.retry_count * 4) # sleep for self.retry_count*4 minutes and try again.
                return self._request(url)
            raise            

    def _get_element_values(self,url,tagname):
        def get_element(element):
            text = ''.join( n.data for n in element.childNodes if n.nodeType == n.TEXT_NODE )
            try:
                entry_type = element.getAttribute('type')
                if entry_type == 'integer':
                    try:
                        return int( text )
                    except ValueError:
                        return 0
                elif entry_type in ('date','datetime'):
                    return parseDate( text )
                elif entry_type == 'boolean':
                    try:
                        return text.strip().lower() in ('true', '1')
                    except ValueError:
                        return False
                elif entry_type == 'decimal':
                    try:
                        return float( text )
                    except ValueError:
                        return 0.0
                else:
                    return text
            except:
                return text

        xml = self._request(url)
        for entry in xml.getElementsByTagName(tagname):
            value = {}
            for attr in entry.childNodes:
                if attr.nodeType == attr.ELEMENT_NODE:
                    tag = attr.tagName
                    value[tag] = get_element( attr )

            if value:
                yield value

