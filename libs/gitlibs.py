import datetime
import base64
import json
import re
import logging
import libs.logger as logger
import libs.coloredOP as co
import config as config
import requests 
import git

def readFile(FileName):
    with open(FileName, 'r') as rf:
        FileContent = rf.read()
    return FileContent

def SetRepoName():
    # generate git repo name 
    repoName = str(datetime.datetime.now())
    repoName = re.sub('-|:|\.|\ ', '_', repoName)
    # set the logger
    logger.SetLogger(repoName)
    return repoName

def CreateRemoteRepo(repoName):
    # api url
    url = "https://api.github.com/user/repos"
    # request body
    jsonReq = {
        "name" : repoName,
        "private" : "true",
        "description" : "Github action automation repo"
    }
    # authorization header
    HEADERS = config.HEADERS
    HEADERS["Authorization"] = HEADERS.get("Authorization").format(config.ACCESS_TOKEN)
    # making API call
    req = requests.post(url, json=jsonReq, headers=HEADERS, timeout=10)
    logging.info("RepositoryCreationURL"+url)
    # check the status 
    if str(req.status_code).startswith('2'):
        print(co.bullets.OK, co.colors.GREEN+"Repository successfully created."+co.END)
        logging.info("RepoCreation|Sucess")
        logging.info("RepositoryName|"+repoName)
        print(co.bullets.INFO, "Repo_name : "+co.colors.CYAN+"{}".format(repoName)+co.END)
        # success 
        return 0
    else:
        print("Error received : {}".format(req.json()))
        logging.critical("Error During Repository Creation|RepositoryName|"+repoName)
        logging.critical("Error Message|"+json.dumps(req.json()))
        # failure
        return 1

def CommitFile(repoName, fileContent, path, commitMessage):
    # where path is where the file should be on repo
    url = 'https://api.github.com/repos/{}/{}/contents/{}'
    url = url.format(config.GITHUB_ACCOUNT_NAME, repoName, path)
    HEADERS = config.HEADERS
    HEADERS["Authorization"] = HEADERS.get("Authorization").format(config.ACCESS_TOKEN)
    b64Data = base64.b64encode(fileContent.encode('ascii'))
    b64Data= b64Data.decode('ascii')
    # json payload
    Json = {
        "content" : b64Data,
        "message" : commitMessage,
        "branch"  : "main",
    }
    # making api call
    # timeout 100 for pushing big files in some cases
    req = requests.put(url, json=Json, headers=HEADERS, timeout=100)
    logging.info("CommitFile|"+url)
    FileName = path.split("/")[-1]
    if str(req.status_code).startswith('2'):
        print(co.bullets.OK, co.colors.GREEN+FileName+" Successfully committed."+co.END)
        logging.info("CommitFile|Sucess")
        logging.info("CommitFileName|"+FileName)
        # success
        return 0
    else:
        print("Error received : {}".format(req.json()))
        logging.critical("Error During CommitingFile|FileName|"+FileName)
        logging.critical("Error Message|"+json.dumps(req.json()))
        # failure
        return 1

def CloneRepo(repoName):
    url = "https://oauth2:{}@github.com/{}/{}.git".format(config.ACCESS_TOKEN, config.GITHUB_ACCOUNT_NAME, repoName)   
    path = "./repo/{}".format(repoName) # localpath to store logs
    logging.info("CloningRepo|Url|"+url)
    try:
        git.Repo.clone_from(url, path)
        print(co.bullets.OK, co.colors.GREEN+"Repository successfully cloned under ./repo/ directory!"+co.END)
        logging.info("CloningRepository|Sucess")
        logging.info("RepositoryName|"+repoName)
        return 0
    except Exception as e:
        print("Error during cloning: {}".format(e.__str__()))
        logging.critical("Error in CloningRepo|Name|"+repoName)
        logging.critical("Error Message|"+str(e.__str__()))
        return 1

def DeleteRepo(repoName):
    # stops the workflow if needed
    delete_url = 'https://api.github.com/repos/{}/{}' # {Github_account_name, repo_name}
    delete_url = delete_url.format(config.GITHUB_ACCOUNT_NAME, repoName)
    HEADERS = config.HEADERS
    HEADERS["Authorization"] = HEADERS.get("Authorization").format(config.ACCESS_TOKEN)
    # making API call
    req = requests.delete(delete_url, data=None, headers=HEADERS, timeout=10)
    logging.info("DeletingRepository|Url|"+delete_url)
    # check the status  
    if str(req.status_code).startswith('2'):
        print(co.bullets.OK, co.colors.GREEN+"Repository successfully Deleted."+co.END)
        logging.info("DeletingRepository|Sucess")
        logging.info("RepositoryName|"+repoName)
        return 0
    else:
        print("Error received : {}".format(req.json()))
        logging.critical("Error in DeletingRepository|Name|"+REPONAME)
        logging.critical("Error Message|"+json.dumps(req.json()))
        return 1    
