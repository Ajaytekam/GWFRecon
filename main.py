#!/usr/bin/python3 

import sys
import libs.gitlibs as gitlibs
import libs.coloredOP as co
import signal
import enumlibs.TestRunner as TestRunner

def main():
    '''
    # set reponame
    global REPONAME
    REPONAME = gitlibs.SetRepoName() 
    # create repo
    if gitlibs.CreateRemoteRepo(REPONAME):
        print(co.bullets.ERROR, co.colors.BRED+"Could not create repository: Exiting Program."+co.END)
        sys.exit(1)
    ### commit a file 
    FileName = '/mnt/c/Users/ajay/OffceWork/DevLab/GWFRecon/test.txt' # filename  with full path
    FileContent = gitlibs.readFile(FileName)
    path = 'test.txt' # 
    commitMessage = "This is a test commit"
    if gitlibs.CommitFile(REPONAME, FileContent, path, commitMessage):
        print(co.bullets.ERROR, co.colors.BRED+"Could not commit config files on the repository.!!"+co.END)
        sys.exit(1)
    ### commit workflow file 
    WF_TEMPLATE = './example.yml'
    FileContent = gitlibs.readFile(WF_TEMPLATE) 
    ## add data into workflow file 
    if ports:
        FileContent = FileContent.format(ipList, ports) 
    else:
        FileContent = FileContent.format(ipList)
    path = '.github/workflows/{}'.format(WF_TEMPLATE)
    commitMessage = "workflow file {} is commited".format(WF_TEMPLATE)
    if gitlibs.CommitFile(REPONAME, FileContent, path, commitMessage):
        print(co.bullets.ERROR, co.colors.BRED+"Could not commit workflow file on the repository.!!."+co.END)
        sys.exit(1) 
    ### clone Repo 
    if gitlibs.CloneRepo(REPONAME):
        print(co.bullets.ERROR, co.colors.BRED+"Could not clone the remote Repository."+co.END)
    ### Delet repo
    if gitlibs.DeleteRepo(repoName):
        print(co.bullets.ERROR, co.colors.BRED+"Could not Delete the Repository!! Error Occured.."+co.END)
    '''
    TestRunner.Execute()

if __name__ == "__main__":
    main()
