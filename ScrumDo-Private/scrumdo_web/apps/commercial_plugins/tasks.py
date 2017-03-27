from apps.projects.models import *

from apps.scrumdocelery import app

from rollbardecorator import logexception
from zipfile import ZipFile

import zipfile
import StringIO

class InMemoryZip(object):
   def __init__(self):
       # Create the in-memory file-like object
       self.in_memory_zip = StringIO.StringIO()
   
   def open(arg):
    pass   

   def size():
    return self.in_memory_zip.size()

   def append(self, filename_in_zip, file_contents):
       '''Appends a file with name filename_in_zip and contents of
          file_contents to the in-memory zip.'''
       # Get a handle to the in-memory zip in append mode
       zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)
      
       # Write the file to the in-memory zip
       zf.writestr(filename_in_zip, file_contents)
      
       # Mark the files as having been created on Windows so that
       # Unix permissions are not inferred as 0000
       for zfile in zf.filelist:
           zfile.create_system = 0       
      
       return self
      
   def read(self):
       '''Returns a string with the contents of the in-memory zip.'''
       self.in_memory_zip.seek(0)
       return self.in_memory_zip.read()
  
   def writetofile(self, filename):
       '''Writes the in-memory zip to a file.'''
       f = file(filename, "wb")
       f.write(self.read())
       f.close()

@app.task
def generateATDDFile(project_id, iteration_id, job_id, fieldname, filetype='txt'):
    job = FileJob.objects.get(id=job_id)
    project = Project.objects.get(id=project_id)
    iteration = project.iterations.get(id=iteration_id)
    zipfile = InMemoryZip()
    for story in iteration.stories.all():
        filename = "%d.%s" % (story.local_id, filetype)
        text = story.__dict__[fieldname] if filetype == 'txt' else \
            "Feature: %s\nScenario: %s" % (story.__dict__['summary'], story.__dict__['detail'])
        zipfile.append(filename, text.encode('utf-8'))
    job.attachment_file.save("atdd.zip", zipfile )
    job.completed = True
    job.save()



