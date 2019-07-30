#!/usr/bin/env python3

import logging
import argparse
import sys

import lib

def create_repo_version(repo,ver=None):
	"""creating repository version"""
	return lib.post(repo+'versions/',data={'base_version': ver})

def get_repository_version(task):
	"""getting the repo version from the task"""
	return lib.get(task)

repo1 = '/pulp/api/v3/repositories/fdf22817-cd92-4ed7-861b-26f40479c9cb/'
repo2 = '/pulp/api/v3/repositories/595f15e1-1b2c-46b4-9ff8-ff2508a496a1/'
repo_ver_a = create_repo_version(repo1)
task = repo_ver_a.get("task")
version_a = get_repository_version(task)
version_a = version_a.get("created_resources")

repo_ver_b = create_repo_version(repo2,version_a)
task = repo_ver_b.get("task")
version_b = get_repository_version(task)
version_b = version_b.get("created_resources")
print (version_b)
