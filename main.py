# https://www.youtube.com/watch?v=coZbOM6E47I&t=1288s
# 
# https://google-api-client-libraries.appspot.com/documentation/youtube/v3/python/latest/index.html
# TODO auto-rescan after 15 mins a new video is added to the playlist, and send an e-mail
# https://developers.google.com/youtube/v3/docs/videos/list

import os
import json
from googleapiclient.discovery import build
import datetime

max_backups = 5

today = datetime.datetime.now()

# add your YouTube dev api key here
# instead of os.environ[] <-- this is for Replit
api_key = os.environ['api_key']

youtube = build('youtube', 'v3', developerKey=api_key)

nextPageToken = None
vid_id_titles = []
removed_ids = []
print("Requesting YouTube playlist data...")
while True:
	pl_request = youtube.playlistItems().list(
		part='contentDetails, snippet, status',
		#playlistId='PLHHR3ttLRhvnph5Z1WCdyrCv1BDu9okR0',
		playlistId='PLHHR3ttLRhvlpgSWJvBILXscHZv2KoZj6',
		maxResults=50,
		pageToken=nextPageToken
	)
	pl_response = pl_request.execute()

	for item in pl_response['items']:
		vid_id_titles.append(
				[
				item['contentDetails']['videoId'],
				item['snippet']['title'],
				item['status']['privacyStatus']
				]
			)
	nextPageToken = pl_response.get('nextPageToken')
	if not nextPageToken:
		break
print("YouTube playlist data stored!\n")

with open('newScan.json', 'w') as f:
	json.dump(vid_id_titles, f, indent=4)

old_list = []
new_list = []
with open('oldScan.json', 'r') as old:
	with open('newScan.json', 'r') as new:
		old_list.append(json.load(old))
		new_list.append(json.load(new))
# Removing double brackets because JSON.
old_list = old_list[0]
new_list = new_list[0]


print("Backing up old scans...")
# Backup old scan
totalFiles = 0
for base, dirs, files in os.walk('Backup Scans'):
	for Files in files:
		totalFiles += 1
if totalFiles < max_backups:
	with open('Backup Scans/{}.json'.format(today), 'w') as f:
		json.dump(new_list, f, indent=4)
elif totalFiles >= max_backups:
	for base, dirs, files in os.walk('Backup Scans'):
		os.remove('Backup Scans/{}'.format(files[0]))
	with open('Backup Scans/{}.json'.format(today), 'w') as f:
		json.dump(new_list, f, indent=4)

print("Backup complete!\n")

missing = []
relisted = []

print("Checking for missing videos...")
# Get the last list from oldScan and match titles
with open('oldScan.json') as oldScan:
	with open('newScan.json') as newScan:
		oldScan = json.load(oldScan)
		newScan = json.load(newScan)

		# titid = title & ID
		for old_titid in oldScan:
			for new_titid in newScan:
				# matching ID
				if old_titid[0] == new_titid[0]:		
					# titid[2] gets the privacyStatus
					if old_titid[2] == new_titid[2]:
						# video is still public/unlisted/privated/deleted from last scan
						pass
					elif old_titid[2] != new_titid[2]:
						# if old video was private/unlisted
						if old_titid[2] == 'private' or old_titid[2] == 'unlisted':
							if new_titid[2] == 'private':
								# video was changed from unlisted to private
								# but still not available
								pass
							elif new_titid[2] == 'unlisted':
								# video was changed from private to unlisted
								# but still not available
								pass
							elif new_titid[2] == 'public':
								# video has been unprivated/relisted
								relisted.append(new_titid)
							elif new_titid[2] == 'privacyStatusUnspecified':
								# video has been deleted from an unlisted/privated status
								print("Rare case: \n{} <--- video was deleted from an unlisted/privated status. You likely won't notice any consequence".format(old_titid))
						# if new video is private/unlisted/deleted, check old video difference
						if new_titid[2] == 'private' or new_titid[2] == 'unlisted' or new_titid[2] == 'privacyStatusUnspecified':
							if old_titid[2] == 'public':
								# video has been privated/unlisted/deleted:
								missing.append(old_titid)

tuple1 = tuple(tuple(sub) for sub in old_list)
tuple2 = tuple(tuple(sub) for sub in new_list)

set1 = set(tuple1)
set2 = set(tuple2)

removed = list(sorted(set1 - set2))
removed_dupe = removed.copy()
added = list(sorted(set2 - set1))
added_dupe = added.copy()

# Missing != added, but would count as added because of the different title
# E.g. 	  ('zbGByNBfFyQ', 'Test', 'public') 
# Becomes ('zbGByNBfFyQ', 'Deleted video', 'UnspecifiedStatus')
indices = []
for idx, add in enumerate(added):
	for miss in missing:
		if add[0] == miss[0]:
			indices.append(idx)
for i in sorted(indices, reverse=True):
	del added_dupe[i]
added = added_dupe

# Missing != removed, but still counts old_list/new_list discrepancies
# Seperating this to differentiate deleted/unlisted videos from videos removed from the playlist itself
# E.g. 	  ('zbGByNBfFyQ', 'Thicc', 'public') 
# Becomes ('zbGByNBfFyQ', 'Deleted video', '('zbGByNBfFyQ', 'Thicc', 'public')')
indices = []
for idx, remove in enumerate(removed):
	for miss in missing:
		if remove[0] == miss[0]:
			indices.append(idx)
for i in sorted(indices, reverse=True):
	del removed_dupe[i]
removed = removed_dupe

print("\nScan complete!\n")
data_collected = []

if missing != []:
	is_missing = ["Missing videos: ", missing]
	data_collected.append(is_missing)
	final_msg = "\nMissing videos: "
	for obj in missing:
		final_msg += '\n{}'.format(obj)
	print(final_msg)
if relisted != []:
	is_relisted = ["Relisted videos: ", relisted]
	data_collected.append(is_relisted)
	final_msg = "\nRelisted videos: "
	for obj in relisted:
		final_msg += '\n{}'.format(obj)
	print(final_msg)
if removed != []:
	is_removed = ["Removed from playlist: ", removed]
	data_collected.append(is_removed)
	final_msg = "\nRemoved videos: "
	for obj in removed:
		final_msg += '\n{}'.format(obj)
	print(final_msg)
if added != []:
	is_added = ["Added to playlist: ", added]
	data_collected.append(is_added)
	final_msg = "\nAdded videos: "
	for obj in added:
		final_msg += '\n{}'.format(obj)
	print(final_msg)

if removed == [] and added == [] and missing == [] and relisted == []:
	print("This scan was identical to the last scan, meaning there were no changes to the playlist whatsoever!")
else:
	with open('Retrieved Data/{}.json'.format(today), 'w') as f:
		json.dump(data_collected, f, indent=4)

# rename scan to old, so the next run checks today's scan.
os.rename('newScan.json', 'oldScan.json')
# create new scan file for the next run to overwrite 
# (could also be an empty list)
with open('newScan.json', 'w') as f:
	json.dump(new_list, f, indent=4)

print("\nDone!")