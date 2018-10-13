from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError,ImgurClientRateLimitError


def uploadImage(tmpPath):    #upload function imgur
  client = getClient()       #set client information , make it persistent for each session
  print("begin upload")      #LOG

  try:
    resp = client.upload_from_path(tmpPath,config =None, anon = True)  #upload the downloaded image from the temporary path | default config | annonymus user
    print(client.credits)    #checks for client credits
    return resp["link"]      #returns the imgur link if successful

  except ImgurClientError as e:
    print(e.status_code)  #error log
    print(e.error_message)
    return ''                #returns empty string indicating failure
  except ImgurClientRateLimitError as e:
    print(e.status_code)    
    print(e.error_message)
    return ''                #returns empty string indicating failure
  #SH02X7X

def getClient():             #setting up client information
    print("setting clinet info..")
    client_id = 'a8780a1384666b1'  #clientID
    client_secret = '21da9a6142ded7a21a63d246dc8ba8d433685400'  #client secret

    return ImgurClient(client_id, client_secret)    #client

#for evaluating
if __name__ == "__main__":
  getClient()
