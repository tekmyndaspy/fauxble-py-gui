'''
an application to alternate between playing random video files from a main folder and its subfolder,
and an intermediary folder and its subfolders
'''

import os
import sys
import random
import subprocess
import tkinter
import threading
import tkinter.filedialog

# fauxble default settings
# it is recommended to use a separate fauxble_settings.py file within the same 
# directory as this file if you wish to change these settings
# these settings will be set back to the defaults upon updating, as this file will be overwritten
ALLOWED_EXTENSIONS = ['.mp4', '.webm', '.mkv']
VIDEO_PLAYER = 'mpv'
VIDEO_PLAYER_FLAGS = ['--no-config', '--terminal=no', '--fullscreen', '--af=loudnorm']
VIDEO_DIRECTORY_CYCLE = ['Main', 'Intermediary']
VIDEOS_UNTIL_REPLAY = 48

# overwrite defaults with user defined settings, if applicable
try:
    from fauxble_settings import *
    print('fauxble_settings.py found. overwriting defaults with settings in file.')
except ModuleNotFoundError:
    pass

# script constants
SCRIPT_ROOT = sys.path[0]

# globals for communication between threads
VIDEO_PLAYER_THREAD = None
FAUXBLE_ACTIVE = False
QUEUE = []
QUEUE_TEXT = ""
VIDEO_DIRECTORY_CYCLE_TEXT = ""

def get_random_file(directory, allowed_extensions=[], disallowed_files=[]):
    '''
    returns a random file from the specified directory that satisfies the 
    specified allowed extensions.

    accepts a string referring to a directory the fauxble root, such as 'Main',
    a list of allowed extensions, such as ['.mp4', '.webm', '.mkv'],
    a list of disallowed files, such as ['one.mp4','two.mp4','three.mp4']
    '''
    
    video_directory = os.path.join(SCRIPT_ROOT, directory)
    os.chdir(video_directory)

    # loop through directory
    file_is_chosen = False
    while not file_is_chosen:
        files_in_directory = os.listdir()
        # if the working directory has no items, return to the video directory and restart the loop, 
        # otherwise carry on
        if not files_in_directory:
            os.chdir(video_directory)
            continue
        
        # select random item in working directory for review
        potential_item = random.choice(files_in_directory)
        
        # if the item is a directory, enter the directory and restart the loop, 
        # otherwise carry on
        if os.path.isdir(potential_item):
            os.chdir(potential_item)
            continue
        
        # the item is a file if it is not a directory

        # if the file is in disallowed_files, return to the video directory and restart the loop,
        # otherwise carry on
        if os.path.abspath(potential_item) in disallowed_files:
            os.chdir(video_directory)
            continue
        # if the file is not in allowed_extensions, return to the video directory and restart the loop, 
        # otherwise carry on
        if os.path.splitext(potential_item)[-1].lower() not in allowed_extensions:
            os.chdir(video_directory)
            continue
        # if no previous checks fail, return the file
        return potential_item

def main_loop():
    '''loop that governs how videos are chosen and played'''
    global FAUXBLE_ACTIVE, VIDEO_PLAYER_THREAD
    # set initial values and begin constantly running loop
    current_video_directory = 0
    recently_played_videos = []
    FAUXBLE_ACTIVE = True
    while FAUXBLE_ACTIVE:
        # if the video directory index is outside the list range, set it to the beginnning
        if current_video_directory > len(VIDEO_DIRECTORY_CYCLE) - 1:
            current_video_directory = 0
        
        # if there is a video on the video queue, choose the first video on the queue then remove that video from the queue, 
        # otherwise choose a random video from the current video directory
        if VIDEO_DIRECTORY_CYCLE[current_video_directory] == VIDEO_DIRECTORY_CYCLE[0] and QUEUE:
            chosen_video = QUEUE[0]
            QUEUE.pop(0)
            update_queue_text()
        else:
            chosen_video = get_random_file(VIDEO_DIRECTORY_CYCLE[current_video_directory], ALLOWED_EXTENSIONS, recently_played_videos)

        # play the chosen video, waiting until the process ends to continue
        VIDEO_PLAYER_THREAD = subprocess.Popen([VIDEO_PLAYER] + VIDEO_PLAYER_FLAGS + [chosen_video], creationflags=subprocess.CREATE_NO_WINDOW)
        VIDEO_PLAYER_THREAD.wait()
        
        # if the video directory is the same as the first in the video directory, 
        # add the last played video to the recently played videos
        if VIDEO_DIRECTORY_CYCLE[current_video_directory] == VIDEO_DIRECTORY_CYCLE[0]:
            recently_played_videos.append(os.path.abspath(chosen_video))
        
        # add one to the video directory index
        current_video_directory += 1

        # if the number of videos is greater than acceptable in the recently played videos list
        # remove enough videos from the list until it is within an acceptable range
        if len(recently_played_videos) > VIDEOS_UNTIL_REPLAY - 1:
            del recently_played_videos[0:len(recently_played_videos) - VIDEOS_UNTIL_REPLAY]

def terminate_main_loop():
    '''kill the thread and kill any mpv windows left over'''
    global FAUXBLE_ACTIVE
    FAUXBLE_ACTIVE = False
    # kill the thread
    subprocess.run(['TASKKILL', '/PID', str(VIDEO_PLAYER_THREAD.pid), '/T', '/F'], creationflags=subprocess.CREATE_NO_WINDOW)

def update_queue_text():
    QUEUE_TEXT.config(text='\n'.join(QUEUE))

def update_video_directory_cycle_text():
    VIDEO_DIRECTORY_CYCLE_TEXT.config(text=str(VIDEO_DIRECTORY_CYCLE))

def create_control_panel():
    '''create the window to control fauxble'''
    # root of control window
    root = tkinter.Tk()
    root.title("Fauxble Control Panel")
    
    # frame containing general fauxble functions, like starting and stopping
    general_frame = tkinter.Frame(root)
    general_frame.grid(column=0, row=0)
    # start and stop buttons, each kill themself and then invoke the other upon clicking them
    start_button = tkinter.Button(general_frame, text="Start Fauxble", command=lambda:[start_button.grid_forget(), threading.Thread(target=main_loop).start(), stop_button.grid(column=0, row=0)])
    start_button.grid(column=0, row=0)
    stop_button = tkinter.Button(general_frame, text="Stop Fauxble", command=lambda:[stop_button.grid_forget(), terminate_main_loop(), start_button.grid(column=0, row=0)])
    
    # frame containing secondary functions, like adding videos to the queue
    secondary_frame = tkinter.Frame(root)
    secondary_frame.grid(column=1, row=0)
    # queue functionality
    add_to_queue_button = tkinter.Button(secondary_frame, text="Add to Queue", command=lambda:[QUEUE.extend(list(tkinter.filedialog.askopenfilenames(parent=root,initialdir=SCRIPT_ROOT))), update_queue_text()])
    add_to_queue_button.grid(column=0, row=0)
    clear_queue_button = tkinter.Button(secondary_frame, text="Clear Queue", command=lambda:[QUEUE.clear(), update_queue_text()])
    clear_queue_button.grid(column=0, row=1)
    # video directory cycle functionality
    video_directory_cycle_button = tkinter.Button(secondary_frame, text = "Change Video Directory Cycle", command=lambda:[VIDEO_DIRECTORY_CYCLE.clear(), VIDEO_DIRECTORY_CYCLE.extend(tkinter.simpledialog.askstring(title="Change Video Directory Cycle",prompt="What do you want the new video directory cycle to be? Separate each entry with a \'>\'.").split('>')),update_video_directory_cycle_text()])
    video_directory_cycle_button.grid(column=0, row=2)

    # frame containing information about certain variables
    information_frame = tkinter.Frame(root)
    information_frame.grid(column=2, row=0)
    # queue information
    queue_label = tkinter.Label(information_frame, text="Current Queue")
    queue_label.grid(column=0, row=0)
    global QUEUE_TEXT
    QUEUE_TEXT = tkinter.Label(information_frame)
    update_queue_text()
    QUEUE_TEXT.grid(column=0, row=1)
    # video directory cycle information
    video_directory_cycle_label = tkinter.Label(information_frame, text="Video Directory Cycle")
    video_directory_cycle_label.grid(column=0, row=2)
    global VIDEO_DIRECTORY_CYCLE_TEXT
    VIDEO_DIRECTORY_CYCLE_TEXT = tkinter.Label(information_frame)
    update_video_directory_cycle_text()
    VIDEO_DIRECTORY_CYCLE_TEXT.grid(column=0, row=3)

    root.mainloop()

if __name__ == '__main__':
    # create the fauxble control panel
    create_control_panel()
    # terminate any left over video players if the window was closed without stopping fauxble first
    terminate_main_loop()