# fauxble-py
A program to automatically alternate between playing videos from folders in a main folder and videos in an intermediary folder

# To Install:
There are a couple options, but I would personally recommend using git for installation as this will allow for easy updating.

- git (you must have git installed to use this method; i also recommend some knowledge with git to begin with)
1. Run `git clone https://github.com/tekmyndaspy/fauxble-py-gui` in the directory you want the fauxble-py-gui folder to be in.

- Manual Installation (`update.bat` will not work if this method is used)
1. Click the green 'Code' button near the top of the repository.
2. Click 'Download ZIP'.
3. Extract the `fauxble-py-gui-main` folder to the folder of your choice.


# To Use:
1. Place main video files in a folder named `Main` or subfolders of the previously mentioned `Main` folder
2. Place intermediary video files in a folder named `Intermediary` or subfolders of the previously mentioned `Intermediary` folder
4. Run fauxble.pyw

# Optional Actions:
- You can create a file fauxble_settings.py which may contain variables and values to be used by fauxble.pyw
  - You should be careful to only use variables spcified in the "fauxble user-definable settings" section in fauxble.pyw, and only in a similar format
  - The benefit of using the fauxble_settings.py file as opposed to changing the settings in the main file is that they will not be wiped out upon updating fauxble

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
|- fauxble.pyw
|- fauxble_settings.py  
|- README.md
```

# To Close:
1. Close the GUI window that opens upon launching the fauxble.pyw script

# Things to Know:
- two files will be created, videos.log and fauxble.log
  - fauxble.log records general actions performed by the program
  - videos.log records the videos played by fauxble

# Functionality Planned for the Future:
- possibly integrate mpv into the gui itself (may make application less portable, though an installation of mpv is already required)
- include ways to change behavior on launch, such as with launch arguments (such as previous behavior where a gui is not required)
  - in this case, add way to add videos to queue through script (is this even possible?)
- add check for certain prefix of videos to stop them from playing

# To Do List:
"The way to shorten the time between videos would probably just be to run the logic for deciding the next filepath when a file starts playing instead of when a file finishes, that way the program simply has to wait for the current file to end and then it can instantly open the next one instead of running the logic to decide what to play next at that exact moment."