from idlelib.pyparse import trans
from itertools import count
from tkinter import *
from PIL import Image, ImageTk, ImageFilter
import time
import os
import win32gui
import numpy as np
import imageio
import ctypes
import mss.tools
import threading
from tkinter.filedialog import asksaveasfile
from create_video import convert_png_to_mov
import cv2
import keyboard
from io import BytesIO
class theme:
    default ="orange"
    hover = "blue"
    success = "green"
    error = "red"
    warning = "orange"
    primary = "purple"
    secondray = "gray"
    active = "blue"
    white = "white"

global start_record, flag, screen_number

toggle_screens_to_choose = False
start_time_ref = False
count_frame_prev = 0
meduim_screen = 800
screen_number = 1
start_record = True
result_times = []
images_prev = []
screens = []
transperty_images=[]
frames = []
width = 400
height = 50
flag = True
gap = 20
start=0
end = 0
frame_prev_width = 0
frame_prev_height = 0
in_out_play = False
bar = None
start_px = 0
im_cursor = Image.open('arrow.png')

ctypes.windll.user32.SetProcessDPIAware()
master = Tk()
master.title("avi assistant")

full_screen = master.winfo_screenwidth()
canvas_width = width - gap

with mss.mss() as sct:
    screens = sct.monitors[1:]

master.geometry("%dx%d+%d+%d" % (width, height, (master.winfo_screenwidth() / 2) - (width / 2), 0))
master.configure(bg="#1b1f2a", bd=0)
# master.overrideredirect(True)

master.rowconfigure(0, weight=1)
master.rowconfigure(1, weight=1)
master.columnconfigure(0, weight=1)

canvas_bg = Canvas(master, width=width, height=height, bd=0)
canvas_bg.grid(row=0, column=0,padx=0, pady=0,)
canvas_bg.create_rectangle(0,0,width,height ,fill="#1b1f2a")

left_frame = Frame(master, width=canvas_width, height = height , bg="#1b1f2a", bd=0 )
left_frame.grid(row=0, column=0, sticky="nswe")
left_frame.rowconfigure(0, weight=1)
left_frame.columnconfigure(0, weight=1)
left_frame.columnconfigure(1, weight=1)
left_frame.grid_propagate(False)

btn_action_frame = Frame(left_frame, bg="#1b1f2a", bd=0, height = height, width=100 )
btn_action_frame.grid(row=0, column=0,padx=0,sticky="w", pady=0)
btn_action_frame.rowconfigure(0, weight=1)
btn_action_frame.columnconfigure(0, weight=1)
btn_action_frame.grid_propagate(False)

btn_choose_frame = Frame(left_frame, bg="#1b1f2a", bd=0, height = height, width=150)
btn_choose_frame.grid(row=0, column=1, sticky="e",padx=0, pady=0)
btn_choose_frame.rowconfigure(0, weight=1)
btn_choose_frame.columnconfigure(0, weight=1)
btn_choose_frame.grid_propagate(False)



def save_from_tkintert_images_to_video(type, images_array, save_path):
    def tkimage_to_array(tkimage):
        return np.array(tkimage)
    fourcc = ''
    if type == "avi":
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    elif type == "mov":
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    if fourcc == '':
        return print('there is no type')
    frame_size = (images_array[0].width, images_array[0].height)  # Assuming all images have the same size
    video_writer = cv2.VideoWriter(save_path, fourcc, 16, frame_size)
    for tkimage in images_array:
        np_img = tkimage_to_array(tkimage)
        bgr_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
        video_writer.write(bgr_img)
    video_writer.release()


def record_screen():
    global start_time
    print("start recording ...")
    if toggle_screens_to_choose == True:
        close_toggle_choose_screens()
    count_frame = 0
    while flag:
        im = screen_shot(index=screen_number)
        count_frame += 1
        frames.append(im)
        time.sleep((1000/16)/1000)
    else:
        end = len(frames)
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
    global toggle_screens_to_choose,left_frame, images, screen_number, start_time_ref
    if start_time_ref == True:
        close_toggle_output_edit()
        start_time_ref = False

    i = 0
    if (toggle_screens_to_choose == False):
        toggle_screens_to_choose = True
        master.geometry("%dx%d+%d+%d" % (width, height + 150, (master.winfo_screenwidth() / 2) - (width / 2), 1))
        w = 150
        frame_photo_1 = Frame(master, width =width, height=150, bg="#1b1f2a")
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
        if start_time_ref == True:
            close_toggle_choose_screens()
            start_time_ref = False

def close_toggle_choose_screens():
    global toggle_screens_to_choose, frame_photo_1
    toggle_screens_to_choose = False
    master.geometry("%dx%d+%d+%d" % (width, height, (master.winfo_screenwidth()/2) - (width/2), 0))
    frame_photo_1.grid_forget()

def close_toggle_output_edit():
    global  frame_edit,start_time_ref, width
    width = 400
    master.geometry("%dx%d+%d+%d" % (width, height, (master.winfo_screenwidth()/2) - (width/2), 0))
    # stop_video_ref()
    count_frame_prev = 0
    start_time_ref = False
    frame_edit.grid_forget()


    # .grid_forget()

def turn_px_to_fr(px, frame_len):
    global canvas_width, result_times,pps
    fps = 10
    pps = meduim_screen / fps
    sec = frame_len / fps
    time_in_sec = px * (sec / meduim_screen)
    class res:
        global pps
        fr = round(fps / (1 / time_in_sec))
        # fr = round(fps / (1/time_in_sec))
        time = time_in_sec

    result_times.append(res)
    return res

def turn_fr_to_px(fr, frames_len):

    global canvas_width, result_times, px
    fps = 10
    sec = frames_len / fps
    # print(fr * (width / sec))
    class res:
        px = round(fr * (width / sec))
    return res

def play_result():
    global frames, bar, video_out_put_label, images_prev, photo_prev_1, width_prev_1_label
    start_video_ref()

def draw_video_frame():
    global video_out_put_label,middle_frame,frames,frame_prev_height, frame_prev_width, position_mouse
    height_crop = position_mouse[3]-position_mouse[1]
    width_crop = position_mouse[2]-position_mouse[0]
    video_out_put_label = Label(middle_frame, width=width_crop, bd=0, height=height_crop, bg="#0f1012", )
    canvas_width = width -20
    canvas_height = int(frames[count_frame_prev].height / (frames[count_frame_prev].width / (width-20)))

    relx = 0
    rely = 0
    if position_mouse[0]>0:
        relx = round(1/ (canvas_width / ((canvas_width - width_crop)/2)), 1)
    if position_mouse[1]>0:
        rely = round(1/ (canvas_height / ((canvas_height - height_crop)/2)),1)
    video_out_put_label.place(relx=relx, rely=rely, anchor=NW)

def check_crop():
    canvas_crop.delete("all")
    canvas_crop.config(bg="#0f1012")
    button_check.destroy()
    draw_video_frame()
    start_video_btn()

def crop_image():
    global middle_frame,button_check, count_frame_prev,button_prev_actions, frame_prev_width, frame_prev_height, position_mouse, drag, frames,canvas_crop

    button_check = create_button(button_prev_actions, "v", "v", "orange", "white", "red", check_crop)
    button_check.place(relx=0.85, rely=0.5, anchor=W)
    button_check.bind("<Enter>", lambda e, color="red": on_hover(e, color))
    button_check.bind("<Leave>", lambda e, color="gray": on_leave(e, color))

    canvas_crop = Canvas(middle_frame, width = frame_prev_width, height=frame_prev_height, bd=0, highlightthickness=0)
    frame_resize  = frames[count_frame_prev].resize((
        width-20,
        int(frames[count_frame_prev].height / (frames[count_frame_prev].width / (width-20)))
    ))
    img = ImageTk.PhotoImage(frame_resize)
    master.one = img
    def create_transperty_rect(x1, y1, x2, y2, **kwargs):
        alpha = int(kwargs.pop("alpha") * 255)
        fill = kwargs.pop("fill")
        fill = master.winfo_rgb(fill) + (alpha,)

        image = Image.new('RGBA', (x2 - x1, y2 - y1) , fill)
        return image
    transperty_images.append(ImageTk.PhotoImage(create_transperty_rect(
        0,
        0,
        width-20,
        round(int(frames[count_frame_prev].height)/ (frames[count_frame_prev].width/(width -20))),
        fill="#000000",
        alpha=0.4
    )))

    canvas_crop.create_image((0,0), anchor=NW, image=img)
    drag= False

    def mouse_down(e):
        global position_mouse, drag
        drag = True
        x = e.x
        y = e.y
        position_mouse = [x,y,x,y]
        canvas_crop.create_image(0,0,image=transperty_images[-1], anchor='nw')
        canvas_crop. create_rectangle(x,y,x,y,outline="red", file=None)

    def create_crop_image(e):
        global transperty_images, frame_resize, count_frame_prev, frames, img2,position_mouse
        canvas_crop.create_image(0,0,image=transperty_images[-1], anchor="nw")
        frame_resize = frames[count_frame_prev].resize((width-0, int(frames[count_frame_prev].height / (frames[count_frame_prev].width / (width -20)))))
        img2 = ImageTk.PhotoImage(frame_resize.crop([position_mouse[0], position_mouse[1], e.x, e.y]))
        master.two = img2
        canvas_crop.create_image((position_mouse[0], position_mouse[1]), anchor=NW, image=img2)
        position_mouse[2] = e.x
        position_mouse[3] = e.y

    def mouse_move(e):
        global position_mouse, frame_resize, img2
        if(drag):
            canvas_crop.delete("all")
            frame_resize = frames[count_frame_prev].resize((width-0, int(frames[count_frame_prev].height / (frames[count_frame_prev].width / (width -20)))))
            img = ImageTk.PhotoImage(frame_resize.filter(ImageFilter.GaussianBlur(5)))
            master.one = img
            canvas_crop.create_image((0,0), anchor=NW, image=img)

            x = e.x
            y = e.y

            create_crop_image(e)
            canvas_crop.create_rectangle(position_mouse[0], position_mouse[1], e.x, e.y, width=4, outline="#FFFFFF", fill=None)

    def mouse_up(e):
        global position_mouse, frame_resize, img2, position_mouse, count_frame_prev, frames,drag
        drag = False
        canvas_crop.delete("all")
        frame_resize = frames[count_frame_prev].resize(
            (width - 0, int(frames[count_frame_prev].height / (frames[count_frame_prev].width / (width - 20)))))
        img = ImageTk.PhotoImage(frame_resize.filter(ImageFilter.GaussianBlur(5)))
        master.one = img
        canvas_crop.create_image((0, 0), anchor=NW, image=img)
        create_crop_image(e)
        canvas_crop.create_rectangle(position_mouse[0], position_mouse[1], e.x, e.y, width=4, outline="#FFFFFF", fill=None)

    canvas_crop.bind('<Button>',mouse_down )
    canvas_crop.bind('<Motion>', mouse_move)
    canvas_crop.bind('<ButtonRelease>',mouse_up )
    canvas_crop.place(relx=0, rely=0, anchor=NW)

def init_edit_frame():
    global toggle_screens_to_choose, side, frames, video_out_put_label, handle, C,frame_prev_height,frame_prev_width, width,top_frame,middle_frame,frame_edit,button_prev_actions,position_mouse
    if len(frames) == 0 :
        print(" there is no frame")

    width = meduim_screen
    frame_prev_width = width - 20
    frame_prev_height = int(frames[0].height / (frames[0].width / (width - 20)))
    position_mouse=[0,0,width-20,int(frames[0].height / (frames[0].width /(width-20))) ]

    toggle_screens_to_choose = True
    master.geometry("%dx%d+%d+%d" % (frame_prev_width, height + frame_prev_height + 160, (master.winfo_screenwidth()/2)-(width /2), 1))
    frame_edit = Frame(master, width =width , height=height + frame_prev_height + 100, bg="#1b1f2a", )
    frame_edit.columnconfigure(0,weight=1)
    frame_edit.rowconfigure(0,weight=1)
    frame_edit.rowconfigure(1,weight=1)
    frame_edit.rowconfigure(2,weight=1)
    frame_edit.grid(row=1, column=0, sticky="nswe")
    frame_edit.grid_propagate(False)

    top_frame = Frame(frame_edit, width=width , height=30, bg="#1b1f2a")
    top_frame.grid(row=1, column=0, sticky="nswe", padx=20)
    top_frame.columnconfigure(0, weight=1)
    top_frame.columnconfigure(1, weight=1)
    top_frame.rowconfigure(0, weight=1)
    top_frame.grid_propagate(False)

    button_prev_actions = Frame(top_frame, bg="#1b1f2a" )
    button_prev_actions.grid(row=0, column=0, sticky="nswe")
    button_prev_actions.rowconfigure(0,weight=1)
    button_prev_actions.columnconfigure(0,weight=1)
    button_prev_actions.columnconfigure(1,weight=1)
    button_prev_actions.grid_propagate(False)


    button_crop = create_button(button_prev_actions, "v", "v", "gray", "white", "red", check_crop)
    button_crop.place(relx=0.70, rely=0.5, anchor=W)
    button_crop.bind("<Enter>", lambda e, color="red": on_hover(e, color))
    button_crop.bind("<Leave>", lambda e, color="gray": on_leave(e, color))

    button_crop = create_button(button_prev_actions, "crop", "crop", "gray", "white", "red", crop_image)
    button_crop.place(relx=0.70, rely=0.5, anchor=W)
    button_crop.bind("<Enter>", lambda e, color="red": on_hover(e, color))
    button_crop.bind("<Leave>", lambda e, color="gray": on_leave(e, color))


    button_play_in_out = create_button(button_prev_actions, "in and out", "in and out", "gray", "white", "red",play_in_out_only)
    button_play_in_out.place(relx=0.45, rely=0.5, anchor=W)
    button_play_in_out.bind("<Enter>", lambda e, color="red": on_hover(e, color))
    button_play_in_out.bind("<Leave>", lambda e, color="gray": on_leave(e, color))

    button_play = create_button(button_prev_actions, "play", "play", "gray", "white", "red",start_video_btn)
    button_play.place(relx=0.30, rely=0.5, anchor=W)
    button_play.bind("<Enter>", lambda e, color="red": on_hover(e, color))
    button_play.bind("<Leave>", lambda e, color="gray": on_leave(e, color))

    button_stop = create_button(button_prev_actions, "pause", "pause", "gray", "white", "red",pause_video_ref)
    button_stop.place(relx=0.0, rely=0.5, anchor=W)
    button_stop.bind("<Enter>", lambda e, color="red": on_hover(e, color))
    button_stop.bind("<Leave>", lambda e, color="gray": on_leave(e, color))

    button_stop = create_button(button_prev_actions, "stop", "stop", "gray", "white", "red", stop_video_ref)
    button_stop.place(relx=0.15, rely=0.5, anchor=W)
    button_stop.bind("<Enter>", lambda e, color="red": on_hover(e, color))
    button_stop.bind("<Leave>", lambda e, color="gray": on_leave(e, color))

    button_save = create_button(top_frame, "save", "save", "gray", "white", "red", save_file)
    button_save.grid(row=0, column=1,  padx=10, )
    button_save.bind("<Enter>", lambda e, color="red": on_hover(e, color))
    button_save.bind("<Leave>", lambda e, color="gray": on_leave(e, color))

    middle_frame = Frame(frame_edit, width=frame_prev_width,bd=0, height=frame_prev_height, bg="#1b1f2a")
    middle_frame.grid(row=0, column=0, pady=10, padx=10)
    middle_frame.rowconfigure(0, weight=1)
    middle_frame.columnconfigure(0, weight=1)
    middle_frame.grid_propagate(False)

    bottom_frame = Frame(frame_edit, width=width, height=54, bg="#1b1f2a", bd=0)
    bottom_frame.grid(row=2,column=0, sticky="nswe", pady=20, padx=20)
    bottom_frame.columnconfigure(0, weight=1)
    bottom_frame.rowconfigure(0, weight=1)
    bottom_frame.grid_propagate(False)
    #
    # video_out_put_label = Label(middle_frame, width=frame_prev_width, height=frame_prev_height, bg="white" )
    # video_out_put_label.grid(row=0, column=0)
    # video_out_put_label.columnconfigure(1,weight=1)
    # video_out_put_label.rowconfigure(1,weight=1)
    # video_out_put_label.grid_propagate(False)
    draw_video_frame()
    C = Canvas(bottom_frame, bg="#1b1f2a", width=width-40, height=100, bd=0,  highlightthickness=0)
    C.grid(row=0, column=0, sticky="nswe")

    C.create_rectangle(0,30,width - 60, 100, fill="black")
    C.create_rectangle(0,0,width - 60, 20, fill="black")

    point = round((width -40) / (len(frames)/ 10))
    index = 0
    for _ in range(round(len(frames)/10)):
        sec = len(frames) / 10
        time_in_sec = round((point * index) * (sec / (width- 40)))
        # print(round(time_in_sec))
        def preapre_time(time):
            str = ''
            if time < 10:
                str = f'0{time}:00'
            else:
                str = f'{time}:00'
            return str
        C.create_rectangle(point * index, 0,(point * index) + 5, 20 , fill="#464646")
        C.create_text((point * index) + 5 + (point /2) ,  20/2 ,width=100, fill="#464646",text=preapre_time(time_in_sec))
        index += 1

    bar = C.create_rectangle(50,30,width - 60, 100, fill="red")
    bar_start_handle = C.create_rectangle(50,30,60, 100, fill="white")
    bar_end_handle = C.create_rectangle(width - 70,30,(width - 70) +10, 100, fill="white")



    handle = C.create_rectangle(0,0,5, 100, fill="white")

    side =""
    x1 = 0
    x2 = 0

    def on_press(e):
        global drag_trim, x1, x2, side, rs, rs_bar
        drag_trim = True
        bar_position = C.coords(bar)
        bar_x1 = bar_position[0]
        bar_x2 = bar_position[2]
        handle_pos = C.coords(handle)
        rs = 0
        rs_bar = 0
        if handle_pos[0] < e.x  and handle_pos[2] > e.x:
            rs = e.x - handle_pos[0]
            return
        if bar_x1 - 10 < e.x and bar_x1 + 10 > e.x:
            side = "start"
        elif bar_x2 -10 < e.x and bar_x2 +10 > e.x:
            side = "end"
        elif bar_x2 - 10 > e.x and bar_x1 +10 < e.x:
            side = "center"
            rs_bar = e.x -bar_x1
        else:
            side = ""

    def on_move(e):
        global drag_trim, x1, x2 ,side, rs,count_frame_prev,photo_prev_1,images_prev, frames,rs_bar
        bar_position = C.coords(bar)
        bar_x1 = bar_position[0]
        bar_y1 = bar_position[1]
        bar_x2 = bar_position[2]
        bar_y2 = bar_position[3]
        if drag_trim and rs > 0:
            C.coords(handle, e.x - rs, 0, (e.x - rs) + 10,bar_y2)

            frame_choose = turn_px_to_fr(e.x, len(frames))
            count_frame_prev = int(frame_choose.fr)
            # print(int(frames[count_frame_prev].height / (frames[count_frame_prev].width / (width - 20))))
            frame_resize = frames[count_frame_prev].resize((width - 20, int(frames[count_frame_prev].height / (frames[count_frame_prev].width / (width - 20))))).crop([position_mouse[0], position_mouse[1], position_mouse[2], position_mouse[3]])
            photo_prev_1 = ImageTk.PhotoImage(frame_resize)
            photo_prev_1_label = Label(video_out_put_label, image=photo_prev_1, bd =0)
            photo_prev_1_label.place(relx=0, rely=0, anchor=NW)
            # photo_prev_1_label.grid(row=0, column=0)
            images_prev.append(photo_prev_1)
            return

        if drag_trim:
            if side == "start":
                C.coords(bar, e.x, bar_y1, bar_x2, bar_y2)
                C.coords(bar_start_handle, e.x, bar_y1, e.x + 10, bar_y2)

                frame_choose = turn_px_to_fr(e.x, len(frames))
                count_frame_prev = int(frame_choose.fr)
                frame_resize = frames[count_frame_prev].resize((width - 20, int(frames[count_frame_prev].height / (frames[count_frame_prev].width / (width - 20))))).crop([position_mouse[0], position_mouse[1], position_mouse[2], position_mouse[3]])

                photo_prev_1 = ImageTk.PhotoImage(frame_resize)
                photo_prev_1_label = Label(video_out_put_label, image=photo_prev_1, bd=0)
                photo_prev_1_label.place(relx=0, rely=0, anchor=NW)
                # photo_prev_1_label.grid(row=0, column=0)
                images_prev.append(photo_prev_1)
            elif side == "end":
                C.coords(bar, bar_x1, bar_y1, e.x, bar_y2)
                C.coords(bar_end_handle,e.x -10, bar_y1,e.x, bar_y2)

                frame_choose = turn_px_to_fr(e.x, len(frames))
                count_frame_prev = int(frame_choose.fr)
                frame_resize = frames[count_frame_prev].resize((width - 20, int(
                    frames[count_frame_prev].height / (frames[count_frame_prev].width / (width - 20))))).crop([position_mouse[0], position_mouse[1], position_mouse[2], position_mouse[3]])

                photo_prev_1 = ImageTk.PhotoImage(frame_resize)
                photo_prev_1_label = Label(video_out_put_label, image=photo_prev_1, bd =0)
                photo_prev_1_label.place(relx=0, rely=0, anchor=NW)
                # photo_prev_1_label.grid(row=0, column=0)
                images_prev.append(photo_prev_1)
            elif side == "center":
                # rs
                C.coords(bar, e.x - rs_bar, bar_y1, (e.x - rs_bar)+ bar_x2 - bar_x1, bar_y2)
                C.coords(bar_start_handle, e.x - rs_bar, bar_y1, (e.x - rs_bar) + 10, bar_y2)
                C.coords(bar_end_handle,(e.x - rs_bar)+ bar_x2 - bar_x1, bar_y1,((e.x - rs_bar)+ bar_x2 - bar_x1)+10, bar_y2)

    def on_release(e):
        global drag_trim, frames, start, end,rs,rs_bar, start_px
        drag_trim = False
        bar_position = C.coords(bar)
        bar_x1 = bar_position[0]
        bar_x2 = bar_position[2]
        start = turn_px_to_fr(bar_x1, len(frames)).fr
        start_px = bar_x1
        end = turn_px_to_fr(bar_x2, len(frames)).fr

        # print("start",start)
        # print("end",end)
        rs = 0
        rs_bar = 0


    C.bind("<Button-1>", on_press)
    C.bind("<ButtonRelease-1>", on_release)
    C.bind("<B1-Motion>", on_move)

def start_video_ref():
    global start_time_ref, count_frame_prev, video_out_put_label, frames, C,start, end, in_out_play, length, position_mouse
    start_time_ref = True
    length = 0
    while start_time_ref:
        # print(start, end, len(frames[start:end+1]), count_frame_prev)

        if in_out_play == True:
            length = len(frames[start:end+1])
            frame_resize = frames[start:end+1][count_frame_prev].resize((width - 20, int(frames[count_frame_prev].height / (frames[count_frame_prev].width /(width-20)))))
        else:
            length = len(frames)
            frame_resize = frames[count_frame_prev].resize((width - 20, int(frames[count_frame_prev].height / (frames[count_frame_prev].width /(width-20)))))\
                .crop([position_mouse[0], position_mouse[1], position_mouse[2], position_mouse[3]])

        photo_prev_1 = ImageTk.PhotoImage(frame_resize)

        photo_prev_1_label = Label(video_out_put_label, image=photo_prev_1, bd=0)
        # print("position_mouse", position_mouse)
        # if
        # relx = 1 / ((width-20) / position_mouse[0])
        # rely = 1 / ((width-20) / position_mouse[1])
        photo_prev_1_label.place(relx=0, rely=0, anchor=NW)
        images_prev.append(photo_prev_1)
        count_frame_prev += 1

        if count_frame_prev == length:
            count_frame_prev = 0
            start_pos = 0
            if in_out_play:
                start_pos = start_px
            else:
                start_pos = 0
            C.coords(handle, start_pos,0,start_pos + 5,100)
        else:
            C.move(handle, width / (len(frames) / 10) / 10  , 0)
        time.sleep(1/10)

def pause_video_ref():
    global start_time_ref
    start_time_ref = False

def stop_video_ref():
    global start_time_ref, count_frame_prev
    ## reset the counter frame
    count_frame_prev = 0
    ## stop the video
    start_time_ref = False
    ## reset the handle
    C.coords(handle, 0, 0, 5, 100)

def play_in_out_only():
    global in_out_play, count_frame_prev,bar, start_px
    C.coords(handle, start_px, 0, start_px+ 5, 100)
    count_frame_prev = 0
    in_out_play = True
    return


def start_video_btn():
    threading.Thread(target=start_video_ref, args=()).start()

def save_file():
    global start, end,final_images,string,paths,video
    files = (
        ("Gif File", "*.gif"),
        ("Avi File", "*.avi"),
        ("Mov file", "*.mov"),
        ("All files", "*.")
    )
    filenames = asksaveasfile(filetypes=files, defaultextension="*.gif")
    # crop gif

    end_frames = []
    # print("end_frames: ",frames)

    for frame in frames:
        # convert resize
        orginal_height = frame.height
        orginal_width = frame.width

        crop_width = position_mouse[2] -position_mouse[0]
        crop_height = position_mouse[3] -position_mouse[1]

        canvas_width = width -20
        canvas_height = int(frame.height / (frame.width / (width -20)))
        divide  = (orginal_width / canvas_width)
        print(round(position_mouse[0] * divide))
        print(round(position_mouse[1] * divide))
        print(round(position_mouse[2] * divide))
        print(round(position_mouse[3] * divide))
        frame_reize = frame.crop([
            round(position_mouse[0] * divide) ,
            round(position_mouse[1] * divide),
        round(position_mouse[2] * divide),
        round(position_mouse[3] * divide)
        ])
        end_frames.append(frame_reize)

    our_path = str(filenames.name)
    paths = []
    index = 0

    def tkimage_to_array(tkimage):
        return np.array(tkimage)

    type_save = filenames.name.split("/")[-1].split(".")[-1]
    video_filename =our_path

    if type_save == "gif":
        end_frames[int(start)].save(
            our_path,
            save_all=True,
            append_images=end_frames[int(start) + 1:int(end)],
            optimize=False,
            duration=int(1000 / 100),
            loop=0)
    elif type_save == "avi":
        save_from_tkintert_images_to_video(type="avi", images_array=end_frames, save_path=video_filename)
    elif type_save == "mov":
        save_from_tkintert_images_to_video(type="mov", images_array=end_frames, save_path=video_filename)
    os.startfile("/".join(video_filename.split('/')[:-1]))
    print("/".join(video_filename.split('/')[:-1]))
    print("stop recording ...")

def on_hover(event, color):
    event.widget.configure(bg=color)

def on_leave(event,color):
    event.widget.configure(bg=color)

def on_click(event,color):
    event.widget.configure(bg=color)

images_icons = []
def create_button(widget , type, text, bg, fg, active, command):
    global image_icon,images_icons, options
    image_icon=''
    options = dict(
        cursor = "hand2",
        padx = 4,
        command = command,
        font = ("", 10),
        borderwidth = 2,
        bd = 0,
        bg = bg,
        fg = fg,
        activeforeground = active,
        activebackground = active
    )

    if type == "stop":
        image_icon = ImageTk.PhotoImage(file="icons/stop_w.png")
        options["image"]= image_icon
        options["width"]= 30
        options["height"]= 30
        # width = 30,
        #  = 30,
    elif type == "start":
        image_icon = ImageTk.PhotoImage(file="icons/record_w.png")
        options["image"]= image_icon
        options["width"] = 30
        options["height"] = 30
    elif type == "play":
        image_icon = ImageTk.PhotoImage(file="icons/play_w.png")
        options["image"]= image_icon
        options["width"] = 30
        options["height"] = 30
    elif type == 'pause':
        image_icon = ImageTk.PhotoImage(file="icons/pause_w.png")
        options["image"] = image_icon
        options["width"] = 30
        options["height"] = 30
    elif type == "crop":
        image_icon = ImageTk.PhotoImage(file="icons/crop_w.png")
        options["image"] = image_icon
        options["width"] = 30
        options["height"] = 30
    else:
        options["text"] = text

    images_icons.append(image_icon)
    return Button(widget,**options)

btn_choose_screen = create_button(btn_choose_frame, "choose", "choose screen", "gray", "white", "red", choose_screen)
btn_choose_screen.grid(row=0, column=0, sticky="e", padx=10)

btn_choose_screen.bind("<Enter>" , lambda e,color="red": on_hover(e,color))
btn_choose_screen.bind("<Leave>", lambda e,color="gray": on_leave(e,color))

btn_start_recording = create_button(btn_action_frame, "start", "start", "gray", "white", "red", start_recording)
btn_start_recording.bind("<Enter>",  lambda e,color="red": on_hover(e,color))
btn_start_recording.bind("<Leave>", lambda e,color="gray": on_leave(e,color))
btn_start_recording.grid(row=0, column=0)

btn_stop_recording = create_button(btn_action_frame, "stop", "stop", "gray", "white", "red", stop_recording)
btn_stop_recording.bind("<Enter>",  lambda e,color="red": on_hover(e,color))
btn_stop_recording.bind("<Leave>", lambda e,color="gray": on_leave(e,color))
btn_stop_recording.grid(row=0, column=1)

## add listener keyboard

# master.attributes('-topmost',True)
mainloop()
