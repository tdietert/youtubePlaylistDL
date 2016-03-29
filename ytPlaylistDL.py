import urllib.request
import urllib.error

import re
import sys
import time
import os

from pytube import YouTube

class progressBar:
    def __init__(self, barlength=25):
        self.barlength = barlength
        self.position = 0
        self.longest = 0

    def print_progress(self, cur, total, start):
        currentper = cur / total
        elapsed = int(time.clock() - start) + 1
        curbar = int(currentper * self.barlength)
        bar = '\r[' + '='.join(['' for _ in range(curbar)])  # Draws Progress
        bar += '>'
        bar += ' '.join(['' for _ in range(int(self.barlength - curbar))]) + '] '  # Pads remaining space
        bar += bytestostr(cur / elapsed) + '/s '  # Calculates Rate
        bar += getHumanTime((total - cur) * (elapsed / cur)) + ' left'  # Calculates Remaining time
        if len(bar) > self.longest:  # Keeps track of space to over write
            self.longest = len(bar)
            bar += ' '.join(['' for _ in range(self.longest - len(bar))])
        sys.stdout.write(bar)

    def print_end(self, *args):  # Clears Progress Bar
        sys.stdout.write('\r{0}\r'.format((' ' for _ in range(self.longest))))

def getHumanTime(sec):
    if sec >= 3600:  # Converts to Hours
        return '{0:d} hour(s)'.format(int(sec / 3600))
    elif sec >= 60:  # Converts to Minutes
        return '{0:d} minute(s)'.format(int(sec / 60))
    else:            # No Conversion
        return '{0:d} second(s)'.format(int(sec))

def bytestostr(bts):
    bts = float(bts)
    if bts >= 1024 ** 4:    # Converts to Terabytes
        terabytes = bts / 1024 ** 4
        size = '%.2fTb' % terabytes
    elif bts >= 1024 ** 3:  # Converts to Gigabytes
        gigabytes = bts / 1024 ** 3
        size = '%.2fGb' % gigabytes
    elif bts >= 1024 ** 2:  # Converts to Megabytes
        megabytes = bts / 1024 ** 2
        size = '%.2fMb' % megabytes
    elif bts >= 1024:       # Converts to Kilobytes
        kilobytes = bts / 1024
        size = '%.2fKb' % kilobytes
    else:                   # No Conversion
        size = '%.2fb' % bts
    return size

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
        print("Error:", str(e), "- Skipping Video with url '"+vid_url+"'.")
        return

    try:  # Tries to find the video in 720p
        video = yt.get('mp4', '720p')
    except Exception:  # Sorts videos by resolution and picks the highest quality video if a 720p video doesn't exist
        video = sorted(yt.filter("mp4"), key=lambda video: int(video.resolution[:-1]), reverse=True)[0]

    print("downloading", yt.filename+"...")
    try:
        bar = progressBar()
        video.download(path, on_progress=bar.print_progress, on_finish=bar.print_end)
        print("successfully downloaded", yt.filename, "!")
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
