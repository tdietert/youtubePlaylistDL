# youtubePlaylistDL
A simple script to download all videos in a youtube playlist (720p quality)

### Requirements:


#####**This script needs Python 3.4.1+**

```bash
$ pip3 install pytube
```

### Usage:

```bash
$ python ytPlaylistDL.py <playlistURL>
```
```bash
$ python ytPlaylistDL.py <playlistURL> <destinationPath>
```

### Example:
---
Say I'd like to download all videos in the playlist "FOMH 2015" (a music channel I like on youtube), found at URL 
https://www.youtube.com/playlist?list=PLVJcUspOFG-Np-YotXlPviRUK_MKyvwId, and put them in a music folder named
~/Music/FOMH. This is how I would do that:

```bash
$ python ytPlaylistDL.py https://www.youtube.com/playlist?list=PLVJcUspOFG-Np-YotXlPviRUK_MKyvwId ~/Music/FOMH
```
