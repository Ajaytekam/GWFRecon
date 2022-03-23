import sys
import libs.gitlibs as gitlibs
import libs.workflowlibs as wflibs
import libs.coloredOP as co

#========
# Workflow Template : SubDomainEnum.yml
TemplateName = "MisConfigScan.yml"
TemplateData = """
name: CI

# Controls when the workflow will run
on:
  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

# A workflow run is made up of one or more jobs that can run sequentially or in parallel
jobs:
  # This workflow contains a single job called "build"
  build:
    # The type of runner that the job will run on
    runs-on: ubuntu-latest

    # Steps represent a sequence of tasks that will be executed as part of the job
    steps:
      # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
      - uses: actions/checkout@v2
      - uses: actions/setup-go@v2
        with:
          go-version: '1.17.x'

      # Runs a set of commands using the runners shell
      - name: Prepare System
        run: sudo apt-get update -y;
 
      - name: Install nuclei 
        run: go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest 

      - name: Performing MisConfig Scan 
        run: |
          nuclei -t cves/ -l subdomains.txt -o cves.txt --silent
          nuclei -t default-logins/ -l subdomains.txt -o default_logins.txt --silent
          nuclei -t exposures/ -l subdomains.txt -o exposures.txt --silent
          nuclei -t misconfiguration/ -l subdomains.txt -o misconfigurations.txt --silent
          nuclei -t takeovers/ -l subdomains.txt -o takeovers.txt --silent
          nuclei -t vulnerabilities/ -l subdomains.txt -o bulnerabilities.txt --silent

      # github doesn't allow you to commit files > 100M
      - name: Pruning files greater than 100MB
        run: find . -size +99M -delete
         
      - name: Commit and push
        uses: stefanzweifel/git-auto-commit-action@v4.2.0
        with:
          commit_message: Commit output files
          commit_user_name: 'Basic Shell'
          commit_user_email: 'github-actions.shell@github.com'
"""
### 
#========

def Execute(subdomainList):
    global TemplateName
    global TemplateData
    # Setting up the github repository 
    repoName = gitlibs.SetRepoName()
    if gitlibs.CreateRemoteRepo(repoName):
        print(co.bullets.ERROR, co.colors.BRED+"Could not create repository: Exiting Program."+co.END)
        sys.exit(1)
    # pushing subdomain list 
    try:
        SubDFileContent = open(subdomainList, "r").read()
    except:
        print("Error in reading subdomains input file!!!")
        sys.exit(1)
    if gitlibs.CommitFile(repoName, SubDFileContent, "subdomains.txt", "subdomains list file commited."): 
        print(co.bullets.ERROR, co.colors.BRED+"Could not commit subdomains file on the repository.!!."+co.END)
        sys.exit(1)
    # pushing workflow yml file 
    TemplatePath = '.github/workflows/{}'.format(TemplateName) 
    commitMessage = "github sample workflow added"
    if gitlibs.CommitFile(repoName, TemplateData, TemplatePath, commitMessage):
        print(co.bullets.ERROR, co.colors.BRED+"Could not commit config files on the repository.!!."+co.END)
        sys.exit(1)
    # initiate the workflow if everything is OK
    wflibs.WorkflowController(repoName, TemplateName)
