import urllib.request
import urllib.error

import re
import sys
import time
import os

from pytube import YouTube

def getPageHtml(url):
    try:
        yTUBE = urllib.request.urlopen(url).read()
        return str(yTUBE)
    except urllib.error.URLError as e:
        print(e.reason)
        exit(1)

def getPlaylistUrlID(url):
    if 'list=' in url:
        eq_idx = url.index('=') + 1
        pl_id = url[eq_idx:]
        if '&' in url:
            amp = url.index('&')
            pl_id = url[eq_idx:amp]
        return pl_id   
    else:
        print(url, "is not a youtube playlist.")
        exit(1)

def getFinalVideoUrl(vid_urls):
    final_urls = []
    for vid_url in vid_urls:
        url_amp = len(vid_url)
        if '&' in vid_url:
            url_amp = vid_url.index('&')
        final_urls.append('http://www.youtube.com/' + vid_url[:url_amp])
    return final_urls

def getPlaylistVideoUrls(page_content, url):
    playlist_id = getPlaylistUrlID(url)

    vid_url_pat = re.compile(r'watch\?v=\S+?list=' + playlist_id)
    vid_url_matches = list(set(re.findall(vid_url_pat, page_content)))

    if vid_url_matches:
        final_vid_urls = getFinalVideoUrl(vid_url_matches)
        print("Found",len(final_vid_urls),"videos in playlist.")
        printUrls(final_vid_urls)
        return final_vid_urls
    else:
        print('No videos found.')
        exit(1)

def downloadVideo(path, vid_url):
    try:
        yt = YouTube(vid_url)
    except Exception as e:
        print("Error:", e.reason, "- Skipping Video with url '"+vid_url+"'.")
        return

    try:  # Tries to find the video in 720p
        video = yt.get('mp4', '720p')
    except Exception:  # Sorts videos by resolution and picks the highest quality video if a 720p video doesn't exist
        video = sorted(yt.filter("mp4"), key=lambda video: int(video.resolution[:-1]), reverse=True)[0]

    print("downloading",yt.filename+"...")
    try:
        video.download(path)
        print("successfully downloaded", yt.filename,"!")
    except OSError:
        print(yt.filename, "already exists in this directory! Skipping video...")
 
def printUrls(vid_urls):
    for url in vid_urls:
        print(url)
        time.sleep(0.04)
        
if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print('USAGE: python ytPlaylistDL.py playlistURL OR python ytPlaylistDL.py playlistURL destPath')
        exit(1)
    else:
        url = sys.argv[1]
        directory = os.getcwd() if len(sys.argv) != 3 else sys.argv[2]
    
        # make directory if dir specified doesn't exist
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            print(e.reason)
            exit(1)

        if not url.startswith("http"):
            url = 'https://' + url

        playlist_page_content = getPageHtml(url)
        vid_urls_in_playlist = getPlaylistVideoUrls(playlist_page_content, url)

        # downloads videos
        for vid_url in vid_urls_in_playlist:
            downloadVideo(directory, vid_url)
            time.sleep(1)
