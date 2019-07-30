#!/usr/bin/env python3

import sys
import lib

def list_units():
    """List the file content with all the fields""" 
    return lib.get('/pulp/api/v3/content/file/files/')

def inspect_content(href):
    """Inspect a file content using href"""
    return lib.get(href)


list = list_units()
print("-------List the content--------:", (list))

#url = (list.get("results"))[0].get("_href")

for i in list.get("results"):
    url = i.get("_href")
    content = inspect_content(url)
    print("---------Inspect the file content-------------:", (content))

