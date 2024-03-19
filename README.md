# Video-Upscaler

This project uses Tkinter windows, Tkinter drag and drop (TkinterDnD), Moviepy, and OpenCV to upscale a 16:9 resolution video to specific resolutions

1: Creates the interface window with Tkinter
2: Places all of the buttons, input boxes, and other interactables with Tkinter and TkinterDnD
3: User drops a video in the input box
4: User selects the resolution to upscale the video to from the drop down menu
    - Note: The program will accept any resolution video, but if the video dimensions are not 4:3 or 16:9 then the end result will not be good
5: User starts the program by clicking on the "Upscale" button
6: Output video is provided in the same directory as the input video