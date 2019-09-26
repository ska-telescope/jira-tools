#!/bin/bash

python3 jira-parse.py && 
    twopi -Tpng -o jira-tree-diagram.png jira_parse_out.gv

