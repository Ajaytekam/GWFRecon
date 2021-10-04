import libs.coloredOP as co
import sys
import config
import libs.signal as sig
import libs.gitlibs as gitlibs
import signal 
import time 
import logging 
import requests
import json

REPONAME = ''
TEMPLATE_NAME = ''
JOB_ID = ''
HTML_URL = ''
LOGS_URL = ''
JOB_RUN_SUCCESS = True
TIME_LOG_WRITER = False
LOGS_DOWNLOADED = False

def StartWorkflow():
    global REPONAME
    global TEMPLATE_NAME 
    url = 'https://api.github.com/repos/{}/{}/actions/workflows/{}/dispatches'.format(config.GITHUB_ACCOUNT_NAME, REPONAME, TEMPLATE_NAME)
    Json = {
        "ref" : "main"
    }
    # preparing headers
    HEADERS = config.HEADERS
    HEADERS["Authorization"] = HEADERS.get("Authorization").format(config.ACCESS_TOKEN)
    # querying the github server
    # delay for 10 seconds because repository 
    # it takes some time to initialize the repo
    print(co.bullets.INFO, co.colors.ORANGE+"Waiting for 10 sec. for initialization of git repo"+co.END)
    time.sleep(10)
    req = requests.post(url, json=Json, headers=HEADERS, timeout=10)
    logging.info("StartWorkFlow|Url|"+url)
    # check if request is successful or not 
    if req is not None:
        print(co.bullets.OK, co.colors.GREEN+"Workflow Successfully started for "+TEMPLATE_NAME+co.END)
        logging.info("StartWorkFlow|Sucess")
        return 0
    else:
        print(co.bullets.ERROR, co.colors.RED+"Could not start Workflow fo     r "+TEMPLATE_NAME+co.END)
        logging.critical("Error in StartWorkFlow|TEMPLATE_NAME|"+TEMPLATE_NAME)
        logging.critical("Error Message|"+json.dumps(req.json()))
        return 1

def CheckRunningTime():
    global REPONAME
    global JOB_ID
    global TIME_LOG_WRITER 
    timing_url = "https://api.github.com/repos/{}/{}/actions/runs/{}/timing".format(config.GITHUB_ACCOUNT_NAME, REPONAME, JOB_ID)
    # authorization header
    HEADERS = config.HEADERS
    HEADERS["Authorization"] = HEADERS.get("Authorization").format(config.ACCESS_TOKEN)
    req = requests.get(timing_url, params=None, headers=HEADERS, timeout=10)
    logging.info("CheckRunningTime|Url|"+timing_url)
    if str(req.status_code).startswith('2'):
        try:
            if req.json()['run_duration_ms'] is not None:
                total_running_time_ms = int(req.json()['run_duration_ms'])
                total_seconds = total_running_time_ms/1000
                Minute = int(total_seconds/60)
                Hour = int(Minute/60)
                Minutes = int(Minute%60)
                Second = int(total_seconds%60)
                print(co.bullets.INFO, "Total Running Time : "+co.colors.CYAN+"{:02d}:{:02d}:{:02d}".format(Hour, Minutes, Second)+co.END+"  [ In MS : "+co.colors.CYAN+"{}".format(total_running_time_ms)+co.END+" ]")
                logging.info("CheckRunningTime|TotoalTime|"+str(total_running_time_ms))
                # write running time on Logging file only once
                if not TIME_LOG_WRITER:
                    today = datetime.datetime.now()
                    Month = today.strftime("%b")
                    Date = today.day
                    currenTime = "{:02d}-{:02d}-{:02d}".format(today.hour, today.minute, today.second)
                    file = open('RunningTime.log', 'a+')
                    file.write("{}:{}:{}:{}:{}\n".format(config.GITHUB_ACCOUNT_NAME,Month,Date,currenTime, total_running_time_ms))
                    file.close()
                    TIME_LOG_WRITER = True
                    return 0
                TIME_LOG_WRITER = False
                return 0
            TIME_LOG_WRITER = False
            return 1
        except:
            logging.critical("CheckRunningTime|Error Message|"+json.dumps(req.json()))
            TIME_LOG_WRITER = False
            return 1
           
def CheckWorkflowStatus():
    global REPONAME
    global TEMPLATE_NAME
    global JOB_ID
    global LOGS_URL
    global HTML_URL
    global LOGS_DOWNLOADED 
    global JOB_RUN_SUCCESS 
    global TIME_LOG_WRITER 
    runsurl = 'https://api.github.com/repos/{}/{}/actions/workflows/{}/runs'.format(config.GITHUB_ACCOUNT_NAME, REPONAME, TEMPLATE_NAME)  # takes input as github_account_name, repoName, templateName
    jobsurl = 'https://api.github.com/repos/{}/{}/actions/runs/{}/jobs' # takes input as github_account_name, repoName, job_id
    # preparing headers
    HEADERS = config.HEADERS
    HEADERS["Authorization"] = HEADERS.get("Authorization").format(config.ACCESS_TOKEN)
    req = requests.get(runsurl, params=None, headers=HEADERS, timeout=10)
    logging.info("CheckWorkflowStatus|URL|"+runsurl)
    if req is not None:
        while True:
            if len(req.json()['workflow_runs']) == 0:
                # workflow is not started currently
                print(co.bullets.INFO, co.colors.ORANGE+"Waiting for the workflow Jobs"+co.END)
                time.sleep(10)
                req = requests.get(runsurl, params=None, headers=HEADERS, timeout=10)
            else:
                break
        ########### Both below values needs to be returned to set into global ########### 
        JOB_ID = req.json()['workflow_runs'][0]['id']    
        LOGS_URL = req.json()['workflow_runs'][0]['logs_url']
        logging.info("Workflow stared with JOB_ID|"+str(JOB_ID))
        print(co.bullets.INFO, "JobID : "+co.colors.CYAN+"{}".format(JOB_ID)+co.END)
        print(co.bullets.OK, co.colors.GREEN+"Monitoring for jobs now"+co.END)
        print(co.bullets.INFO, co.colors.ORANGE+"Press 'Ctrl + C' to Cancel the workflow"+co.END)
        # Set the signal handler
        # assign the sig_handler to the signal SIGINT 
        # for cancelling the workflow when user press Ctrl+C
        signal.signal(signal.SIGINT, sig.sig_handler)
        # monitoring current working jobs
        print(co.bullets.INFO, co.colors.ORANGE+"Checking Running Jobs in 10 seconds of intervals"+co.END)
        PrintedOnce = False
        while True:
            jobsurl = 'https://api.github.com/repos/{}/{}/actions/runs/{}/jobs'.format(config.GITHUB_ACCOUNT_NAME, REPONAME, JOB_ID) # takes input as github_account_name, repoName, job_id
            try:
                req = requests.get(jobsurl, params=None, headers=HEADERS, timeout=10)
                if not req.json()['jobs']:
                    print(co.bullets.ERROR, co.colors.BRED+"Workflow could not Start."+co.END)
                    print(co.bullets.ERROR, co.colors.RED+"There are some problem with supplied {} file!! Please check it Manually.".format(TEMPLATE_NAME)+co.END)
                    logging.critical("CheckWorkflowStatus|Error on Job run|Workflow could not Start.")
                    logging.critical("There are problem with Workflow template file|"+TEMPLATE_NAME)
                    return 3
                # print below lines only once
                if not PrintedOnce:
                    HTML_URL = req.json()['jobs'][0]['html_url']
                    print(co.bullets.INFO, "Visit url for more info: "+co.colors.CYAN+"{}".format(HTML_URL)+co.END)
                    logging.info("URL for Workflow monitoring|"+HTML_URL)
                    PrintedOnce = True
                if req is not None:
                    if req.json()['jobs'][0]['status'] == "completed":
                        print("")
                        if req.json()['jobs'][0]['conclusion'] != "success":
                            JOB_RUN_SUCCESS = False
                            # restore the original signal handler
                            sig.RestoreOriginalHandler()
                            print(co.bullets.ERROR, co.colors.RED+"job completed but there are some errors during the run..."+co.END)
                            logging.critical("Job completed but there are some errors during the run")
                            logging.critical("Check the url|"+HTML_URL)
                            retVal = CheckRunningTime()
                            retVal = DownloadRunnerLogs()
                            print(co.bullets.INFO, "Visit url for more info: {}".format(HTML_URL)+co.END)
                            return 1
                        print(co.bullets.CProcess, co.colors.BGREEN+"Job successfully completed."+co.END)
                        logging.info("Job successfully completed.")
                        # restore the original signal handler
                        sig.RestoreOriginalHandler()
                        retVal = CheckRunningTime()
                        retVal = DownloadRunnerLogs()
                        return 0
                    else:
                        laststep = None
                        for step in req.json()['jobs'][0]['steps']:
                            if step['status'] == "completed":
                                laststep = step['name']
                        print("                                                            ", end="\r")   # for clearing the whole line
                        print(co.bullets.INFO, co.colors.ORANGE+"Last step executed: {} .".format(laststep)+co.END, end="\r")
                        time.sleep(2)
                        print(co.bullets.INFO, co.colors.ORANGE+"Last step executed: {} ..".format(laststep)+co.END, end="\r")
                        time.sleep(2)
                        print(co.bullets.INFO, co.colors.ORANGE+"Last step executed: {} ...".format(laststep)+co.END, end="\r")
                        time.sleep(2)
                        print(co.bullets.INFO, co.colors.ORANGE+"Last step executed: {} ....".format(laststep)+co.END, end="\r")
                        time.sleep(2)
                        print(co.bullets.INFO, co.colors.ORANGE+"Last step executed: {} .....".format(laststep)+co.END, end="\r")
                        logging.info("Last step executed|"+str(laststep))
                        time.sleep(2)
                        continue
            except:
                logging.critical("Error During Checking Running Workflow status|URL"+jobsurl)    
                break
        if req.json()['jobs'][0]['conclusion'] != "success":
            JOB_RUN_SUCCESS = False
            # restore the original signal handler
            sig.RestoreOriginalHandler()
            print("")
            print(co.bullets.ERROR, co.colors.RED+"Job completed but there are some errors during the run..."+co.END)
            HTML_URL = req.json()['jobs'][0]['html_url']
            retVal = CheckRunningTime()
            retVal = DownloadRunnerLogs()
            print(co.bullets.INFO, "Visit url for more info: {}".format(HTML_URL)+co.END)
            logging.critical("Job completed but there are some errors during the run")
            logging.critical("Check the url|"+HTML_URL)
            return 1
        sig.RestoreOriginalHandler()
        return 2

def DeleteWorkflow():
    global REPONAME
    global JOB_ID
    delete_url = "https://api.github.com/repos/{}/{}/actions/runs/{}".format(config.GITHUB_ACCOUNT_NAME, REPONAME, JOB_ID)
    print(co.bullets.INFO, co.colors.ORANGE+"Deleting workflow with JOB_ID : {}".format(JOB_ID)+co.END)
    # authorization header
    HEADERS = config.HEADERS
    HEADERS["Authorization"] = HEADERS.get("Authorization").format(config.ACCESS_TOKEN)
    # sleep for 2 seconds
    time.sleep(2)
    req = requests.delete(delete_url, data=None, headers=HEADERS, timeout=10)
    logging.info("DeleteWorkflow|Url|"+delete_url)
    if str(req.status_code).startswith('2'):
        print(co.bullets.OK, co.colors.GREEN+"Workflow Deleted successfully.!!"+co.END)
        logging.info("DeleteWorkFlow|Sucess")
        return 0
    else:
        print(co.bullets.ERROR, co.colors.RED+"Error received during workflow cancellation : {}".format(req.json())+co.END)
        print(co.bullets.ERROR, co.colors.RED+"Delete it manually by going to Repository settings."+co.END)
        logging.critical("Error in DeleteWorkFlow|RepoName|"+REPONAME)
        logging.critical("Error Message|"+json.dumps(req.json()))
        return 1 

def DownloadRunnerLogs():
    global REPONAME
    global LOGS_URL
    global LOGS_DOWNLOADED
    if LOGS_DOWNLOADED:
        return 0, True
    HEADERS = config.HEADERS
    HEADERS["Authorization"] = HEADERS.get("Authorization").format(config.ACCESS_TOKEN)
    if not LOGS_URL:
        print(co.bullets.ERROR, co.colors.RED+" Logs URL is not setted up.!!"+co.END)
        logging.critical("Error in DownloadRunnerLogs|Logs URL is not setted up.!!")
    else:
        print(co.bullets.INFO, "Requesting for RunnerLogs.."+co.END)
        logreq = requests.get(LOGS_URL,headers=HEADERS, allow_redirects=True, stream=True, timeout=10)
        if str(logreq.status_code).startswith('2') or logreq.status_code == 302:
            print(co.bullets.INFO, "Requesting RunnerLogs again for log after 5 second delay..."+co.END)
            time.sleep(5)
            logreq = requests.get(LOGS_URL,headers=HEADERS, allow_redirects=True, stream=True, timeout=10)
        if str(logreq.status_code).startswith('2') or logreq.status_code == 302:
            FileName = "{}_RunLogs.zip".format(REPONAME)
            Path = "RunnerLogs/{}".format(FileName)
            try:
                zfile = open(Path, 'wb')
                zfile.write(logreq.content)
                zfile.close()
            except:
                print(co.bullets.ERROR, co.colors.RED+"Some Problem during writing downloaded ZIP files."+co.END)
            print(co.bullets.DONE, co.colors.GREEN+"Log File Downloaded sucessfully: {}".format(Path)+co.END)
            logging.info("Log File Downloaded sucessfully: "+Path)
        else:
            print(co.bullets.ERROR, co.colors.RED+"Something Error occurs during Log Request|Status_Code:{}".format(logreq.status_code)+co.END)
            logging.critical("Something Error occurs during Log Request|Status_Code:"+str(logreq.status_code))

def CancelWorkflow():
    global REPONAME
    global JOB_ID
    global HTML_URL
    cancel_url = "https://api.github.com/repos/{}/{}/actions/runs/{}/cancel".format(config.GITHUB_ACCOUNT_NAME, REPONAME, JOB_ID)
    print(co.bullets.INFO, co.colors.ORANGE+"Cancelling workflow with JOB_ID : {}".format(JOB_ID)+co.END)
    # authorization header
    HEADERS = config.HEADERS
    HEADERS["Authorization"] = HEADERS.get("Authorization").format(config.ACCESS_TOKEN)
    req = requests.post(cancel_url, data=None, headers=HEADERS, timeout=10)
    logging.info("CancelWorkflow|Url|"+cancel_url)
    if str(req.status_code).startswith('2'):
        print(co.bullets.OK, co.colors.GREEN+"Workflow cancelled successfully.!!"+co.END)
        logging.info("CancelWorkflow|Sucess")
        # delete the workflow
        DeleteWorkflow()
        CheckRunningTime()
        DownloadRunnerLogs()
        sys.exit(0)
    else:
        print(co.bullets.ERROR, co.colors.RED+"Error received during workflow cancellation : {}".format(req.json())+co.END)
        print(co.bullets.ERROR, co.colors.RED+"Cancel it manually with URL : {}".format(HTML_URL)+co.END)
        logging.critical("Error in CancelWorkflow|RepoName|"+REPONAME)
        logging.critical("Error Message|"+json.dumps(req.json()))
    CheckRunningTime()
    DownloadRunnerLogs()
    sys.exit(1)

def WorkflowController(RepoName, TemplateName):
    # Setting up soem global variables 
    # for this module internal use 
    global REPONAME
    REPONAME = RepoName
    global TEMPLATE_NAME 
    TEMPLATE_NAME = TemplateName
    # initiate the workflow 
    # starting workflow action
    if StartWorkflow():
        # some problem occurs
        sys.exit()
    # Tracking the workflow run 
    retVal = 0
    retVal = CheckWorkflowStatus()
    if retVal == 0:
        # clone repository
        if gitlibs.CloneRepo(REPONAME):
            print(co.bullets.ERROR, co.colors.BRED+"Could not clone the remote Repository."+co.END)
            sys.exit(1)
        # delete workflow 
        if DeleteWorkflow():
            print(co.bullets.ERROR, co.colors.BRED+"Could not Delete the Workflow Run."+co.END)
            sys.exit(1)
        # Delete remote repository
        if gitlibs.DeleteRepo(REPONAME):
            print(co.bullets.ERROR, co.colors.BRED+"Could not Delete the Repository!! Error Occured.."+co.END)
            sys.exit(1)
    elif retVal == 1:
        print(co.bullets.ERROR, co.colors.BRED+"Error during workflow run.!!."+co.END)
        sys.exit(1)
    elif retVal == 3:
        print(co.bullets.ERROR, co.colors.RED+"Go and Check Remote Repository : "+co.colors.CYAN+"'https://github.com/{}/{}/actions' ".format(config.GITHUB_ACCOUNT_NAME, REPONAME)+co.END)
    else:
        print(co.bullets.ERROR, co.colors.RED+"Go and Check Remote Repository : "+co.colors.CYAN+"'https://github.com/{}/{}/actions' ".format(config.GITHUB_ACCOUNT_NAME, REPONAME)+co.END)








