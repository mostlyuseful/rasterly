import pretty_errors
from functools import partial
from array import array
import itertools
import sys
import tkinter
import tkinter.filedialog
import numpy as np
from pathlib import Path
from PIL import Image, ImageTk
from time import sleep
from numpy.lib.type_check import imag
from pymouse import PyMouse


def extract_chords(data):
    cols = np.nonzero(data)[0]
    if len(cols) == 0:
        return []
    chords = []

    start_col = cols[0]
    end_col = cols[0]
    for col in cols:
        if col > (end_col + 1):
            chords.append((start_col, end_col))
            start_col = col
            end_col = start_col
        else:
            end_col = col
    chords.append((start_col, end_col))
    return chords


def playback(binary_image, scale, tx, ty, sleep_duration_per_chord=0.02):
    m = PyMouse()
    for row_idx, row_data in enumerate(binary_image):
        y = int((scale * row_idx) + ty)
        chords = extract_chords(row_data)
        for c0, c1 in chords:
            x0 = int((scale * c0) + tx)
            x1 = int((scale * c1) + tx)
            m.move(x0, y)
            m.drag(x1, y)
        sleep(sleep_duration_per_chord * len(chords))

    


def on_quantize_click():
    global im, qnt, num_colors_entry, qnt_lbl
    num_colors = int(num_colors_entry.get())
    qnt = im.quantize(num_colors, kmeans=1)
    qnt_photo = ImageTk.PhotoImage(qnt)
    qnt_lbl.config(image=qnt_photo)
    qnt_lbl.image = qnt_photo

    populate_playback_buttons()


def split_seq(iterable, size):
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))


def populate_playback_buttons():
    global frame_playback_buttons, qnt
    for child in frame_playback_buttons.winfo_children():
        child.destroy()

    q = np.asarray(qnt)
    num_colors = q.max() + 1
    pal = array("B", qnt.palette.tobytes())
    colors = list(split_seq(pal, 3))[:num_colors]

    for i, color in enumerate(colors):
        r, g, b = color
        bg_color = f"#{r:02x}{g:02x}{b:02x}"
        fg_color = f"#{255-r:02x}{255-g:02x}{255-b:02x}"
        btn = tkinter.Button(
            frame_playback_buttons,
            text=f"{bg_color}",
            command=partial(playback_layer, i),
            background=bg_color,
            foreground=fg_color,
        )
        btn.pack(side=tkinter.LEFT, padx=5, pady=5)


def playback_layer(layer_idx):
    print(layer_idx)
    global qnt, tx_entry, ty_entry, scale_entry

    q = np.asarray(qnt)
    bin_layer = q == layer_idx

    scale = float(scale_entry.get())
    tx = int(tx_entry.get())
    ty = int(ty_entry.get())

    playback(bin_layer, scale, tx, ty)


def on_preview_click():
    global tx_entry, ty_entry, scale_entry, qnt
    m = PyMouse()
    old_pos = m.position()

    tx = int(tx_entry.get())
    ty = int(ty_entry.get())
    scale = float(scale_entry.get())

    w = qnt.width
    h = qnt.height

    xx = [tx, w * scale + tx, w * scale + tx, tx, tx]
    yy = [ty, ty, h * scale + ty, h * scale + ty, ty]
    m.move(int(xx[0]), int(yy[0]))
    for x, y in zip(xx, yy):
        m.move(int(x), int(y))
        sleep(0.5)

    m.move(*old_pos)


if __name__ == "__main__":
    mainwin = tkinter.Tk()

    if len(sys.argv) == 2:
        image_path = sys.argv[1]
    else:
        script_dir = str(Path(__file__).parent.absolute())
        image_path = tkinter.filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("All files", "*.*")],
            initialdir=script_dir,
        )
        if not image_path:
            sys.exit(1)
    im = Image.open(image_path)
    qnt = im.convert("P")

    ###

    frame1 = tkinter.Frame(mainwin)
    frame1.pack(fill=tkinter.X)

    lbl1 = tkinter.Label(frame1, text="# colors", width=6)
    lbl1.pack(side=tkinter.LEFT, padx=5, pady=5)

    num_colors_entry = tkinter.Entry(frame1)
    num_colors_entry.delete(0, tkinter.END)
    num_colors_entry.insert(0, "4")
    num_colors_entry.pack(fill=tkinter.X, padx=5, expand=True)

    ###

    quantize_btn = tkinter.Button(mainwin, text="Quantize", command=on_quantize_click)
    quantize_btn.pack(fill=tkinter.X)

    ###

    frame4 = tkinter.Frame(mainwin)
    frame4.pack(fill=tkinter.X)

    src_photo = ImageTk.PhotoImage(im)
    image_lbl = tkinter.Label(frame4, image=src_photo)
    image_lbl.image = src_photo
    image_lbl.pack(side=tkinter.LEFT, padx=5, pady=5)

    qnt_photo = ImageTk.PhotoImage(qnt)
    qnt_lbl = tkinter.Label(frame4, image=qnt_photo)
    qnt_lbl.image = qnt_photo
    qnt_lbl.pack(side=tkinter.RIGHT, padx=5, pady=5)

    ###

    frame2 = tkinter.Frame(mainwin)
    frame2.pack(fill=tkinter.X)

    lbl2 = tkinter.Label(frame2, text="tx", width=6)
    lbl2.pack(side=tkinter.LEFT, padx=5, pady=5)

    tx_entry = tkinter.Entry(frame2)
    tx_entry.delete(0, tkinter.END)
    tx_entry.insert(0, "300")
    tx_entry.pack(fill=tkinter.X, padx=5, expand=True)

    ###

    frame3 = tkinter.Frame(mainwin)
    frame3.pack(fill=tkinter.X)

    lbl3 = tkinter.Label(frame3, text="ty", width=6)
    lbl3.pack(side=tkinter.LEFT, padx=5, pady=5)

    ty_entry = tkinter.Entry(frame3)
    ty_entry.delete(0, tkinter.END)
    ty_entry.insert(0, "200")
    ty_entry.pack(fill=tkinter.X, padx=5, expand=True)

    ###

    frame = tkinter.Frame(mainwin)
    frame.pack(fill=tkinter.X)

    lbl3 = tkinter.Label(frame, text="scale", width=6)
    lbl3.pack(side=tkinter.LEFT, padx=5, pady=5)

    scale_entry = tkinter.Entry(frame)
    scale_entry.delete(0, tkinter.END)
    scale_entry.insert(0, "1.0")
    scale_entry.pack(fill=tkinter.X, padx=5, expand=True)

    ###

    preview_btn = tkinter.Button(mainwin, text="Preview ROI", command=on_preview_click)
    preview_btn.pack(fill=tkinter.X)

    ###

    frame_playback_buttons = tkinter.Frame(mainwin)
    frame_playback_buttons.pack(fill=tkinter.BOTH)

    # ty, image previews, btn quantize, btn preview roi, btn playback

    # lbl = tkinter.Label(mainwin, text="Hello", background="#ff0000")
    # lbl.pack()

    on_quantize_click()
    mainwin.mainloop()


if False:
    tx, ty = 300, 300
    scale = 2.0
    im = Image.open("kawaii.jpg")
    q = im.quantize(4)
    a = np.asarray(q)

    sleep(1)
    layer = a == 4
    playback(layer, scale, tx, ty)
