#!/usr/bin/env python3

import sys
import lib

def create_repo_version(repo,ver=None):
	"""creating repository version"""
	return lib.post(repo+'versions/',data={'base_version': ver})

def get_repository_version(task):
	"""getting the repo version from the task"""
	return lib.get(task)

def create_repo(name):
	"""Create repository"""
	return lib.post('/pulp/api/v3/repositories/',data={'name': name})

repo1 = create_repo(lib.get_random_string())
repo1 = repo1.get("_href")
repo2 = create_repo(lib.get_random_string())
repo2 = repo2.get("_href")

repo_ver_a = create_repo_version(repo1)
task = repo_ver_a.get("task")
version_a = get_repository_version(task)
version_a = version_a.get("created_resources")

repo_ver_b = create_repo_version(repo2,version_a)
task = repo_ver_b.get("task")
version_b = get_repository_version(task)
version_b = version_b.get("created_resources")
print (version_b)
