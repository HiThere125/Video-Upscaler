import cv2, gc, os, moviepy.editor as editor
from tkinter import *
from tkinterdnd2 import DND_FILES, TkinterDnD
from threading import *

#
#   The purpose of this program is to be able to upscale (resize) a video to 1080p
#   1:  Tkinter is used to handle the drag and drop aspect to get the path of the video
#   2:  Moviepy is used to get the audio from the video
#   3:  OpenCV is used to upscale the video
#   4:  Moviepy is used to combine the upscaled video and the audio
#   5:  OS is used to remove all temporary files
#
#   Notes:
#   1:  Threading is used to ensure the tkinter window is still responsive while processing the video
#       -   Despite this it is recommended to only upscale one video at a time to reduce CPU load
#
#   Future Plans:
#   1:  Implement additional image processing to increase the visual quality
#
#-----------------------------------------CODE STARTS HERE-----------------------------------------------------

''' Extracts audio from a video given a String file path and saves it in the same directory
    @Params:    video_path  |   String  |   File path of the video that is being upscaled
    @Returns:   audio_path  |   String  |   File path of audio extracted from the video'''
def convert_video_to_audio(video_path):
    video_file = editor.VideoFileClip(video_path)
    audio = video_file.audio
    audio_path = video_path.replace('.mp4', '.mp3')
    audio.write_audiofile(audio_path, bitrate = '320k')
    video_file.close()
    audio.close()
    return audio_path       

''' Combines an audio file and the temporary video and saves it at the output path
    @Params:    temp_path   |   String  |   File path of the temporary video file that needs audio
                audio_path  |   String  |   File path of the audio file to use
                fps         |   Integer |   Frames per second of the video file
                output_path |   String  |   File path to save the final video to'''
def add_audio_to_video(temp_path, audio_path, fps, output_path):
    video = editor.VideoFileClip(temp_path) 
    audio = editor.AudioFileClip(audio_path) 
    final_video = video.set_audio(audio)
    final_video.write_videofile(filename=output_path, codec="libx264", fps=fps)
    video.close()
    audio.close()    
    final_video.close()    

''' Creates and returns the paths for the temporary video (without audio), and the final output video
    @Params:    video_path  |   String  |   File path of the video that is being upscaled
                size        |   String  |   Size to upscale the video to
    @Returns:   output_path |   String  |   File path to save the final video to
                temp_path   |   String  |   File path of the temporary video file that needs audio'''
def get_output_path(video_path, size):
    split_path = video_path.replace("/", "\\").split("\\")
    output_path = ""
    temp_path = ""
    for part in split_path:
        if ".mp4" in part:
            output_path = output_path + "\\Upscaled " + part
            temp_path = temp_path + "\\Temp " + part
        elif part == split_path[0]:
            output_path = part
            temp_path = part
        else:            
            output_path = output_path + "\\" + part
            temp_path = temp_path + "\\" + part
    if "480" in output_path:
        output_path = output_path.replace("480", size)
    elif "720" in output_path:
        output_path = output_path.replace("720", size)
    return output_path, temp_path

''' Returns various details about the video that is being upscaled: FPS, Total Frames, Duration, Resolution
    @Params:    video_path  |   String  |   File path of the video that is being upscaled
    @Returns:   fps         |   Integer |   Frames per second of the video file
                frame_count |   Integer |   Total frames in the video file
                duration    |   Integer |   Total length of the video file
                resolution  |   List    |   The size of the frames in the video file
                    [0]     |   Integer |   Width of the frame in pixels
                    [1]     |   Integer |   Height of the frame in pixels'''
def get_video_info(video_path):
    video = cv2.VideoCapture(video_path)
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(round(video.get(cv2.CAP_PROP_FPS)))               # Rounds fps to the nearest integer to account for weird cases
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count/fps
    resolution = [frame_width, frame_height]
    return fps, frame_count, duration, resolution

''' Upscales the video and saves it at the temp path
    @Params:    video_path  |   String  |   File path of the video that is being upscaled
                temp_path   |   String  |   File path of the temporary video file that needs audio
                size        |   String  |   Size to upscale the video to
                fps         |   Integer |   Frames per second of the video file'''
def upscale_video(video_path, temp_path, size, fps):
    # Open the input video file
    cap = cv2.VideoCapture(video_path)
    
    # Define the desired output resolution
    new_width = 1920
    new_height = 1080
    if size == "480":
        new_width = 640
        new_height = 480
    elif size == "720":
        new_width = 1280
        new_height = 720
    elif size == "1440":
        new_width = 2560
        new_height = 1440
    elif size == "4k":
        new_width = 3840
        new_height = 2160
    elif size == "8k":
        new_width = 7680
        new_height = 4320
    
    # Create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv2.VideoWriter(temp_path, fourcc, fps, (new_width, new_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Resize the frame to the desired resolution
        resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_CUBIC) # cv2.INTER_LANCZOS4 is another interpolation option
        
        # Write the resized frame to the output video file
        out.write(resized_frame)
    
    # Release VideoCapture and VideoWriter objects
    cap.release()
    out.release()

''' Handles all of the function calls to upscale the video
    @Params:    video_path  |   String  |   File path of the video that is being upscaled
                size        |   String  |   Size to upscale the video to'''
def upscaler(video_path, size):
    print("Beginning upscaling process")
    audio_path = convert_video_to_audio(video_path)

    print("\nGetting Video Info:")
    fps, frame_count, duration, resolution = get_video_info(video_path)
    print(f"FPS: {fps}\nFrame Count: {frame_count}\nDuration: {duration}\nResolution: {resolution}")

    print("\nGetting Output Path")
    output_path, temp_path = get_output_path(video_path, size)
    print(f"Output Path: {output_path}")
    
    print(f"\nUpscaling video\nSaving Temp to: {temp_path}")
    upscale_video(video_path, temp_path, size, fps)

    print("Adding audio to video")
    add_audio_to_video(temp_path, audio_path, fps, output_path)
    gc.collect()

    print("Removing temporary files")
    os.remove(temp_path)
    os.remove(audio_path)
    gc.collect()

''' Processes the drag and drop input event, changing the label to reflect what was most recently dropped in the box
    @Params:    event       |           |   Drag and drop event'''
def process_input(event):
    path = event.data.replace("{","").replace("}","")
    window.insert("end", path)
    l3.config(text = path)

''' Starts the upscaling process by pulling the text from label l3 and using that as the video path'''
def take_input():
    PATH_INPUT = l3.cget("text")
    SIZE = clicked.get()
    thread1 = Thread(target=upscaler, args=(PATH_INPUT, SIZE))
    thread1.start()



if __name__ == "__main__":
    root = TkinterDnD.Tk()
 
    # Specify size of window.
    root.geometry("1000x350")
 
    # Create labels
    l = Label(root, text = "Upscaler")
    l2 = Label(root, text = "Path to video:")
    l3 = Label(root, text = "")
    
    # Create drop down menu
    options = ["480", "720", "1080", "1440", "4k", "8k"]
    clicked = StringVar()           # Datatype of menu text
    clicked.set("1080")             # Initial menu text
    drop = OptionMenu( root , clicked , *options )

    # Create button for next text.
    b1 = Button(root, text = "Upscale", command = lambda:take_input())
 
    # Create an Exit button.
    b2 = Button(root, text = "Exit",
                command = root.destroy)

    # Create Drag and Drop box
    window = Listbox(root)
    window.drop_target_register(DND_FILES)
    window.dnd_bind('<<Drop>>', process_input)
 
    # Pack all tkinter window components
    l.pack()
    drop.pack()    
    l2.pack()
    l3.pack()
    window.pack()
    b1.pack()
    b2.pack()
    
    # Run the tkinter window
    mainloop()
