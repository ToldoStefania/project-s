import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd
import openpyxl
import re
import streamlit as st
from sentimental import analyse_comments



api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyCfzhKWLzLRGUjessouWIhURmHF0_WJFwE"

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)


def button_click(linkId):
    print('Checking video fuck')
    extracted_id = extract_youtube_video_id_regex(linkId)
    call_youtube_api(extracted_id)



#linkId = input('Enter the link of the youtube video:')

def extract_youtube_video_id_regex(url):
    result = re.match(r"^[^v]+v=(.{11}).*", url)
    if result:
        return result.group(1)
    return None

#extracted_id = extract_youtube_video_id_regex(linkId)

def call_youtube_api(extracted_id):
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=extracted_id,
        maxResults=100,
    )

    response = request.execute()

    comments = []

    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        public = item['snippet']['isPublic']
        comments.append([
            comment['authorDisplayName'],
            comment['publishedAt'],
            comment['likeCount'],
            comment['textOriginal'],
        ])

    while (True):
        try:
            nextPageToken = response['nextPageToken']
        except KeyError:
            break
        nextPageToken = response['nextPageToken']
        # Create a new request object with the next page token.
        nextRequest = youtube.commentThreads().list(part="snippet", videoId=extracted_id, maxResults=100, pageToken=nextPageToken)
        # Execute the next request.
        response = nextRequest.execute()
        # Get the comments from the next response.
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            #public = item['snippet']['isPublic']
            comments.append([
                comment['authorDisplayName'],
                comment['publishedAt'],
                comment['likeCount'],
                comment['textOriginal'],
            ])

    df = pd.DataFrame(comments, columns=['author', 'updated_at', 'like_count', 'text'])
    df.to_excel('comments.xlsx', index=False)
    st.subheader("Youtube comments")
    st.write(df)
    df_reader = pd.read_excel('comments.xlsx', usecols=['like_count', 'text'])

    analyse_comments(df_reader)
    print(df)

st.title("Decoding viewers' appreciation")
linkId = st.text_input("Insert the youtube link")
if st.button("Check video"):
    button_click(linkId)