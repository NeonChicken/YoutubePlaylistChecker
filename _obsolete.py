# These function are no longer in use since info such as titles and releaseDates are now stored during the api request directly

# # get video titles from list of IDS
# def get_titles(ins_list):
# 	titles = []
# 	nextToken = None
# 	# This loop is for when more than 50 videos have been removed/relisted since the last scan!
# 	while True:
# 		vid_request = youtube.videos().list(
# 			part='snippet',
# 			id=','.join(ins_list),
# 			maxResults=50,
# 			pageToken=nextToken
# 		)
# 		vid_response = vid_request.execute()

# 		for item in vid_response['items']:
# 			vid_title = item['snippet']['title']
# 			titles.append(vid_title)
# 		nextToken = vid_response.get('nextPageToken')
# 		if not nextToken:
# 			break
			
# 	return titles

# # get video title from single ID
# def get_title(ins):
# 	vid_request = youtube.videos().list(
# 		part='snippet',
# 		id=ins
# 	)
# 	vid_response = vid_request.execute()
# 	title = ''
# 	for item in vid_response['items']:
# 		vid_title = item['snippet']['title']
# 		title = vid_title
# 	return title