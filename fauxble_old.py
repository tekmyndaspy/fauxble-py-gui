# an application to alternate between playing random videos from a main folder and its subfolders and an intermediary folder and its subfolders

import threading # for allowing fauxble mainloop to run alongside gui to control the mainloop
import tkinter # for creating guis
import tkinter.filedialog # for adding files to the queue
import subprocess # for running applications with a great deal of control
import random # for pseudorandomly choosing things
import os
import sys

# user definable variables follow

# defines the extensions allowed to be played
ALLOWED_EXTENSIONS = ['.mp4', '.webm', '.mkv']
# defines the command for the videplayer to be used
VIDEOPLAYER = ['mpv']
# defines the flags used with the videoplayer
VIDEOPLAYER_FLAGS = ['--no-config', '--terminal=no', '--fullscreen', '--af=loudnorm']

# constants used by the script. best not to touch these
SCRIPT_ROOT = os.path.dirname(os.path.realpath(sys.argv[0]))

#print("Starting Fauxble.")
RANDOM_MESSAGES = ["\"smoking pot and programming camp, i don\'t give a shit\" - casket",
                  "\"fuck batch. me and my homies all hate batch\" - tekmyndaspy"]
print(random.choice(RANDOM_MESSAGES))
VIDEOS_UNTIL_REPLAY = 12

# globals used to communicate between different threads of the script
FAUXBLE_ACTIVE = False
VIDEOPLAYER_THREAD = None
VIDEO_QUEUE = []
QUEUE_TEXT = None
def update_queue_text():
    '''update queue text label in gui'''
    QUEUE_TEXT.config(text='\n'.join(VIDEO_QUEUE))
VIDEO_DIRECTORY_CYCLE = ['Main', 'Intermediary']
VIDEO_DIRECTORY_CYCLE_TEXT = None
def update_video_directory_cycle_text():
    '''update video directory cycle text in gui'''
    VIDEO_DIRECTORY_CYCLE_TEXT.config(text=str(VIDEO_DIRECTORY_CYCLE))

def main_loop():
    '''loop that governs the playing of videos'''
    global FAUXBLE_ACTIVE, VIDEOPLAYER_THREAD
    FAUXBLE_ACTIVE = True
    current_video_directory = 0
    recently_played_videos = []
    while FAUXBLE_ACTIVE:
        # choose video directory
        if current_video_directory > len(VIDEO_DIRECTORY_CYCLE) - 1:
            current_video_directory = 0
        file_chosen = False
        chosen_video = None
        # Choose Video
        # if the current video directory is the same as the first in the list (presumed main) and the video queue is not empty, set chosen video to first in queue and set file chosen to true
        if VIDEO_DIRECTORY_CYCLE[current_video_directory] == VIDEO_DIRECTORY_CYCLE[0] and VIDEO_QUEUE:
            chosen_video = VIDEO_QUEUE[0]
            VIDEO_QUEUE.pop(0)
            update_queue_text()
            file_chosen = True
        # if a video has not already been chosen, go to the current video directory
        if not file_chosen:
            os.chdir(SCRIPT_ROOT)
            os.chdir(VIDEO_DIRECTORY_CYCLE[current_video_directory])
        # loop through directory and subdirectories until a video is chosen
        while not file_chosen and chosen_video is None:
            files_in_directory = os.listdir()
            # if the working directory has no items, return to the current video directory and restart loop
            if not files_in_directory:
                os.chdir(SCRIPT_ROOT)
                os.chdir(VIDEO_DIRECTORY_CYCLE[current_video_directory])
                continue
            # select random item in working directory for review
            potential_item = random.choice(files_in_directory)
            # if the item is a directory, enter the directory and restart the loop
            if os.path.isdir(potential_item):
                os.chdir(potential_item)
                continue
            # if the item is a file, do further checking
            if os.path.isfile(potential_item):
                # if the file's extension is not in ALLOWED_EXTENSIONS, return to the current video directory and restart loop
                if os.path.splitext(potential_item)[-1].lower() not in ALLOWED_EXTENSIONS:
                    os.chdir(SCRIPT_ROOT)
                    os.chdir(VIDEO_DIRECTORY_CYCLE[current_video_directory])
                    continue
                # if the file is in the recently played video list, return to the current video directory and restart loop
                if os.path.abspath(potential_item) in recently_played_videos:
                    os.chdir(SCRIPT_ROOT)
                    os.chdir(VIDEO_DIRECTORY_CYCLE[current_video_directory])
                    continue
                # if no previous checks fail, choose the file for playback
                chosen_video = potential_item
                file_chosen = False
        # play the chosen file
        VIDEOPLAYER_THREAD = subprocess.Popen(VIDEOPLAYER + VIDEOPLAYER_FLAGS + [str(chosen_video)], creationflags=subprocess.CREATE_NO_WINDOW)
        VIDEOPLAYER_THREAD.wait()
        if len(recently_played_videos) > 11:
            del recently_played_videos [0:len(recently_played_videos) - VIDEOS_UNTIL_REPLAY]
        if VIDEO_DIRECTORY_CYCLE[current_video_directory] == VIDEO_DIRECTORY_CYCLE[0]:
            recently_played_videos.append(os.path.abspath(chosen_video))
        # go to next video directory in VIDEO_DIRECTORIES
        current_video_directory += 1

def terminate_main_loop():
    '''set the loop to inactive, thus ensuring the thread ends, 
    killing the thread, and kill any mpv windows left over'''
    global FAUXBLE_ACTIVE
    FAUXBLE_ACTIVE = False
    #os.system("TASKKILL /PID " + str(MPV.pid) + " /T")
    subprocess.Popen(['TASKKILL', '/PID', str(VIDEOPLAYER_THREAD.pid), '/T', '/F'], creationflags=subprocess.CREATE_NO_WINDOW)

def create_control_window():
    '''create the window to control fauxble'''
    # root of control window
    root = tkinter.Tk()
    root.title("Fauxble Control")
    # frame containing general fauxble functions, like starting and stopping
    general_frame = tkinter.Frame(root)
    general_frame.grid(column=0, row=0)
    start_button = tkinter.Button(general_frame, text="Start Fauxble", command=lambda:[start_button.grid_forget(), threading.Thread(target=main_loop).start(), stop_button.grid(column=0, row=0)])
    start_button.grid(column=0, row=0)
    stop_button = tkinter.Button(general_frame, text="Stop Fauxble", command=lambda:[stop_button.grid_forget(), terminate_main_loop(), start_button.grid(column=0, row=0)])
    # frame containing secondary functions, like adding videos to the queue
    secondary_frame = tkinter.Frame(root)
    secondary_frame.grid(column=1, row=0)
    # queue functionality
    add_to_queue_button = tkinter.Button(secondary_frame, text = "Add to Queue", command=lambda:[VIDEO_QUEUE.extend(list(tkinter.filedialog.askopenfilenames(parent=root,initialdir=SCRIPT_ROOT))),update_queue_text()])
    add_to_queue_button.grid(column=0, row=0)
    clear_queue_button = tkinter.Button(secondary_frame, text = "Clear Queue", command=lambda:[VIDEO_QUEUE.clear(), update_queue_text()])
    clear_queue_button.grid(column=0, row=1)
    # video directory cycle functionality
    vid_dir_cycle_button = tkinter.Button(secondary_frame, text = "Change Video Directory Cycle", command=lambda:[VIDEO_DIRECTORY_CYCLE.clear(), VIDEO_DIRECTORY_CYCLE.extend(tkinter.simpledialog.askstring(title="Change Video Directory Cycle",prompt="What do you want the new video directory cycle to be? Separate each entry with a space.").split()),update_video_directory_cycle_text()])
    vid_dir_cycle_button.grid(column=0, row=2)
    # frame containing information about certain variables
    variable_area_frame = tkinter.Frame(root)
    variable_area_frame.grid(column=2, row=0)
    # queue
    queue_label = tkinter.Label(variable_area_frame, text="Current Queue")
    queue_label.grid(column=0, row=0)
    global QUEUE_TEXT
    QUEUE_TEXT = tkinter.Label(variable_area_frame)
    update_queue_text()
    QUEUE_TEXT.grid(column=0, row=1)
    # video directory cycle
    video_directory_cycle_label = tkinter.Label(variable_area_frame, text="Video Directory Cycle")
    video_directory_cycle_label.grid(column=0, row=2)
    global VIDEO_DIRECTORY_CYCLE_TEXT
    VIDEO_DIRECTORY_CYCLE_TEXT = tkinter.Label(variable_area_frame)
    update_video_directory_cycle_text()
    VIDEO_DIRECTORY_CYCLE_TEXT.grid(column=0, row=3)
    root.mainloop()

create_control_window()
terminate_main_loop() # terminate the loop in case the gui is closed before the loop
