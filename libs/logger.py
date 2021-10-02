import logging

def SetLogger(repoName):
    LogFile = "logs/"+repoName+".log" 
    logging.basicConfig(level=logging.INFO, filename=LogFile, filemode='w')
