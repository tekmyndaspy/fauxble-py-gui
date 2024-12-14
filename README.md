# fauxble-py
A program to automatically alternate between playing videos from folders in a main folder and videos in an intermediary folder.

# To Use:
1. Place main video files in a folder named 'Main' or subfolders of the previously mentioned 'Main' folder.
2. Place intermediary video files in a folder named 'Intermediary' or subfolders of the previously mentioned 'Intermediary' folder.
4. Run fauxble.pyw.

# Example Directory Tree:

```
Fauxble Root  
|- Main  
|  |- main1  
|  |  |- main1v1.mp4  
|  |  |- main1v2.mp4  
|  |- main2  
|  |  |- main2v1.mp4  
|  |  |- main2v2.mp4  
|  |- main3  
|     |- main3v1.mp4  
|     |- main3v2.mp4  
|- Intermediary  
|  |- intermediary1.mp4  
|  |- intermediary2.mp4  
|  |- intermediary3.mp4  
|- fauxble.cmd  
|- README.md
```

# To Close:
1. Close the GUI window that opens upon launching the fauxble.pyw script.

# Functionality Planned for the Future:
- possibly integrate mpv into the gui itself (may make application less portable, though an installation of mpv is already required)
- include ways to change behavior on launch, such as with launch arguments (such as previous behavior where a gui is not required)
  - in this case, add way to add videos to queue through script (is this even possible?)
- add check for certain prefix of videos to stop them from playing

# Other Notes:
fauxble.pyw is commented quite a bit. near the top of the file are variables to allow one to set the video player to be used and the file types that are accepted.  
by default, fauxble uses mpv and accepts mp4, webm, and mkv files.  
