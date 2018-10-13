from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError,ImgurClientRateLimitError


def uploadImage(tmpPath):
  #print(len(tmpPath))
  client = getClient() #set client information , make it persistent for each session
  #print("begin upload") #log file

  try:
    resp = client.upload_from_path(tmpPath,config =None, anon = True)
    print(client.credits)
    #print("upload completed successfully") #log file
    return resp["link"]

  except ImgurClientError as e:
    print(e.status_code)  #error log
    print(e.error_message)
    return ''
  except ImgurClientRateLimitError as e:
    print(e.status_code)
    print(e.error_message)
    return ''
  #SH02X7X

def getClient():
    print("setting clinet info..")
    client_id = 'a8780a1384666b1'
    client_secret = '21da9a6142ded7a21a63d246dc8ba8d433685400'

    return ImgurClient(client_id, client_secret)
    #print(client.credits) #for testing- client information


#for evaluating
if __name__ == "__main__":
  getClient()
