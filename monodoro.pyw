from tkinter import *
from tkinter import ttk

from PIL import ImageTk
import platform
import threading
import queue as Queue
import sqlite3
import argparse
import datetime
import time
import atexit
import pygame
import config
import os
import ctypes

import importlib
dk = importlib.__import__('dkinter')

settings = config.config()

#   store some stuff for win api interaction
set_to_foreground = ctypes.windll.user32.SetForegroundWindow
keybd_event = ctypes.windll.user32.keybd_event
alt_key = 0x12
extended_key = 0x0001
key_up = 0x0002

BREAK_DURATION = settings['BREAK_DURATION']
SLOT_DURATION = settings['SLOT_DURATION']
__LIVE__ = settings['LIVE'] is True
SOUND_FILE = './cartoon-telephone_daniel_simion.mp3'


@atexit.register
def shutdown():
    os.system("shutdown /a")

    if __LIVE__ is True:
        os.system("shutdown /s /f /t 0")
    else:
        os.system("shutdown /s /t 3600")

    print('KILL-SIGNAL')

class ThreadedTask(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.kill = False

        pygame.mixer.init()
        pygame.mixer.music.load(SOUND_FILE)

    def run(self):
        n = 0

        while not self.kill:
            #print("TEST")
            time.sleep(0.2)
            msg = None

            now = datetime.datetime.now()
            mins = 60 * now.hour + now.minute
            lateMark = 22 * 60 + 5
            earlyMark = 5 * 60 + 35
            if (mins >= lateMark) or (earlyMark >= mins):
                print("BAD HOURS TO BE AWAKE")
                self.kill = True
                shutdown()

            try:
                msg = self.queue.get(0)
                print("MSG", msg)
            except Queue.Empty:
                n += 1
                print("SASD", n)
                pass

            if msg == 'DIE':
                pygame.mixer.music.stop()
                print("DIE")
                self.kill = True

            elif msg == 'play':
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(loops=-1)

            elif msg is not None:
                pygame.mixer.music.stop()

class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect('data/data.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pomodoros (
                ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                start UNSIGNED BIGINT,
                end UNSIGNED BIGINT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reasons (
                ID INT NOT NULL,
                reason TEXT,
                
                CONSTRAINT fk_column 
                FOREIGN KEY (ID) 
                REFERENCES pomodoros(ID)
            )
        """)

        self.conn.commit()

    def getLatest(self):
        self.cursor.execute("""
            SELECT end, reason as reason
            FROM pomodoros JOIN reasons USING (ID)
            ORDER BY end DESC
            LIMIT 1
        """)

        row = self.cursor.fetchone()
        if row is None:
            return -1, ""

        return int(row[0]), row[1]

    def addNewSlot(self, start, end, reason):
        self.cursor.execute("""
            INSERT INTO pomodoros (start, end)
            VALUES (?, ?)
        """, (start, end))

        self.conn.commit()
        self.insertReason(end, reason)

    def insertReason(self, endTime, reason, commit=True):
        self.cursor.execute("""
            INSERT INTO reasons (ID, reason)
            VALUES ((
                SELECT ID 
                FROM pomodoros 
                WHERE end = ?
                LIMIT 1
            ), ?)
        """, (endTime, reason))

        if commit:
            self.conn.commit()

def pad(text, length, fill="0", left=True):
    padding = (length - len(text)) * fill
    newText = padding + text if left else text + padding
    return newText

def formatSecs(diff):
    mins = pad(str(diff // 60), 2)
    secs = pad(str(diff % 60), 2)
    return "%s:%s" % (mins, secs)


class MododoroApp(dk.PlusFrame):
    MSG_BUISNESS = "State your buisness."
    MSG_BREAK = "Break time"
    MSG_PROGRESS = "Pomodoro in progress."
    STATE_READY = "ready"
    STATE_ONGOING = "ongoing"
    STATE_BREAK = "break"
    STATE_RINGING = "ringing"

    PADX = 20
    PADY = 20

    def __init__(self, master):
        dk.PlusFrame.__init__(self, master, bindScroll=True)
        self['bg'] = 'white'
        self.master['bg'] = 'white'
        self.db = Database()

        # self.configData = config.config()
        # self.txtHistory = txtHistory.History()
        # self.onScroll = self.onMouseWheel
        self.state = __class__.STATE_READY
        self.insertTime = None
        self.end = -1

        self.queue = Queue.Queue()
        self.thread = ThreadedTask(self.queue)
        self.thread.start()
        #self.queue.put('play')
        #print("play")

        self.make()
        self.recur()
        self.bind("<Destroy>", self.onDestroy)
        self.master.protocol('WM_DELETE_WINDOW', self.shutdown)
        self.enableFullScreen()
        self.center()

        self.pack(
            padx=__class__.PADX,
            pady=__class__.PADY,
            side=TOP,
            expand=YES
        )

    def steal_focus(self):
        keybd_event(alt_key, 0, extended_key | 0, 0)
        set_to_foreground(self.master.winfo_id())
        keybd_event(alt_key, 0, extended_key | key_up, 0)

    def enableFullScreen(self):
        self.master.attributes("-fullscreen", True)
    def disableFullScreen(self):
        self.master.attributes("-fullscreen", False)

    def onDestroy(self, *args):
        print("DESTROY")

    def shutdown(self, *args):
        # os.system("shutdown /s /t 0")
        self.queue.put('DIE')
        print("SHUTDOWN")
        shutdown()
        #pass


    def updateState(self):
        timeNow = int(time.time())
        newState = self.state
        fullscreen = False

        if self.end >= timeNow > 0:
            newState = __class__.STATE_ONGOING

            # pomodoro in progress
            diff = self.end - timeNow
            self.promptLabel.config(text=__class__.MSG_PROGRESS)
            self.timeLabel.config(text=formatSecs(diff))
            self.comments.config(state='disabled')

        elif self.end + BREAK_DURATION >= timeNow >= self.end:
            newState = __class__.STATE_BREAK

            # pomodoro over, break in progress
            diff = self.end + BREAK_DURATION - timeNow
            self.promptLabel.config(text=__class__.MSG_BREAK)
            self.timeLabel.config(text=formatSecs(diff))
            self.comments.config(state='disabled')
            ctypes.windll.user32.LockWorkStation()
            fullscreen = True

        elif self.state == __class__.STATE_BREAK:
            newState = __class__.STATE_RINGING
            self.comments.delete('1.0', 'end')
            # ringing, waiting for user to acknowledge
            # that break is over
            self.queue.put('play')
            fullscreen = True

        elif self.state == __class__.STATE_RINGING:
            self.submitBttn.config(text="Stop Alarm")
            fullscreen = True

        else:
            # nothing going on
            # self.queue.put('stop')
            newState = __class__.STATE_READY
            self.promptLabel.config(text=__class__.MSG_BUISNESS)
            self.timeLabel.config(text="--:--")
            self.comments.config(state='normal')
            fullscreen = True

        if fullscreen:
            self.enableFullScreen()
            if (self.state != newState) or __LIVE__:
                self.steal_focus()
                self.master.attributes("-topmost", True)

        else:
            self.disableFullScreen()
            if (self.state != newState) or __LIVE__:
                self.master.attributes("-topmost", False)

        self.state = newState


    def recur(self):
        self.updateState()
        self.after(250, self.recur)

    def make(self):
        """
        self.grip = Label(self, bg="grey32")
        self.grip.grid(row=0, column=0, sticky="nw")
        self.grip.bind("<ButtonPress-1>", self.StartMove)
        self.grip.bind("<ButtonRelease-1>", self.StopMove)
        self.grip.bind("<B1-Motion>", self.OnMotion)
        self.grip.grid(sticky='ew', row=0, column=100)
        """

        self.promptLabel = Label(
            self, text=__class__.MSG_BUISNESS,
            background='white', relief='flat'
            , font=('Ubuntu', 14), fg='grey32',
            highlightcolor='white'
        )
        self.promptLabel.grid(
            row=100, column=100, pady=(14, 0), sticky='ew'
        )

        self.commentWrapper = Frame(self, bg='white')
        self.commentBox = Frame(self.commentWrapper, bg='grey82')
        self.commentWhite = Frame(self.commentBox, bg='white')
        self.comments = Text(
            self.commentWhite, width=20, height=3, bd=2
            , background='white', relief='flat'
            , font=('Ubuntu', 14), fg='grey32', highlightcolor='white'
            , selectbackground='grey32'
        )
        self.comments.grid(
            row=100, column=100, padx=3, pady=3, sticky='nsew'
        )
        # self.rowconfigure(100, weight=1)
        # self.commentBox.columnconfigure(100, weight=1)

        self.commentWhite.grid(
            padx=2, pady=2, row=100, column=100, sticky='nsew'
        )
        self.commentBox.grid(row=100, column=100, sticky='ew')
        self.commentWrapper.columnconfigure(100, weight=1)
        self.commentBox.columnconfigure(100, weight=1)
        self.commentWhite.columnconfigure(100, weight=1)

        self.scrollComment = ttk.Scrollbar(
            self.commentWrapper, command=self.comments.yview
        )
        self.comments.config(
            yscrollcommand=self.scrollComment.set
        )
        self.scrollComment.grid(
            row=100, column=200, sticky='nse'
            , padx=(10, 0)
        )
        self.commentWrapper.grid(
            row=300, column=100, pady=(14, 0), sticky='ew'
        )

        self.submitBttn = dk.Button(
            self, font=('Ubuntu', 14), fg='white'
            , highlightcolor='white', bg='grey32'
            , hoverBg='#1b9eea', pressBg='#417aeb'
            , text='Submit'

            , onRelease=self.submit
        )
        self.submitBttn.grid(
            row=400, column=100, pady=(14,0), ipady=5, ipadx=16 #, sticky='ew'
        )

        self.timeLabel = Label(
            self, text="12:34", background='white', relief='flat'
            , font=('Ubuntu', 14), fg='grey32', highlightcolor='white'
        )
        self.timeLabel.grid(
            row=500, column=100, pady=(14, 0), sticky='ew'
        )

        end, reason = self.db.getLatest()
        self.comments.delete('1.0', 'end')
        if end > int(time.time()):
            self.comments.insert('end', reason)

        self.end = end

    def submit(self, *args):
        reason = self.comments.get("1.0", END)
        timeNow = int(time.time())

        if self.state == __class__.STATE_READY:
            self.end = timeNow + SLOT_DURATION
            self.db.addNewSlot(timeNow, self.end, reason)
            self.state = __class__.STATE_ONGOING
            self.updateState()

        elif self.state == __class__.STATE_ONGOING:
            self.db.insertReason(self.end, reason)
            self.updateState()

        elif self.state == __class__.STATE_RINGING:
            self.submitBttn.config(text="Submit")
            self.queue.put('stop')
            self.state = __class__.STATE_READY
            self.updateState()


    def setMain(self):
        self.topline = Frame(self, height=2, bg='grey96')
        self.topline.grid(
            row=0, column=100, columnspan=1000, sticky='ew'
        )

        #self.graph.onMasterHover = self.onCnvEnter
        #self.graph.onMasterClick = self.onCnvPress

        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky='nsew')

        self.update()
        self.master.minsize(1000, self.winfo_height())

        try:
            self.master.state('zoomed')
        except TclError:
            self.master.attributes('-zoomed', True)

    def StartMove(self, event):
        self.x = __class__.PADX + event.x
        self.y = __class__.PADY + event.y

    def StopMove(self, event):
        self.x = None
        self.y = None

    def OnMotion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + __class__.PADX + deltax
        y = self.winfo_y() + __class__.PADY + deltay

        x = event.x_root + __class__.PADX
        y = event.y_root + __class__.PADY
        self.master.geometry(
            "+%s+%s" % (x, y)
        )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force", help="force shutdowns",
        action="store_true"
    )
    args = parser.parse_args()

    if args.force:
        __LIVE__ = True

    root = Tk()
    root.title('Monodoro v0.01')
    root = MododoroApp(root)
    # root.setMain()
    # root.grid()

    root.mainloop()
