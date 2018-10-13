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
job_id_list={"jobId":[]}
class UploadHandler(tornado.web.RequestHandler):
  def get(self):
    self.render("index.html")
  def post(self):
    json_req = json_decode(self.request.body) #object from json string
    #print(json_req)
    
    job_id = imageload.queue_image_url(json_req) #calls image loader to download and upload the link to
   
    #returns dictionary value of job id.
    job_id_list["jobId"].append(job_id)

    self.set_header("Content-Type","text/plain")
    self.write(json.dumps(job_id_list)) #all jobs
    #stopServer()


class JobStatusHandler(tornado.web.RequestHandler): #gets job information based on jobid as query string
  def get(self,slug):
    #print("slug value: "+slug)
    job = imageload.job_list_s[slug]
    #print(json.dumps(job.__dict__))
    self.write("<h1>This is the main story</h1>"+""+json.dumps(job.__dict__))

class UploadedLinks(tornado.web.RequestHandler): #get all uploaded image links
  def get(self):
    print("imgur links")
    uploads = {"uploaded":[]}         #ASSUMPTION: links of all uploaded images, regardless of the jobs status

    #self.write(str(len(imageload.job_list_s)))
    for key in imageload.job_list_s:
      #print("values pairs")
      #print(key)
      #print(imageload.job_list_s[key].uploaded['completed'])
      uploads["uploaded"]+= imageload.job_list_s[key].uploaded['completed'] #available to view all the links from different uploads, regardless of the order of job
    if(uploads):
      self.write(json.dumps(uploads))
    else:
      self.write("<h1>list empty</h1>")
    print(uploads)
      


def main_app(): #initialize application
  return tornado.web.Application([
    (r'/',UploadHandler),(r'/v1/images/upload',UploadHandler),(r'/v1/images/upload/\:([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',JobStatusHandler),(r'/v1/images',UploadedLinks)
  ])

def main(): #calls main
  app = main_app()
  app.listen(8888)
  print("log: application has started")
  tornado.ioloop.IOLoop.instance().start()
  #tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
  main()
