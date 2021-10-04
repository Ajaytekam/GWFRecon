import sys
import libs.gitlibs as gitlibs
import libs.workflowlibs as wflibs
import libs.coloredOP as co

# This is a simple test runner
# which runs some simple command
# on the CICD 

def Execute():
    # Setting up the github repository 
    repoName = gitlibs.SetRepoName()
    if gitlibs.CreateRemoteRepo(repoName):
        print(co.bullets.ERROR, co.colors.BRED+"Could not create repository: Exiting Program."+co.END)
        sys.exit(1)
    # pushing workflow yml file 
    TemplateName = 'sample.yml' 
    TemplatePath = '.github/workflows/{}'.format(TemplateName)
    # Opening a file
    with open(TemplateName, 'r') as rf:
        FileContent = rf.read()
    commitMessage = "github sample workflow added"
    if gitlibs.CommitFile(repoName, FileContent, TemplatePath, commitMessage):
        print(co.bullets.ERROR, co.colors.BRED+"Could not commit config files on the repository.!!."+co.END)
        sys.exit(1)
    # initiate the workflow if everything is OK
    wflibs.WorkflowController(repoName, TemplateName)
