import sys
import libs.gitlibs as gitlibs
import libs.workflowlibs as wflibs
import libs.coloredOP as co

#  
# 

#========
# Workflow Template : SubDomainEnum.yml
TemplateName = "SubDomainEnum.yml"
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
      - uses: actions/setup-python@v2 
        with:
          python-version: '3.x'
      - uses: actions/setup-go@v2
        with:
          go-version: '1.17.x'

      # Runs a set of commands using the runners shell
      - name: Prepare System
        run: |
          sudo apt-get update -y;
          sudo apt-get install wget -y;

      - name: Install amass
        run: sudo snap install amass
          
      - name: Install assetfinder
        run: go install github.com/tomnomnom/assetfinder@latest
        
      - name: Install findomain
        run: |
          wget https://github.com/Findomain/Findomain/releases/download/5.0.0/findomain-linux
          chmod +x findomain-linux
          mv findomain-linux /home/runner/go/bin/findomain
  
      - name: Amass Subdomain Scan
        run: amass enum --passive -o amass.txt -d {} > /dev/null 2>&1

      - name: assetfinder subdomain Scan
        run: assetfinder --subs-only {} >> assetfinder.txt

      - name: findomain subdomain Scan
        run: findomain -q --target {} --threads 20 >> findomain.txt
        
      - name: Merging and sorting all files
        run: |
          cat amass.txt assetfinder.txt findomain.txt | sort -u >> PassiveSubD.txt
          rm amass.txt assetfinder.txt findomain.txt

      # Code for splitting file which are +99MB
      - name: Splitting big files 
        run: |
          if [ `du -m PassiveSubD.txt | cut -d" " -f1 | tr -d -c 0-9` -gt 99 ]
          then
            split -d -b20971520 PassiveSubD.txt PassiveSubD
          fi
          
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

def Execute():
    global TemplateName
    global TemplateData
    TemplateData = TemplateData.format("indeed.com", "indeed.com", "indeed.com")
    # Setting up the github repository 
    repoName = gitlibs.SetRepoName()
    if gitlibs.CreateRemoteRepo(repoName):
        print(co.bullets.ERROR, co.colors.BRED+"Could not create repository: Exiting Program."+co.END)
        sys.exit(1)
    # pushing workflow yml file 
    TemplatePath = '.github/workflows/{}'.format(TemplateName) 
    commitMessage = "github sample workflow added"
    if gitlibs.CommitFile(repoName, TemplateData, TemplatePath, commitMessage):
        print(co.bullets.ERROR, co.colors.BRED+"Could not commit config files on the repository.!!."+co.END)
        sys.exit(1)
    # initiate the workflow if everything is OK
    wflibs.WorkflowController(repoName, TemplateName)
