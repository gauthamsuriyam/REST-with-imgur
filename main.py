import sys
import tornado.ioloop
import tornado.web
import json
from tornado.escape import json_decode
import imageload


  
## use-case : input is a json string with unique download links
# use-case : input has duplicates - remove dups
# use-case : input has null values?
# use-case : multiple input request, ie, first request with 3 list of urls, second request with 5 list of urls, all possible due to asynchronous nature of the api

#use call back to send back job id once request has been raised.
#make all calls asynchronous

job_id_list={"jobId":[]} #job id list that have been initialized

class UploadHandler(tornado.web.RequestHandler): #all uploads handler
  def get(self):
    self.render("index.html")     #also used for initial entry point
  def post(self):
    json_req = json_decode(self.request.body) #object from json string
    
    job_id = imageload.queue_image_url(json_req) #calls image loader to download and upload the link to imgur
   
    #returns dictionary value of job id.
    job_id_list["jobId"].append(job_id)   #appends to list of Jobs initialized

    self.set_header("Content-Type","text/plain")
    self.write(json.dumps(job_id_list)) #all jobs id list


class JobStatusHandler(tornado.web.RequestHandler): #gets job information based on jobid as query string
  def get(self,slug):
    job = imageload.job_list_s[slug]                #slug contains the jobId
    self.write("<h1>This is the main story</h1>"+""+json.dumps(job.__dict__)) #json format output of the job informaiton for the specific jobId

class UploadedLinks(tornado.web.RequestHandler): #get all uploaded image (imgur) links
  def get(self):
    print("imgur links")
    uploads = {"uploaded":[]}         #ASSUMPTION: links of all uploaded images to imgur, regardless of the jobs status
    for key in imageload.job_list_s:
      uploads["uploaded"]+= imageload.job_list_s[key].uploaded['completed'] #available to view all the links from different uploads, regardless of the order of job
    if(uploads):
      self.write(json.dumps(uploads)) #returns jsondump of imgur url if list is not empty
    else:
      self.write("<h1>list empty</h1>")
    print(uploads)
      
class StopServer(tornado.web.RequestHandler): #for closing tornado server: only testing
  def get(self):
    tornado.ioloop.IOLoop.instance().stop()

def main_app(): #initialize application
  return tornado.web.Application([
    (r'/',UploadHandler),(r'/v1/images/upload',UploadHandler),(r'/v1/images/upload/\:([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',JobStatusHandler),
    (r'/v1/images',UploadedLinks),(r'/stopServer',StopServer)]) #url assignments

def main(arg =""): #calls main
  app = main_app()
  app.listen(8888)
  print("log: application has started")
  try:
    if arg != "test":
      tornado.ioloop.IOLoop.instance().start()
    else:
      print("this is a system test")
  except KeyboardInterrupt:
    print("interrupted")

if __name__ == "__main__":
  main(str(sys.argv[1]))
