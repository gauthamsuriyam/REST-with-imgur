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
    self.job_id = str(uuid.uuid4()) #random unique id generated, may be replaced by time_uuid
    self.created = time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()) #assumption that time stamp is UTC in GMT format
    self.finished = False #boolean - indicates if the jobs are completed
    self.status = "pending" # pending - jobs has not started | in-progress - job in prog |complete - all jobs completed
    self.uploaded = {
      "pending" : [], #assumption list of links need to be downloaded and then uploaded. for now has list of temp file names. later change it to make it asynch
      "completed": [],
      "failed" : []
    }

class begin_upload(threading.Thread):
  def __init__(self,job_info, urlst): #initialize with new created job_info_obj and the list of url to dowload and upload to imgur
    threading.Thread.__init__(self)
    self.threadId = job_info.job_id
    self.job = job_info
    self.url_list = urlst

  def run(self):
    if(self.threadId):
      for l in self.url_list:
        report = image_download(l);
        if report["status_code"] == 200:
          self.job.uploaded["pending"].append(report) #dowloads all images, adds temp file path to pending
        else:
          self.job.uploaded["failed"].append(l) #when download fails
      
      #print("url_list size: {} and tmp_file_list size: {}".format(len(self.url_list),len(self.job.uploaded["pending"]))) # testing purpos: remove
      
      #print("job uploaded list before imgur")
      #print(self.job.uploaded)
      self.job.status = "in-progress"
      while(self.job.uploaded["pending"]):
        path = self.job.uploaded["pending"].pop()
        resp = ig.uploadImage(path["temp_fn"]) #sending just the temp path info. check image_download() for rport structure
        if(resp):
          self.job.uploaded["completed"].append(resp)
        else:
          self.job.uploaded["failed"].append(path["url"])
      
      self.job.finished = True
      self.job.status = "complete"
      #print("job uploaded list after imgur")
      #print(self.job.uploaded)




def queue_image_url(jUrl):
  lst = jUrl["urls"] #gets list of images

  job = job_info_obj()
  job_list_s[job.job_id]= job
  #print("job id created:")
  #print(job.job_id)
  bg = begin_upload(job,lst)
  bg.start()
  #print("thread started "+str(job.job_id))
  #bg.join()
  #print("thread set to background"+str(job.job_id))
  return job.job_id


def image_download(urlString): #donwloads the image and returns temp file path
  print("downloading..")
  #img = resp.read()
  #with open('images/downFile.jpg','wb') as f:
  #  f.write(img)
  report = { "status_code": 404,#place holder for errorcode
    "url": urlString,
    }
  try:
    with request.urlopen(urlString) as response:
      with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
          shutil.copyfileobj(response, tmp_file)

    #print("download status: "+str(response.status)) #log
    if(response.status == 200):
      report["status_code"]= response.status
      report["temp_fn"] = tmp_file.name            #returns file name with the other response info
      return report
  except URLError as e:
    print("error hit: URLError")
    print(e.reason)
  except ValueError as v:
    print("value error: ValueError")
  return report #response with no filename
  #print(dir(tmp_file))
  #print(tmp_file.name)
  #return tmp_file.name

if __name__ == "__main__":
  image_download()