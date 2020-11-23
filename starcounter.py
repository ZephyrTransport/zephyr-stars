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
	zephyr_stars = pandas.Series(stars, name='starcount')
	zephyr_stars = zephyr_stars[zephyr_stars >= threshold]
	zephyr_stars = zephyr_stars.reset_index(drop=False) # for list order stability
	zephyr_stars['projectname'] = zephyr_stars['index'].str.lower()
	zephyr_stars = zephyr_stars.sort_values(['starcount','projectname'], ascending=(False,True))
	zephyr_stars = zephyr_stars.set_index('index').loc[:,'starcount']
	return zephyr_stars, descriptions

def write_markdown(known_users, stars, descriptions, filename="STARS.md"):
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
		print(CONTRIBUTING, file=f)
		print(time.strftime("\n\nLast updated %B %d, %Y"), file=f)

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

CONTRIBUTING = """

## Contributing

Zephyr members are invited to contribute in two ways:

1. If you’re already included on our list, go out and put GitHub stars on projects you 
   use or like.  
2. You can propose additions to the list of known users, either by 
   adding yourself, or by adding respected colleagues working in our industry.  You can do 
   so by making a 
   [pull request](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request)
   on the [known-users.yml](https://github.com/ZephyrTransport/zephyr-stars/blob/master/known-users.yml) file in the
   [Zephyr Stars repository](https://github.com/ZephyrTransport/zephyr-stars).
   If you’re not familiar with Git, this is your opportunity 
   to learn a bit how to use it.  For a simple repository update like this, you can do it 
   entirely on [GitHub.com](https://www.github.com) and you don’t even need to download or 
   install anything (although you’ll certainly want to eventually if you want to really 
   use Git).

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