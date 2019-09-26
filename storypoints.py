from jira import JIRA
from collections import defaultdict, namedtuple
import json # only for displaying output nicely
from private_jira_password import my_auth
ska_jira = JIRA('https://jira.skatelescope.org', auth=my_auth)


points = {} # by person, then by sprint
QUERY = 'Sprint = "{}" and assignee = "{}"'

people = ["Bolin, Andrew", "Bengston, Keith", "Humphrey, David",
        "Hampson, Grant", "Troup, Euan", "Chen, Yuqing", "Bunton, John",
        "Abel, Norbert"]
people.sort()

for person in people:
    points[person] = []
    for s in range(1,6):
        sprint = "Perentie Sprint 4.{}".format(s)
        q = QUERY.format(sprint, person)
        issues = ska_jira.search_issues(q)
        #print("query: {}".format(q))
        sprint_total_sp = 0
        for i in issues: 
            sp = i.fields.customfield_10002
            #print("%s %s is %d points for %s" % (i.fields.issuetype.name, i.key, sp, person))
            sprint_total_sp += sp
        points[person].append(sprint_total_sp)

for p in people:
    print("{}".format(p), end='\t')
    for n in points[p]:
        print("%3i" % n, end='  ')
    print()
