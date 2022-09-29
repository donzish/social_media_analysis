#### PROJECT SMA ####

# Questo codice serve per scaricare e raccogliere in un unico dataset i commenti ed i relativi dati del canale youtube 'AsapSCIENCE'.
# La ricerca del canale youtube deve avvenire tramite l'ID; per ottenerlo è sufficiente inserire il link del canale youtube nella cella apposita presente nel seguente link:
# 'https://commentpicker.com/youtube-channel-id.php'.

import json
from csv import writer
from apiclient.discovery import build
import pandas as pd
import pickle
import urllib.request
import urllib

key1 = '***************************************' # youtube API
key2 = '***************************************'
key3 = '***************************************'
key = '*********************************'
videoId = '1iIENII-lVo' # lo stesso codice potrebbe essere eseguito concentrandosi sun un singolo video
channelId = 'UCLLw7jmFsvfIVaUFsLs8mlQ'

# 1) Definiamo i parametri fondamentali della nostra ricerca (per maggiori info consulta 'https://developers.google.com/youtube/v3/docs')
def build_service():
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    return build(YOUTUBE_API_SERVICE_NAME,
                 YOUTUBE_API_VERSION,
                 developerKey=key)

# 2) Nella seguente funzione configuriamo i parametri rimanenti per la ricerca
def get_comments(part='snippet',
                 maxResults=100,
                 textFormat='plainText',
                 order='time',
                 allThreadsRelatedToChannelId=channelId,
                 # videoId=videoId,
                 csv_filename="eng_comments"
                 ):

    # 3) creiamo liste vuote in cui verranno inserite le informazioni ottenute
    comments, commentsId, authorurls, authornames, repliesCount, likesCount, viewerRating, dates, vidIds, totalReplyCounts,vidTitles = [], [], [], [], [], [], [], [], [], [], []

    # costruiamo il nostro 'service'
    service = build_service()

    # 4) Chiamata trameti la API key di Youtube ed i parametri definiti in precedenza
    response = service.commentThreads().list(
        part=part,
        maxResults=maxResults,
        textFormat='plainText',
        order=order,
        # videoId=videoId
        allThreadsRelatedToChannelId=channelId
    ).execute()

    while response: # il ciclo continua ad essere eseguito finchè non raggiunge la quota massima fissata

        for item in response['items']:
            # 5) Definiamo tramite gli indici i dati e le variabili di interesse
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comment_id = item['snippet']['topLevelComment']['id']
            reply_count = item['snippet']['totalReplyCount']
            like_count = item['snippet']['topLevelComment']['snippet']['likeCount']
            authorurl = item['snippet']['topLevelComment']['snippet']['authorChannelUrl']
            authorname = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            date = item['snippet']['topLevelComment']['snippet']['publishedAt']
            vidId = item['snippet']['topLevelComment']['snippet']['videoId']
            totalReplyCount = item['snippet']['totalReplyCount']
            vidTitle = get_vid_title(vidId)

            # 6) Inseriamo i dati nelle liste definite al punto 3
            comments.append(comment)
            commentsId.append(comment_id)
            repliesCount.append(reply_count)
            likesCount.append(like_count)
            authorurls.append(authorurl)
            authornames.append(authorname)
            dates.append(date)
            vidIds.append(vidId)
            totalReplyCounts.append(totalReplyCount)
            vidTitles.append(vidTitle)

        try:
            if 'nextPageToken' in response:
                response = service.commentThreads().list(
                    part=part,
                    maxResults=maxResults,
                    textFormat=textFormat,
                    order=order,
                    # videoId=videoId,
                    allThreadsRelatedToChannelId=channelId,
                    pageToken=response['nextPageToken']
                ).execute()
            else:
                break
        except: break

    # 7) Vengono così restituiti i dati d'interesse
    return {
        'comment': comments,
        'comment_id': commentsId,
        'author_url': authorurls,
        'author_name': authornames,
        'reply_count' : repliesCount,
        'like_count' : likesCount,
        'date': dates,
        'vidid': vidIds,
        'total_reply_counts': totalReplyCounts,
        'vid_title': vidTitles
    }

# ...
def get_vid_title(vidid):
    # VideoID = "LAUa5RDUvO4"
    params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % vidid}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        # print(data['title'])
        return data['title']

if __name__ == '__main__':
    tinas_comments = get_comments()
    df = pd.DataFrame(tinas_comments)
    print(df.shape)
    print(df.head())
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['just_date'] = df['date'].dt.date
    df.to_csv('./eng_comments.csv')
