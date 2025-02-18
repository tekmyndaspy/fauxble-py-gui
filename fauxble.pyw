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
import logging

# instantiate loggers
# most lines are commented out while not testing to not create unnecessary files, 
# though the creation of the loggers themselves is left in to not cause errors with later logging statements
general_logger = logging.getLogger('general_logger')
general_log_handle = logging.FileHandler('fauxble.log', encoding='utf-8')
general_log_handle.setFormatter(logging.Formatter("[%(asctime)s] %(name)s: %(levelname)s, %(message)s"))
general_logger.addHandler(general_log_handle)
general_logger.setLevel(logging.WARNING)

video_logger = logging.getLogger('video_logger')
#video_log_handle = logging.FileHandler('videos.log', encoding='utf-8')
#video_logger.addHandler(video_log_handle)
#video_logger.setLevel(logging.INFO)

# fauxble default settings
# it is recommended to use a separate fauxble_settings.py file within the same 
# directory as this file if you wish to change these settings
# these settings will be set back to the defaults upon updating, as this file will be overwritten
general_logger.info('setting default settings')
ALLOWED_EXTENSIONS = ['.mp4', '.webm', '.mkv']
VIDEO_PLAYER = 'mpv'
VIDEO_PLAYER_FLAGS = ['--no-config', '--terminal=no', '--fullscreen', '--af=loudnorm']
VIDEO_DIRECTORY_CYCLE = ['Main', 'Intermediary']
VIDEOS_UNTIL_REPLAY = 48

# overwrite defaults with user defined settings, if applicable
try:
    from fauxble_settings import *
    general_logger.info('successfully imported fauxble_settings.py, likely overwriting default settings with user settings.')
except ModuleNotFoundError:
    general_logger.warning('failed to import fauxble_settings.py. this may or may not be important.')

# script constants
general_logger.debug('creating script root constant')
SCRIPT_ROOT = sys.path[0]

# globals for communication between threads
general_logger.debug('create commuincation variables')
VIDEO_PLAYER_THREAD = None
FAUXBLE_ACTIVE = False
QUEUE = []
QUEUE_TEXT = ""
VIDEO_DIRECTORY_CYCLE_TEXT = None
RECENTLY_PLAYED_VIDEOS = []
RECENTLY_PLAYED_MAIN_VIDEOS_TEXT = None

def get_random_file(directory, allowed_extensions=[], disallowed_files=[]):
    '''
    returns a random file from the specified directory that satisfies the 
    specified allowed extensions.

    accepts a string referring to a directory the fauxble root, such as 'Main',
    a list of allowed extensions, such as ['.mp4', '.webm', '.mkv'],
    a list of disallowed files, such as ['one.mp4','two.mp4','three.mp4']
    '''

    general_logger.info('moving to ' + directory)
    os.chdir(directory)

    # loop through directory
    file_is_chosen = False
    while not file_is_chosen:
        files_in_directory = os.listdir()
        # if the working directory has no items, return to the video directory and restart the loop, 
        # otherwise carry on
        if not files_in_directory:
            general_logger.warning('no files in ' + os.curdir() + '. is this intentional? moving to ' + directory + ' and restarting search.')
            os.chdir(directory)
            continue
        
        # select random item in working directory for review
        potential_item = random.choice(files_in_directory)
        general_logger.info('selected ' + potential_item + ' for review.')
        
        # if the item is a directory, enter the directory and restart the loop, 
        # otherwise carry on
        if os.path.isdir(potential_item):
            general_logger.info(potential_item + ' is a directory. entering, then restarting search from new directory.')
            os.chdir(potential_item)
            continue
        
        # the item is a file if it is not a directory

        # if the file is in disallowed_files, return to the video directory and restart the loop,
        # otherwise carry on
        if os.path.abspath(potential_item) in disallowed_files:
            general_logger.info(potential_item + ' in disallowed files. restarting search from ' + directory + '.')
            os.chdir(directory)
            continue
        # if the file is not in allowed_extensions, return to the video directory and restart the loop, 
        # otherwise carry on
        if os.path.splitext(potential_item)[-1].lower() not in allowed_extensions:
            general_logger.info(potential_item + ' extension not in ' + ','.join(allowed_extensions) + '. restarting from ' + directory + '.')
            os.chdir(directory)
            continue
        # if no previous checks fail, return the file
        general_logger.info(potential_item + ' passed all checks. returning file.')
        return potential_item

def main_loop():
    '''loop that governs how videos are chosen and played'''
    global FAUXBLE_ACTIVE, VIDEO_PLAYER_THREAD, RECENTLY_PLAYED_VIDEOS
    # set initial values and begin constantly running loop
    general_logger.info('beginning main fauxble loop.')
    current_video_directory = 0
    FAUXBLE_ACTIVE = True
    while FAUXBLE_ACTIVE:
        # if the video directory index is outside the list range, set it to the beginnning
        if current_video_directory > len(VIDEO_DIRECTORY_CYCLE) - 1:
            general_logger.info('video directory index outside list range. setting to beginning.')
            current_video_directory = 0
        
        # if there is a video on the video queue, choose the first video on the queue then remove that video from the queue, 
        # otherwise choose a random video from the current video directory
        if VIDEO_DIRECTORY_CYCLE[current_video_directory] == VIDEO_DIRECTORY_CYCLE[0] and QUEUE:
            general_logger.info('there is a video on the video queue. selecting first video on the queue for playback, then removing it from the queue.')
            chosen_video = QUEUE[0]
            QUEUE.pop(0)
            update_queue_text()
        else:
            general_logger.info('no video is on the queue. selecting random file from ' + VIDEO_DIRECTORY_CYCLE[current_video_directory] + '.')
            chosen_video = get_random_file(os.path.join(SCRIPT_ROOT, VIDEO_DIRECTORY_CYCLE[current_video_directory]), ALLOWED_EXTENSIONS, RECENTLY_PLAYED_VIDEOS)
            general_logger.info('selected ' + chosen_video + ' from ' + VIDEO_DIRECTORY_CYCLE[current_video_directory] + '.')

        # if there is an active video thread, wait until it ends to continue
        if VIDEO_PLAYER_THREAD:
            general_logger.info('there is currently a playing video. waiting until it ends to play selected video.')
            VIDEO_PLAYER_THREAD.wait()

        # if fauxble is active, play the chosen video
        if FAUXBLE_ACTIVE:
            general_logger.info('playing ' + chosen_video + '.')
            if VIDEO_DIRECTORY_CYCLE[current_video_directory] == VIDEO_DIRECTORY_CYCLE[0]:
                video_logger.info(os.path.abspath(chosen_video))
            VIDEO_PLAYER_THREAD = subprocess.Popen([VIDEO_PLAYER] + VIDEO_PLAYER_FLAGS + [chosen_video], creationflags=subprocess.CREATE_NO_WINDOW)

        # if the video directory is the same as the first in the video directory, 
        # add the last played video to the recently played videos
        if VIDEO_DIRECTORY_CYCLE[current_video_directory] == VIDEO_DIRECTORY_CYCLE[0]:
            general_logger.info('main video directory cycle')
            RECENTLY_PLAYED_VIDEOS.append(os.path.abspath(chosen_video))
            update_recently_played_videos_text()

        # if the number of videos is greater than acceptable in the recently played videos list
        # remove enough videos from the list until it is within an acceptable range
        if len(RECENTLY_PLAYED_VIDEOS) > VIDEOS_UNTIL_REPLAY - 1:
            general_logger.info('the number of items in the recently played videos list is higher than it should be. removing enough such that it is under the limit.')
            del RECENTLY_PLAYED_VIDEOS[0:len(RECENTLY_PLAYED_VIDEOS) - VIDEOS_UNTIL_REPLAY]
            update_recently_played_videos_text()

        # add one to the video directory index
        general_logger.info('going to next directory in video directory cycle.')
        current_video_directory += 1

def terminate_main_loop():
    '''kill the thread and kill any mpv windows left over'''
    global FAUXBLE_ACTIVE
    FAUXBLE_ACTIVE = False
    # kill the thread
    general_logger.info('killing any video player threads left over.')
    subprocess.run(['TASKKILL', '/PID', str(VIDEO_PLAYER_THREAD.pid), '/T', '/F'], creationflags=subprocess.CREATE_NO_WINDOW)

def update_queue_text():
    general_logger.info('updating queue text in control panel.')
    QUEUE_TEXT.config(text='\n'.join(QUEUE))

def update_video_directory_cycle_text():
    general_logger.info('updating directory cycle text in control panel.')
    VIDEO_DIRECTORY_CYCLE_TEXT.config(text=', '.join(VIDEO_DIRECTORY_CYCLE))

def update_recently_played_videos_text():
    general_logger.info('updating recently played main videos text in control panel.')
    RECENTLY_PLAYED_MAIN_VIDEOS_TEXT.config(text='\n'.join(RECENTLY_PLAYED_VIDEOS[-5:][::-1]))

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
    change_video_directory_cycle_button = tkinter.Button(secondary_frame, text = "Change Video Directory Cycle", command=lambda:[VIDEO_DIRECTORY_CYCLE.clear(), VIDEO_DIRECTORY_CYCLE.extend(tkinter.simpledialog.askstring(title="Change Video Directory Cycle",prompt="What do you want the new video directory cycle to be? Separate each entry with a \'>\'.").split('>')),update_video_directory_cycle_text()])
    change_video_directory_cycle_button.grid(column=0, row=2)
    # recently played videos functionality
    clear_recently_played_videos_button = tkinter.Button(secondary_frame, text="Clear Recently Played Videos", command=lambda:[RECENTLY_PLAYED_VIDEOS.clear(), update_recently_played_videos_text()])
    clear_recently_played_videos_button.grid(column=0, row=3)

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
    # recently played videos information
    recently_played_main_videos_label = tkinter.Label(information_frame, text="Recently Played Main Videos")
    recently_played_main_videos_label.grid(column=0, row=4)
    global RECENTLY_PLAYED_MAIN_VIDEOS_TEXT
    RECENTLY_PLAYED_MAIN_VIDEOS_TEXT = tkinter.Label(information_frame)
    update_recently_played_videos_text()
    RECENTLY_PLAYED_MAIN_VIDEOS_TEXT.grid(column=0, row=5)

    root.mainloop()

if __name__ == '__main__':
    # create the fauxble control panel
    create_control_panel()
    # terminate any left over video players if the window was closed without stopping fauxble first
    if VIDEO_PLAYER_THREAD:
        general_logger.info('fauxble not stopped before closing control panel. stopping fauxble.')
        terminate_main_loop()