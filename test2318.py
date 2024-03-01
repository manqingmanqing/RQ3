# import requests
# import json

# # 定义GraphQL查询
# query = """
# query ($username: String!) {
#   user(login: $username) {
#     repositories(orderBy: {field: STARGAZERS, direction: DESC}) {
#       pageInfo {
#         hasNextPage
#         endCursor
#       }
#       nodes {
#         name
#         stargazers {
#           totalCount
#         }
#       }
#     }
#   }
# }
# """

# # 初始变量
# variables = {
#     "username": "atiger77"
# }

# # 设置GraphQL API的URL
# url = 'https://api.github.com/graphql'

# # 设置请求头，包含GitHub Personal Access Token
# headers = {
#     'Authorization': 'Bearer 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',
#     'Content-Type': 'application/json',
# }

# # 分页获取所有仓库信息的函数
# def get_all_repos(username, token):
#     repos = []

#     response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
#     if response.status_code != 200:
#         print("Error:", response.status_code, response.text)
#         return repos
#     data = response.json()
#     print(data)
#     if not data['data']['user']['repositories']['pageInfo']['hasNextPage']:
#         return repos
#     repos.extend(data['data']['user']['repositories']['nodes'])
#     variables['cursor'] = data['data']['user']['repositories']['pageInfo']['endCursor']
#     return repos

# # 获取并打印所有仓库的信息
# all_repos = get_all_repos("atiger77", "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")

# for repo in all_repos:
#     print(f"Repo Name: {repo['name']}, Stars: {repo['stargazers']['totalCount']}")

import requests
import json
import csv
import glob
import time
import sys
import os
cmd = 'curl -s --retry 3 --retry-delay 5 -u RinForFuture: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 '

# Define your GraphQL query
query = """
query ($username: String!, $cursor: String) {
  user(login: $username) {
    repositories(first: 100, after: $cursor, orderBy: {field: STARGAZERS, direction: DESC}) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        isFork
        parent {
          name
          owner {
            login
          }
          repositoryTopics(first: 10) {
            nodes {
              topic {
                name
              }
            }
          }
        }
        repositoryTopics(first: 10) {
          nodes {
            topic {
              name
            }
          }
        }
        owner {
          login
        }
      }
    }
  }
}
"""


def process_repository_data(repo):
    if repo['isFork'] and 'parent' in repo and repo['parent'] != None:
      print(repo['parent'])
      # For forked repositories, retain the original repository's name and topics
      repo_name = f"{repo['parent']['owner']['login']}/{repo['parent']['name']}"
      topics = [topic['topic']['name'] for topic in repo['parent']['repositoryTopics']['nodes']]
    else:
      # For non-forked repositories, use the current repository's name and topics
      repo_name = f"{repo['owner']['login']}/{repo['name']}"
      topics = [topic['topic']['name'] for topic in repo['repositoryTopics']['nodes']]
    
    return repo_name, topics


def get_all_repos(username, token):
     # Initialize lists for repository names and topics
    repo_names = []
    repo_topics = []

    url = 'https://api.github.com/graphql'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    repos = []
    cursor = None  # Start with no cursor
    
    while True:
        variables = {"username": username, "cursor": cursor}
        response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
        if response.status_code == 200:
            data = response.json()
            #print(data)
            if 'errors' in data:
                print("Error fetching repositories:", data['errors'])
                if 'type' in data['errors'] and data['errors']['type'] == 'RATE_LIMITED':
                    time.sleep(60 * 60)
                    sys.exit()
                
            repos.extend(data['data']['user']['repositories']['nodes'])
            pageInfo = data['data']['user']['repositories']['pageInfo']
            if pageInfo['hasNextPage']:
                cursor = pageInfo['endCursor']  # Prepare the cursor for the next page
            else:
                break  # Exit the loop if there are no more pages
        else:
            print("Error fetching repositories:", response.text)
            break
    for repo in repos:
        repo_name, topics = process_repository_data(repo)
        repo_names.append(repo_name)
        repo_topics.extend(topics)  # Assumin
    return repo_names, repo_topics

def forkrepo(repourl):
    url_page = repourl
    html_ = os.popen(cmd + url_page)
    html = json.loads(html_.buffer.read().decode(encoding='utf-8'))
    if 'message' in html and 'API rate limit' in html['message']:
        time.sleep(60*60)
        sys.exit()
    if len(html) == 0:
        return False,'',[]
    if len(html)==2:
        if 'message' in html:
            return False,'',[]
    if len(html)==3:
        if 'url' in html:
            url_page = html['url']
            html_ = os.popen(cmd + url_page)
            html = json.loads(html_.buffer.read().decode(encoding='utf-8'))
    if len(html)==2:
        if 'message' in html:
            return False,'',[]
    if len(html) == 0:
        return False,'',[]
    
    forkflag = html['fork']
    #print(repourl)

    if forkflag and 'source' in html:
        origname = html['source']['full_name']
        topics = html['source']['topics']
    else:
        origname = html['full_name']
        topics = html['topics']
    return True,origname,topics

def usercheck(username,reponame,notexistpath):
    url_page = "https://api.github.com/users/" + username
    html_ = os.popen(cmd + url_page)
    html = json.loads(html_.buffer.read().decode(encoding='utf-8'))
    #print(html)
    if 'message' in html and 'Not Found' in html['message']:
        with open(notexistpath, 'a', newline='',errors='replace') as f:
            writer = csv.writer(f)
            writer.writerow([username,reponame])
            return False
    if 'message' in html and 'API rate limit' in html['message']:
        time.sleep(20*60)
        sys.exit()
    return True


token = "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"
exsitllist = []
notexistpath = "Notexist/2318.csv"
rootpath = "datafile1/2318/"
targetfile = "topic2/TopicAndFork_2318.csv"
with open(targetfile, 'r',errors='replace') as f:
    reader = csv.reader(f)
    for a in reader:
        name1 = a[0].strip()
        name2 = a[1].strip()
        list1 = [name1,name2]
        exsitllist.append(list1)
with open(targetfile, 'r',errors='replace') as f:
    reader = csv.reader(f)
    for a in reader:
        name1 = a[0].strip()
        name2 = a[1].strip()
        list1 = [name1,name2]
        exsitllist.append(list1)
notexsitllist = []
if os.path.exists(notexistpath):
    with open(notexistpath, 'r',errors='replace') as f:
        reader = csv.reader(f)
        for a in reader:
            name1 = a[0].strip()
            name2 = a[1].strip()
            list2 = [name1,name2]
            notexsitllist.append(list2)


flag5 = 0
for subdir,dirs,files in os.walk(rootpath):
    for file in files:
        if file == "useroplist.csv":
            filepath = os.path.join(subdir,file)
            alldata = []
            with open(filepath, 'r',errors='replace') as f:
                reader = csv.reader(f)
                for a in reader:
                    reponame = a[0]
                    alldata.append(a)
            print(filepath)
            repourl = "https://api.github.com/repos/" + reponame
            flag,realrepo,repotopic = forkrepo(repourl)
            
            for i in range(len(alldata)):
                username = alldata[i][1]
                reponame = alldata[i][0]
                list2 = [username,reponame]
                if list2 in exsitllist:
                    continue
                if list2 in notexsitllist:
                    continue
                flag1 = 0
                flag2 = 0
                print(username,reponame)

                if '[bot]' in username:
                    continue
                
                userflag = usercheck(username,reponame,notexistpath)
                if userflag == False:
                  continue
                
                userrepolist,usertopic = get_all_repos(username, token)
                if realrepo in userrepolist :
                    flag1 =1
                for j in range(len(repotopic)):
                    if repotopic[j] in usertopic:
                        flag2 = 1
                        break
                data = [username,reponame]
                data.append(flag1)
                data.append(flag2)
                with open(targetfile, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(data)
