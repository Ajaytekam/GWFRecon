import sys
import libs.gitlibs as gitlibs
import libs.workflowlibs as wflibs
import libs.coloredOP as co

# This is a simple test runner
# which runs some simple command
# on the CICD 

#========
# Workflow Template : PortAndServices.yml
TemplateName = "JSScan.yml"
TemplateData = """name: CI

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

      #  Setup python3 environment
      - name: setup python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8.0'

      # Runs a set of commands using the runners shell
      - name: Prepare System
        run: |
          sudo apt-get update -y;

      - name: Install gau, hakrawler, subjs, httpx 
        run: |
          go install github.com/lc/gau/v2/cmd/gau@latest  
          go install github.com/hakluke/hakrawler@latest   
          GO111MODULE=on go get -u -v github.com/lc/subjs@latest  
          go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

      - name: Install pip, linkfinder, secretfinder
        run: |
          python -m pip install --upgrade pip
          git clone https://github.com/m4ll0k/SecretFinder.git secretfinder 
          pushd secretfinder
          pip install -r requirements.txt
          popd
          git clone https://github.com/GerbenJavado/LinkFinder.git linkfinder    
          pushd linkfinder
          pip install -r requirements.txt
          popd

      - name: Testrun of linkfinder, secretfinder
        run: |
          python3 linkfinder/linkfinder.py --help 
          python3 secretfinder/secretfinder.py --help 

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

def Execute(massdnsfile):
    global TemplateName
    global TemplateData
    Filename = massdnsfile.split('/')[-1]
    TemplateData = TemplateData.format(Filename)
    # Setting up the github repository 
    repoName = gitlibs.SetRepoName()
    if gitlibs.CreateRemoteRepo(repoName):
        print(co.bullets.ERROR, co.colors.BRED+"Could not create repository: Exiting Program."+co.END)
        sys.exit(1)
    # push massdns file 
    try:
        MassdnsFile = open(massdnsfile, "r").read()
    except:
        print("Error in reading input file!!!")
        sys.exit(1)
    # pushing massdns result file 
    if gitlibs.CommitFile(repoName, MassdnsFile, Filename, "massdns result file commited"):
        print(co.bullets.ERROR, co.colors.BRED+"Could not commit massdns result file on the repository.!!."+co.END)
        sys.exit(1)
    # pushing workflow yml file 
    TemplatePath = '.github/workflows/{}'.format(TemplateName) 
    commitMessage = "github sample workflow added"
    if gitlibs.CommitFile(repoName, TemplateData, TemplatePath, commitMessage):
        print(co.bullets.ERROR, co.colors.BRED+"Could not commit config files on the repository.!!."+co.END)
        sys.exit(1)
    # initiate the workflow if everything is OK
    wflibs.WorkflowController(repoName, TemplateName)
