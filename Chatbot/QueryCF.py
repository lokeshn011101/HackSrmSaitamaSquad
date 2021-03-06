import requests
import json
maxm = 100000
class QueryCodeForces:
    
    def __init__(self):
        print("Start")
    
    def problemRecommender(self):
        self.problemSuggested = {}
        fp = open('tags.txt')
        tags = fp.read().split("\n")
        fp.close()
        for tag in tags:
            if tag in self.tagRating:
                userlevel = self.tagRating[tag]
            else:
                userlevel = 1
            
            count = 0
            for problem in self.problemQueue[tag]:
                if(int(problem[0]) == userlevel):
                    key = str(problem[1])+str(problem[2])
                    if key not in self.solvedProblemsByUser.keys():    
                        count += 1
                        problemUrl = "http://codeforces.com/problemset/problem/" + str(problem[1]) + "/" + str(problem[2])
                        if tag in self.problemSuggested:
                            self.problemSuggested[tag] += [(problem, problemUrl)]
                        else:
                            self.problemSuggested[tag] = [(problem, problemUrl)]
                if(count == 3):
                    break

        print(len(self.problemSuggested))
        for prob in self.problemSuggested:
            for pp in self.problemSuggested[prob]:
                print(pp)
        print("Problem Suggestion Done")
        return self.problemSuggested
        
    def userStat(self, handle):
        urlUserStat ="http://codeforces.com/api/user.status?handle="+handle+"&from=1&count=" + str(maxm)
        urlUserRating = "http://codeforces.com/api/user.info?handles=" + handle
        res = requests.get(urlUserStat)
        data = json.loads(res.text)
        #print data["result"]
        self.solvedProblemsByUser = {}
        self.tagsSolved = {}
        Nlength = len(data["result"])
        print(Nlength)
        for submission in data["result"]:
            contestId = str(submission['problem']['contestId'])
            index = str(submission['problem']['index'])
            key = contestId+index
            if(str(submission["verdict"]) == "OK"):
                if key not in self.solvedProblemsByUser.keys():
                    self.solvedProblemsByUser[key] = key
            for tags in submission["problem"]["tags"]:
                if(str(tags) != ""):
                    if tags in self.tagsSolved:
                        self.tagsSolved[tags] += 1
                    else:
                        self.tagsSolved[tags] = 1
                
        query = requests.get(urlUserRating)
        qdata = json.loads(query.text)

        userRating = int(qdata["result"][0]["rating"])
        self.tagRating = {}
        for tags in self.tagsSolved:
            if(userRating > 2400):
                self.tagRating[tags] = 5
            elif(userRating > 2000):
                self.tagRating[tags] = 4
            elif(userRating > 1500):
                self.tagRating[tags] = 3
            elif(userRating > 1000):
                self.tagRating[tags] = 2
            else:
                self.tagRating[tags] = 1

        print("user "+ handle+" processing done")
        
    def EvaluateDifficulty(self, solvedCount):             
        coeff = [ 0.00000000e+00 ,-5.57468040e-03 , 3.96749217e-06, -1.43253771e-09,  2.37559930e-13, -1.45370970e-17]
        x = solvedCount
        res = coeff[0] + x*coeff[1] + pow(x,2)*coeff[2] + pow(x,3)*coeff[3] +pow(x,4)*coeff[4] +pow(x,5)*coeff[5] + 6
        
        return res
    
    def problemsetUpdater(self):
        print("downloading data")
        urlAllProblems = "http://codeforces.com/api/problemset.problems"
        res = requests.get(urlAllProblems)
        data = json.loads(res.text)
        print("Problem Data download complete, performing update")
        with open('Problems.txt','w') as outfile:
            json.dump(data,outfile)  
        print("Problem Set Updated! ")

    def allProblemStat(self):
        f = open('Problems.txt', 'r')
        data = json.loads(f.read())
        f.close()
        self.AllProblemData = {}
        print(len(data["result"]["problems"]))
        N = len(data["result"]["problems"])
        for i in range(N):
            contestId = data["result"]["problems"][i]["contestId"]
            index = data["result"]["problems"][i]["index"]
            name = data["result"]["problems"][i]["name"]
            solvedCount = data["result"]["problemStatistics"][i]["solvedCount"]
            tags = data["result"]["problems"][i]["tags"]
            difficulty = self.EvaluateDifficulty(int(solvedCount))
            self.AllProblemData[str(contestId) + str(index)] = (contestId, index, name,solvedCount ,difficulty, tags)
        print("All Problem Processed!")

    def prepareProblemQueue(self):

        self.problemQueue = {}
        for problems in self.AllProblemData:
            contestId = self.AllProblemData[problems][0]
            index = self.AllProblemData[problems][1]
            difficulty  = self.AllProblemData[problems][4]
            name = self.AllProblemData[problems][2]
            for tag in self.AllProblemData[problems][5]:
                if tag in self.problemQueue:
                    self.problemQueue[tag] += [(difficulty, contestId, index, tag, name)]
                else:
                    self.problemQueue[tag] = [(difficulty, contestId, index, tag, name)]
        print("Problem Queue Prepared!")

