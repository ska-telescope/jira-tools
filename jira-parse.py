from jira import JIRA
from collections import defaultdict, namedtuple
import json # only for displaying output nicely
from private_jira_password import my_auth
ska_jira = JIRA('https://jira.skatelescope.org', auth=my_auth)

ShortJiraIssue = namedtuple('ShortJiraIssue', 'key permalink summary status') 

def MakeNamedTuple(jira_issue):
    return ShortJiraIssue(jira_issue.key, jira_issue.permalink(), jira_issue.fields.summary, jira_issue.fields.status.name.lower())

def StringJiraIssue(sji):
    return "%s %s" % (sji.key, sji.summary)

def GvFormatIssue(i):
    col = colours[all_issues[i].status]
    status = all_issues[i].status
    label = '{}\n{}'.format(i, status)
    return '"{}" [label="{}" style=filled fillcolor="{}"];\n'.format(i, label, col)

tree = {}
all_issues = {}
colours = defaultdict(str)
colours["discarded"] = "dimgray"
colours["in progress"] = "coral"
colours["implementing"] = "chocolate"
colours["releasing"] = "gold"
colours["done"] = "chartreuse2"
colours["ready for acceptance"] = "gold2"
colours["achieved"] = "forestgreen"
colours["identified"] = "dodgerblue3"
colours["blocked"] = "firebrick1"
colours["to do"] = "deepskyblue4"


TEAM = "Team_" + "PERENTIE"
query = 'type = Objective and labels = "{}" and fixVersion="PI4"'.format(TEAM)
objectives = ska_jira.search_issues(query)
print("Starting with query {}".format(query))

for o in objectives: 
    print("Crawling %s %s" % (o.fields.issuetype.name, o.key))
    all_issues[o.key] = MakeNamedTuple(o)
    tree[o.key] = {} # make tree a defaultdict(defaultdict(list)) instead?
    for ol in o.fields.issuelinks: # ol: "objective links"
        f = None
        if str(getattr(ol, 'type', None))=='Parent/Child':
            if getattr(ol, 'outwardIssue', False):
                f = ska_jira.issue(ol.outwardIssue.key)
        elif str(getattr(ol, 'type', None))=='Relates':
            if getattr(ol, 'inwardIssue', False):
                f = ska_jira.issue(ol.inwardIssue.key)
        if f:
            # check if we have been here before (someone might link features to each other or something)
            if f.key in all_issues:
                continue # no need to re-traverse children
            all_issues[f.key] = MakeNamedTuple(f)
            tree[o.key][f.key] = [] 
            for fl in f.fields.issuelinks:
                story = None
                if str(getattr(fl, 'type', None))=='Parent/Child':
                    if getattr(fl, 'outwardIssue', False):
                        story = MakeNamedTuple(ska_jira.issue(fl.outwardIssue.key))
                elif str(getattr(fl, 'type', None))=='Relates':
                    if getattr(fl, 'inwardIssue', False):
                        story = MakeNamedTuple(ska_jira.issue(fl.inwardIssue.key))
                if story:
                    tree[o.key][f.key].append(story.key)
                    all_issues[story.key] = story

### it would be a lot faster to test this if I wrote the dicts out here
### then read them in to run the below without crawling jira...

# output
# there must be a standard tree traversal function that I should be using here...
for obj in tree:
    print( StringJiraIssue(all_issues[obj]) )
    for feat in tree[obj]:
        print("\t" + StringJiraIssue(all_issues[feat]) )
        for sty in tree[obj][feat]:
            print("\t\t" + StringJiraIssue(all_issues[sty]) )


with open('jira_parse_out.gv', 'w') as gv:
    gv.write("digraph objectives {\n")
    gv.write('root="{}";\n'.format(TEAM))
    gv.write('ranksep=5;\n')
    gv.write('"{}" [style=filled fillcolor="crimson"];\n'.format(TEAM))
    for obj in tree:
        gv.write('"{}" -> "{}";\n'.format(TEAM, obj))
        gv.write(GvFormatIssue(obj))
        for feat in tree[obj]:
            gv.write('  "{}" -> "{}";\n'.format(obj, feat))
            gv.write('  ' + GvFormatIssue(feat))
            for sty in tree[obj][feat]:
                gv.write('    "{}" -> "{}";\n'.format(feat,sty))
                gv.write('    ' + GvFormatIssue(sty))
    gv.write("}")
