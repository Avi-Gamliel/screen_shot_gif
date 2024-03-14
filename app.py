from tkinter import *
from PIL import Image, ImageTk
import time
import win32gui
import ctypes
import mss.tools
import threading
from tkinter.filedialog import asksaveasfile


ctypes.windll.user32.SetProcessDPIAware()

global start_record, flag, screen_number

start_record = True
im_cursor = Image.open('arrow.png')
master = Tk()
master.title("avi assistant")

width = 400
meduim_screen = 800
full_screen = master.winfo_screenwidth()

height = 50
flag = True
frames = []
screen_number = 1
screens = []


start_time_ref = False
count_frame_prev = 0
gap = 20

canvas_width = width - gap

toggle_screens_to_choose = False

start, end = 0 ,width

## create navbar  float
master.geometry("%dx%d+%d+%d" % (width, height, (master.winfo_screenwidth() / 2) - (width / 2), 0))
master.configure(bg="skyblue")
master.overrideredirect(True)
master.rowconfigure(0, weight=1)
master.rowconfigure(1, weight=1)
master.columnconfigure(0, weight=1)

left_frame = Frame(master, width=canvas_width, height = height - 20, bg="white", bd=0.5)
left_frame.grid(row=0, column=0, padx=10, pady=10)
left_frame.rowconfigure(0, weight=1)
left_frame.columnconfigure(0, weight=1)
left_frame.columnconfigure(1, weight=1)
left_frame.columnconfigure(2, weight=1)


left_frame.grid_propagate(False)
btn_action_frame = Frame(left_frame)
btn_action_frame.grid(row=0, column=0, sticky="nswe")
btn_action_frame.rowconfigure(0, weight=1)
btn_action_frame.columnconfigure(0, weight=1)
btn_action_frame.columnconfigure(1, weight=1)
btn_action_frame.grid_propagate(False)

frame_prev_width = 0
frame_prev_height = 0


with mss.mss() as sct:
    screens = sct.monitors[1:]

def record_screen():
    global start_time
    print("start recording ...")
    close_toggle_choose_screens()
    count_frame = 0
    while flag:
        im = screen_shot(index=screen_number)
        count_frame += 1
        frames.append(im)
        time.sleep((1000/16)/1000)
        print("ok")
    else:
        play_result()


def start_recording():
    global flag
    flag = True
    threading.Thread(target=record_screen, args=()).start()

def get_image_bytes(index=1):
    with mss.mss() as sct:
        monitor_number = int(index)
        mon = screens[monitor_number - 1]
        monitor = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"],
            "height": mon["height"]
        }
        sct_img = sct.grab(monitor)
        return sct_img

def screen_shot(index=1):
    global image_object
    bytes_image = get_image_bytes(index=index)
    curX, curY = win32gui.GetCursorPos()

    if curX < 0:
        curX = (-1 * screens[screen_number - 1]["left"]) + curX

    image_object = Image.frombytes("RGB", bytes_image.size, bytes_image.bgra, "raw", "BGRX").convert("RGBA")
    image_object.paste(im_cursor, box=(curX, curY), mask=im_cursor)
    return image_object


def stop_recording():
    global flag
    flag = False
    init_edit_frame()



def choose_screen():
    global frame_photo_1
    global toggle_screens_to_choose,left_frame, images, screen_number
    i = 0
    if (toggle_screens_to_choose == False):
        toggle_screens_to_choose = True
        master.geometry("%dx%d+%d+%d" % (width, height + 150, (master.winfo_screenwidth() / 2) - (width / 2), 1))
        w = 150

        frame_photo_1 = Frame(master, width =width, height=150, bg="yellow")
        frame_photo_1.grid(row=1, column=0)
        images = []
        for _ in screens:
            screen_1 = screen_shot(index=i + 1)
            screen_1_resize = screen_1.resize((w, int(screen_1.height / (screen_1.width / w))))
            photo_1 = ImageTk.PhotoImage(screen_1_resize)
            photo_1_label = Label(frame_photo_1, image=photo_1)
            def mouse_up(e,index):
                global screen_number
                screen_number= index + 1
            photo_1_label.bind('<ButtonRelease>', lambda e,i=i:mouse_up(e,i))
            if i ==0:
                photo_1_label.place(relx=0, rely=0.5, anchor=W)
            else:
                photo_1_label.place(relx=1, rely=0.5, anchor=E)

            images.append(photo_1)
            if i <= 1:
                i += 1
    else:
        close_toggle_choose_screens()

def close_toggle_choose_screens():
    global toggle_screens_to_choose, frame_photo_1
    toggle_screens_to_choose = False
    master.geometry("%dx%d+%d+%d" % (width, height, (master.winfo_screenwidth()/2) - (width/2), 0))
    frame_photo_1.grid_forget()

result_times = []

def turn_px_to_fr(px, frame_len):
    global canvas_width, result_times
    fps = 10
    sec = frame_len / fps
    time_in_sec = px * (sec / canvas_width)

    class res:
        fr = round(fps / (1 / time_in_sec))
        time = time_in_sec

    result_times.append(res)
    return res

def turn_fr_to_px(fr, frames_len):

    global canvas_width, result_times, px
    fps = 10
    sec = frames_len / fps
    px = fr * (canvas_width / sec)

    class res:
        global px
        px = round(px)
    return res

images_prev = []

def play_result():
    global frames, video_out_put_label, images_prev, photo_prev_1, width_prev_1_label
    ## get the images

    start_video_ref()

def init_edit_frame():

    global toggle_screens_to_choose, side, frames, video_out_put_label, handle, C,frame_prev_height,frame_prev_width, width
    width = meduim_screen
    frame_prev_width = width - 20
    frame_prev_height = int(frames[0].height / (frames[0].width / (width - 20)))
    toggle_screens_to_choose = True
    master.geometry("%dx%d+%d+%d" % (frame_prev_width, height + frame_prev_height + 150, (master.winfo_screenwidth()/2)-(width /2), 1))
    frame_edit = Frame(master, width =width , height=height + frame_prev_height + 100, bg="yellow")
    frame_edit.columnconfigure(0,weight=1)
    frame_edit.rowconfigure(0,weight=1)
    frame_edit.rowconfigure(1,weight=1)
    frame_edit.rowconfigure(2,weight=1)
    frame_edit.grid(row=1, column=0)
    frame_edit.grid_propagate(False)

    top_frame = Frame(frame_edit, width=width , height=50, bg="blue")
    top_frame.grid(row=0, column=0)
    top_frame.columnconfigure(0, weight=1)
    top_frame.columnconfigure(1, weight=1)
    top_frame.columnconfigure(2, weight=1)
    top_frame.rowconfigure(0, weight=1)
    top_frame.grid_propagate(False)

    button_prev_actions = Frame(top_frame)
    button_prev_actions.grid(row=0, column=0, sticky="nswe")
    button_prev_actions.rowconfigure(0,weight=1)
    button_prev_actions.columnconfigure(0,weight=1)
    button_prev_actions.columnconfigure(1,weight=1)
    button_prev_actions.grid_propagate(False)

    button_play = Button(button_prev_actions, text="play", command=start_video_btn)
    button_play.grid(row=0, column=0)
    button_stop = Button(button_prev_actions, text="stop", command=stop_video_ref)
    button_stop.grid(row=0, column=1)

    button_save = Button(top_frame, text="save", command=save_file)
    button_save.grid(row=0, column=2)


    middle_frame = Frame(frame_edit, width=frame_prev_width, height=frame_prev_height, bg="cyan")
    middle_frame.grid(row=1, column=0)
    middle_frame.rowconfigure(0, weight=1)
    middle_frame.columnconfigure(0, weight=1)
    middle_frame.grid_propagate(False)

    bottom_frame = Frame(frame_edit, width=width, height=50, bg="blue")
    bottom_frame.grid(row=2,column=0)
    bottom_frame.grid_propagate(False)


    video_out_put_label = Label(middle_frame, width=frame_prev_width, height=frame_prev_height, bg="purple" )
    video_out_put_label.grid(row=0, column=0)
    video_out_put_label.columnconfigure(1,weight=1)
    video_out_put_label.rowconfigure(1,weight=1)
    video_out_put_label.grid_propagate(False)


    C = Canvas(bottom_frame, bg="green", width=width -20, height=50-20)
    C.pack()

    bar = C.create_rectangle(50,0,width - 20, 50-20, fill="red")
    handle = C.create_rectangle(0,0,10, 50-20, fill="blue")

    side =""
    x1 = 0
    x2 = 0

    def on_press(e):
        global drag_trim, x1, x2, side, rs
        drag_trim = True
        bar_position = C.coords(bar)
        bar_x1 = bar_position[0]
        bar_x2 = bar_position[2]
        handle_pos = C.coords(handle)
        rs = 0
        if handle_pos[0] < e.x  and handle_pos[2] > e.x:
            ## move handle
            rs = e.x - handle_pos[0]
            return

        if bar_x1 - 10 < e.x and bar_x1 + 10 > e.x:
            side = "start"
        elif bar_x2 -10 < e.x and bar_x2 +10 > e.x:
            side = "end"
        else:
            side = ""

    def on_move(e):
        global drag_trim, x1, x2 ,side, rs,count_frame_prev,photo_prev_1,images_prev
        bar_position = C.coords(bar)
        bar_x1 = bar_position[0]
        bar_x2 = bar_position[2]
        bar_y2 = bar_position[2]
        if drag_trim and rs > 0:
            C.coords(handle, e.x - rs, 0, (e.x - rs) + 10,50-20)
            frame_choose = turn_px_to_fr(e.x, len(frames))
            count_frame_prev = int(frame_choose.fr)
            frame_resize = frames[count_frame_prev].resize(
                (width - 20, int(frames[count_frame_prev].height / (frames[count_frame_prev].width / (width - 20)))))
            photo_prev_1 = ImageTk.PhotoImage(frame_resize)
            photo_prev_1_label = Label(video_out_put_label, image=photo_prev_1)
            photo_prev_1_label.grid(row=0, column=0)
            images_prev.append(photo_prev_1)
            return
        if drag_trim:
            if side == "start":
                C.coords(bar, e.x, 0, bar_x2, bar_y2)
                frame_choose = turn_px_to_fr(e.x, len(frames))
                count_frame_prev = int(frame_choose.fr)
                frame_resize = frames[count_frame_prev].resize((width - 20, int(frames[count_frame_prev].height / (frames[count_frame_prev].width / (width - 20)))))
                photo_prev_1 = ImageTk.PhotoImage(frame_resize)
                photo_prev_1_label = Label(video_out_put_label, image=photo_prev_1)
                photo_prev_1_label.grid(row=0, column=0)
                images_prev.append(photo_prev_1)
            elif side == "end":
                C.coords(bar, bar_x1, 0, e.x, bar_y2)
                frame_choose = turn_px_to_fr(e.x, len(frames))
                count_frame_prev = int(frame_choose.fr)
                frame_resize = frames[count_frame_prev].resize((width - 20, int(
                    frames[count_frame_prev].height / (frames[count_frame_prev].width / (width - 20)))))
                photo_prev_1 = ImageTk.PhotoImage(frame_resize)
                photo_prev_1_label = Label(video_out_put_label, image=photo_prev_1)
                photo_prev_1_label.grid(row=0, column=0)
                images_prev.append(photo_prev_1)

    def on_release(e):
        global drag_trim, frames, start, end
        drag_trim = False
        bar_position = C.coords(bar)
        bar_x1 = bar_position[0]
        bar_x2 = bar_position[2]
        start = turn_px_to_fr(bar_x1, len(frames)).fr
        end = turn_px_to_fr(bar_x2, len(frames)).fr

    C.bind("<Button-1>", on_press)
    C.bind("<ButtonRelease-1>", on_release)
    C.bind("<B1-Motion>", on_move)

def start_video_ref():
    global start_time_ref, count_frame_prev, video_out_put_label, frames, C
    start_time_ref = True
    while start_time_ref:

        frame_resize = frames[count_frame_prev].resize((width - 20, int(frames[count_frame_prev].height / (frames[count_frame_prev].width /(width-20)))))
        photo_prev_1 = ImageTk.PhotoImage(frame_resize)
        photo_prev_1_label = Label(video_out_put_label, image=photo_prev_1)
        photo_prev_1_label.grid(row=0, column=0)
        images_prev.append(photo_prev_1)
        count_frame_prev += 1

        if count_frame_prev == len(frames):
            count_frame_prev = 0
            C.coords(handle, 0,0,10,50-20)
        else:
            C.move(handle, width / (len(frames) / 10) / 10  , 0)
        time.sleep(1/10)

def stop_video_ref():
    global start_time_ref
    start_time_ref = False

def start_video_btn():
    threading.Thread(target=start_video_ref, args=()).start()

def save_file():
    global start, end
    print(start, end)
    files = (
        ("Gif File", "*.gif"),
        ("All files", "*.")
    )
    filenames = asksaveasfile(filetypes=files, defaultextension="*.gif")
    # showinfo(title="saved path", message=filenames)


    our_path = str(filenames.name)
    print(our_path)
    frames[int(start)].save(
        our_path,
        save_all=True,
        append_images=frames[int(start)+1:int(end)],
        optimize=False,
        duration=int(1000 / 100),
        loop=0)
    print("stop recording ...")

# create buttons
btn_choose_screen = Button(left_frame, text="choose screen", command=choose_screen)
# btn_choose_screen.place(relx=1, rely=0.5, anchor=E)
btn_choose_screen.grid(row=0, column=2, sticky="nswe")

btn_start_recording = Button(btn_action_frame, text="start", command=start_recording)
# btn_start_recording.place(relx=0, rely=0.5, anchor=W)
btn_start_recording.grid(row=0,column=0)

btn_stop_recording = Button(btn_action_frame, text="stop", command=stop_recording)
# btn_stop_recording.place(relx=0.2, rely=0.5, anchor=CENTER)
btn_stop_recording.grid(row=0, column=1)
# root.wm_attributes("-transparent", True)
# Set the root window background color to a transparent color
# root.config(bg='systemTransparent')
master.attributes('-topmost',True)

mainloop()
