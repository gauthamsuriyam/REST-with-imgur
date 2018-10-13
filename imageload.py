from urllib import request
from urllib.error import URLError
import imgurapi as ig
import tempfile
import shutil
import uuid
import time
import threading

job_list_s ={}
class job_info_obj: #upload JOb object
  def __init__(self,**kwargs): #job object initialize
    self.job_id = str(uuid.uuid4()) #random unique id generated version 4
    self.created = time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()) #assumption that time stamp is UTC in GMT format
    self.finished = False #boolean - indicates if the jobs are completed
    self.status = "pending" # pending - jobs has not started | in-progress - job in prog |complete - all jobs completed
    self.uploaded = {
      "pending" : [], #assumption - list of links that are downloaded but need to be uploaded - dictionary with information-
                      #"temp_fn => temporary file name, "status_code"=> status code of the download url response, "url"=>original url string value
      "completed": [],#list of all imgur url that are successfully uploaded
      "failed" : []   #list of all failed urls, fails could occur at downloading of the image or during uploading to imgur
    }

class begin_upload(threading.Thread): #upload JOB thread
  def __init__(self,job_info, urlst): #initialize with new created job_info_obj and the list of url to dowload and upload to imgur
    threading.Thread.__init__(self)
    self.threadId = job_info.job_id   #using job is as thread name
    self.job = job_info               #job object
    self.url_list = urlst             #list of url to download

  def run(self):
    if(self.threadId):
      for l in self.url_list:
        report = image_download(l);
        if report["status_code"] == 200:
          self.job.uploaded["pending"].append(report) #dowloads all images, adds temp file path to pending
        else:
          self.job.uploaded["failed"].append(l)        #when download fails
      self.job.status = "in-progress"                  #job status updated
      while(self.job.uploaded["pending"]):             #loops through pending list
        path = self.job.uploaded["pending"].pop()      
        resp = ig.uploadImage(path["temp_fn"])         #imgur uploader class - sending just the temp path name. check image_download() for report structure
        if(resp):
          self.job.uploaded["completed"].append(resp)  #if successfully completed - imgur link is added to completed set for the job
        else:
          self.job.uploaded["failed"].append(path["url"]) #failed to upload to imgur
      
      self.job.finished = True                         #end of upload job thread
      self.job.status = "complete"                     #all pending jobs completed

def queue_image_url(jUrl):
  lst = list(set(jUrl["urls"])) #keeping unique list of images - eliminating duplicates
  
  job = job_info_obj()          #Job object initalized, job id is assigned during initialization using Universal Unique Identified version 4
  job_list_s[job.job_id]= job   #adding job to job_list_s dictionary to store jobs of the session in-memory
  bg = begin_upload(job,lst)    #begin upload thread
  bg.start()
  return job.job_id


def image_download(urlString): #donwloads the image and returns temp file path
  print("downloading..")

  #data structure for pending list
  report = { "status_code": 404,#place holder for errorcode
    "url": urlString,           #original string to download
    }
  
  try:
    with request.urlopen(urlString) as response:   #url request
      with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
          shutil.copyfileobj(response, tmp_file)

    #print("download status: "+str(response.status)) #log
    if(response.status == 200):                    #if success
      report["status_code"]= response.status
      report["temp_fn"] = tmp_file.name            #returns file name with the other report values
      return report
  except URLError as e:
    print("error hit: URLError")
    print(e.reason)
  except ValueError as v:
    print("value error: ValueError")
  return report #response with no filename

if __name__ == "__main__":          #for eval
  image_download()
