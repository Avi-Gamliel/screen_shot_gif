from tkinter import *
from PIL import Image , ImageTk
import time
import win32gui
import ctypes
import mss.tools
import threading

ctypes.windll.user32.SetProcessDPIAware()

global start_record, flag, screen_number
start_record = True
im_cursor = Image.open('arrow.png')
master = Tk()
master.title("avi assistant")

width = 400
height = 50
toggle_screens_to_choose = False

master.geometry("%dx%d+%d+%d" % (width, height, (master.winfo_screenwidth() / 2) - (width / 2), 0))
master.configure(bg="skyblue")
master.overrideredirect(True)

left_frame = Frame(master, width=width - 20, height=height - 20, bg="white", bd=0.5)
left_frame.grid(row=0, column=3, padx=10, pady=10)

flag = True
frames = []
screen_number = 1


def stop_recording():
    global flag
    flag = False


def record_screen():
    print("start recording ...")
    while flag:
        # logic here
        im = screen_shot(index=screen_number)
        frames.append(im)
        time.sleep(1 / 10)
        print("ok")
    else:
        frames[0].save(
            "sample.gif",
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=int(1000 / 100),
            loop=0)
        print("stop recording ...")


def start_recording():
    global flag
    flag = True
    threading.Thread(target=record_screen, args=()).start()

def get_image_bytes(index=1):
    with mss.mss() as sct:
        monitor_number = int(index)
        mon = sct.monitors[1:][monitor_number - 1]
        monitor = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"],
            "height": mon["height"]
        }
        sct_img = sct.grab(monitor)
        return sct_img


def screen_shot(index=1):
    global im
    bytes_image = get_image_bytes(index=index)
    curX, curY = win32gui.GetCursorPos()
    im = Image.frombytes("RGB", bytes_image.size, bytes_image.bgra, "raw", "BGRX").convert("RGBA")
    im.paste(im_cursor, box=(curX, curY), mask=im_cursor)
    return im


def choose_screen():
    global toggle_screens_to_choose,photo_1,left_frame
    if (toggle_screens_to_choose == False):
        toggle_screens_to_choose = True
        master.geometry("%dx%d+%d+%d" % (width, height + 150, (master.winfo_screenwidth() / 2) - (width / 2), 1))
        screen_1 = screen_shot(index=1)
        w = 150

        # SCREEN 1 - NEED the second monitor
        screen_index=0
        frame_photo_1 = Frame(master,width=width, height=150, bg="yellow")
        frame_photo_1.place(relx=0, rely=1, anchor=SW)
        screen_1_resize = screen_1.resize((w, int(screen_1.height / (screen_1.width / w))))
        screen_1_resize.save(f'temp/{"1"}.png')
        spddlt = "\\".join(str(__file__).split("\\")[:-1])
        print(f'{spddlt}\\temp\\1.png')
        photo_1 = ImageTk.PhotoImage(Image.open(f'{spddlt}\\temp\\{screen_index+1}.png'))
        print(photo_1)
        photo_1_label = Label(frame_photo_1, image=photo_1)
        def mouse_up(e):
            global screen_number
            screen_number = screen_index + 1

        photo_1_label.bind('<ButtonRelease>', mouse_up)
        photo_1_label.place(relx=0, rely=0.5, anchor=W)
    else:
        toggle_screens_to_choose = False
        master.geometry("%dx%d+%d+%d" % (width, height, (master.winfo_screenwidth() / 2) - (width / 2), 0))
    return


# ignore shrink default frame
left_frame.grid_propagate(False)

# create buttons
btn_choose_screen = Button(left_frame, text="choose screen", command=choose_screen)
btn_choose_screen.place(relx=1, rely=0.5, anchor=E)

btn_start_recording = Button(left_frame, text="start", command=start_recording)
btn_start_recording.place(relx=0, rely=0.5, anchor=W)

btn_stop_recording = Button(left_frame, text="stop", command=stop_recording)
btn_stop_recording.place(relx=0.2, rely=0.5, anchor=CENTER)

mainloop()
