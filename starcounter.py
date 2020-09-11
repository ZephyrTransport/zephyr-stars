import urllib.request
import os
import json
import pandas
import yaml
from collections import Counter

CACHE_DIR = 'cache_stars_json'

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
	for username in known_users:
		local_f = os.path.join(CACHE_DIR, f'stars.{username}.json')
		if os.path.exists(local_f):
			with open(local_f, 'rb') as f:
				userstars = json.load(f)
			for s in userstars:
				stars[s.get('full_name')] += 1
	zephyr_stars = pandas.Series(stars)
	zephyr_stars = zephyr_stars[zephyr_stars >= threshold].sort_values(ascending=False)
	return zephyr_stars

def write_markdown(stars, filename="README.md"):
	with open(filename, 'wt') as f:
		print(README, file=f)
		for name, n in stars.items():
			print(f"- [{name}](https://www.github.com/{name}) ({n} stars)", file=f)

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

if __name__ == '__main__':
	known_users = load_known_users()
	cache_known_users(known_users)
	stars = count_stars(known_users)
	write_markdown(stars)