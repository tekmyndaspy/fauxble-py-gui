'''an application to alternate between playing random videos from a main folder and its subfolders 
and an intermediary folder and its subfolders'''

import threading # for allowing fauxble mainloop to run alongside gui to control the mainloop
import tkinter # for creating guis
import subprocess # for running applications with a great deal of control
import random # for pseudorandomly choosing things
import os
import sys

# user definable variables follow
VIDEO_DIRECTORIES = ['Main', 'Intermediary']
MAIN_VIDEO_DIRECTORY = 'Main'
INTERMEDIARY_VIDEO_DIRECTORY = 'Intermediary'
ALLOWED_EXTENSIONS = ['.mp4', '.webm', '.mkv']
VIDEOPLAYER = 'mpv --no-config --terminal=no --fullscreen --af=loudnorm'

# constants used by the script. best not to touch these
SCRIPT_ROOT = os.path.dirname(sys.argv[0])

print("Starting Fauxble.")
randomMessages = ["\"smoking pot and programming camp, i don\'t give a shit\" - casket",
                  "\"fuck batch. me and my homies all hate batch\" - tekmyndaspy"]
print(random.choice(randomMessages))

FAUXBLE_ACTIVE = False
VIDEOPLAYER_PROCESS = None

def main_loop():
    '''loop that governs the playing of videos'''
    global FAUXBLE_ACTIVE, VIDEOPLAYER_PROCESS
    FAUXBLE_ACTIVE = True
    current_video_directory = 0
    while FAUXBLE_ACTIVE:
        # choose video directory
        if current_video_directory > len(VIDEO_DIRECTORIES) - 1:
            current_video_directory = 0

        # choose video
        os.chdir(SCRIPT_ROOT)
        os.chdir(VIDEO_DIRECTORIES[current_video_directory])
        # loop through directory and subdirectories until a video is chosen
        file_not_chosen = True
        chosen_video = None
        while file_not_chosen and chosen_video is None:
            files_in_directory = os.listdir()
            # if the working directory has no items,
            # return to the current video directory and restart loop
            if not files_in_directory:
                os.chdir(SCRIPT_ROOT)
                os.chdir(VIDEO_DIRECTORIES[current_video_directory])
                continue
            # select random item in working directory for review
            potential_item = random.choice(files_in_directory)
            # if the item is a directory, enter the directory and restart the loop
            if os.path.isdir(potential_item):
                os.chdir(potential_item)
                continue
            # if the item is a file, do further checking
            if os.path.isfile(potential_item):
                # if the file's extension is not in ALLOWED_EXTENSIONS,
                # return to the current video directory and restart loop
                if os.path.splitext(potential_item)[-1].lower() not in ALLOWED_EXTENSIONS:
                    os.chdir(SCRIPT_ROOT)
                    os.chdir(VIDEO_DIRECTORIES[current_video_directory])
                    continue
                # if no previous checks fail, choose the file for playback
                chosen_video = potential_item
                file_not_chosen = False
        # play the chosen file
        VIDEOPLAYER_PROCESS = subprocess.Popen(['mpv', '--no-config', '--terminal=no'] +
                                               [chosen_video],
                                               creationflags=subprocess.CREATE_NO_WINDOW)
        VIDEOPLAYER_PROCESS.wait()
        # go to next video directory in VIDEO_DIRECTORIES
        current_video_directory += 1


def terminate_main_loop():
    '''set the loop to inactive, thus ensuring the thread ends, 
    killing the thread, and kill any mpv windows left over'''
    global FAUXBLE_ACTIVE
    FAUXBLE_ACTIVE = False
    #os.system("TASKKILL /PID " + str(MPV.pid) + " /T")
    subprocess.Popen(['TASKKILL', '/PID', str(VIDEOPLAYER_PROCESS.pid), '/T', '/F'],
                     creationflags=subprocess.CREATE_NO_WINDOW)

def create_control_window():
    '''create the window to control fauxble'''
    root = tkinter.Tk()
    root.title("Fauxble")

    # frame containing general fauxble functions, like starting and stopping
    general_frame = tkinter.Frame(root)
    general_frame.pack()
    start_button = tkinter.Button(general_frame, text="Start Fauxble",
                                  command=lambda:[start_button.pack_forget(),
                                                  threading.Thread(target=main_loop).start(),
                                                  stop_button.pack()])
    start_button.pack()
    stop_button = tkinter.Button(general_frame, text="Stop Fauxble",
                                 command=lambda:[stop_button.pack_forget(),
                                                 terminate_main_loop(), start_button.pack()])

    root.mainloop()

create_control_window()
terminate_main_loop() # terminate the loop in case the gui is closed before the loop
