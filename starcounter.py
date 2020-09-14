import urllib.request
import os
import json
import pandas
import yaml
import time
from collections import Counter

CACHE_DIR = 'cache_stars_json'

os.makedirs(CACHE_DIR, exist_ok=True)

def load_known_users(filename="known-users.yml"):
	with open(filename, 'rt') as f:
		known_users = yaml.safe_load(f)
	return known_users

def cache_known_users(known_users):
	for username in known_users:
		local_f = os.path.join(CACHE_DIR, f'stars.{username}.json')
		url = f'https://api.github.com/users/{username}/starred'
		if not os.path.exists(local_f):
			with urllib.request.urlopen(url) as response:
				html = response.read()
				with open(local_f, 'wb') as f:
					f.write(html)

def count_stars(known_users, threshold=2):
	stars = Counter()
	descriptions = {}
	for username in known_users:
		local_f = os.path.join(CACHE_DIR, f'stars.{username}.json')
		if os.path.exists(local_f):
			with open(local_f, 'rb') as f:
				userstars = json.load(f)
			for s in userstars:
				stars[s.get('full_name')] += 1
				descriptions[s.get('full_name')] = s.get('description')
	zephyr_stars = pandas.Series(stars)
	zephyr_stars = zephyr_stars.sort_index() # for list order stability
	zephyr_stars = zephyr_stars[zephyr_stars >= threshold].sort_values(ascending=False)
	return zephyr_stars, descriptions

def write_markdown(known_users, stars, descriptions, filename="README.md"):
	with open(filename, 'wt') as f:
		print(README, file=f)
		print("## Zephyr Starred Projects", file=f)
		for name, n in stars.items():
			print(f"- [{name}](https://www.github.com/{name}) ({n} stars)  ", file=f)
			desc = descriptions.get(name)
			if desc:
				print(f"  {desc}", file=f)
		print("\n\n## Zephyr Users", file=f)
		print("\nThe list of starred projects is based on these GitHub users.\n", file=f)
		for username, realname in known_users.items():
			print(f"- [{realname} ({username})](https://www.github.com/{username})", file=f)
		print(time.strftime("\n\nLast updated %B %d, %Y"), file=f)
		print(HOWTO, file=f)

README = """\
# Zephyr Stars

These projects have been "starred" multiple times by the 
members of the [Zephyr Foundation](https://zephyrtransport.org).
Stars mean different things to different people, from "this is a 
useful tool for work" to "I want to be able to find this again" 
to "my buddy made a fundraising website".  But it is expected 
that GitHub projects high on this list (i.e. starred by a large 
number of analytic transportation professionals) will tend to be 
in the first category.  
"""

HOWTO = """

	This document is auto-generated, do not edit it directly.  Instead,
	edit the list of users in `known-users.yml`, and then run the 
	`starcounter.py` Python script.
"""

if __name__ == '__main__':
	known_users = load_known_users()
	cache_known_users(known_users)
	stars, descriptions = count_stars(known_users)
	write_markdown(known_users, stars, descriptions)