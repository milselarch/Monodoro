from tkinter import *
from tkinter import ttk
import copy

"""
ability to append callback before colour change?
"""
print('DKINTER 2-05')

def dropbox(url):
    url = url.replace(
        'www.dropbox.com'
        ,'dl.dropboxusercontent.com'
        )
    return(url)

class Button(Frame):
    ID = 0
    tagNames = []
    
    def __init__(self,master,**kwargs):
        Frame.__init__(self,master)
        self.Frame = Frame

        self.holder = Frame(
            self,bd=0,highlightthickness=0
            )
        self.holder.grid(row=100,column=100,sticky='nsew')
        self.holder.rowconfigure(100,weight=1)
        self.holder.columnconfigure(100,weight=1)
        
        self.dkType = 'dk.Bttn'
        self.tagName = "%s:%s" % (self.dkType, str(self.ID))

        while self.tagName in self.tagNames:
            type(self).ID += 1
            self.tagName = "%s:%s" % (self.dkType, str(self.ID))

        self.tagNames.append(self.tagName)
        
        self.default = {
            'text':None
            ,'bg':None #'white'
            ,'fg':None #'grey22'
            ,'hoverBg':None
            ,'hoverFg':None
            ,'pressBg':None
            ,'pressFg':None
            #,'font':('calibri',13,'normal')
            ,'highlightthickness': 0
            ,'highlightbackground': None
            }
        """
        for item in kwargs:
            if item not in default:
                raise IndexError(item)
        """

        self.border = 0
        self.borderColor = None
        #self.passive = False

        self.pressed = False
        self.hovered = False

        self.onPress = lambda x:None
        self.onRelease = lambda x:None
        self.onEnter = lambda x:None
        self.onLeave = lambda x:None
        
        self.enable = True

        #self['bg'] = kwargs['bg']
        self.kwargs = kwargs
        #print(kwargs)

        for item in self.default:
            if item not in self.kwargs:
                self.kwargs[item] = self.default[item]
                
        self.make()
        self.grid()

    def enableEventCll(self):
        self.enable = True
    def disableEventCll(self):
        self.enable = False
    
    def bind(self,event,func):
        #print('BINDED',event,func)
        if event == '<ButtonPress-1>':
            self.onPress = func
        elif event == '<ButtonRelease-1>':
            self.onRelease = func
        elif event == '<Enter>':
            self.onEnter = func
        elif event == '<Leave>':
            self.onLeave = func
        else:
            #print('OTHEREVENT')
            self.bind_class(self.tagName,event,func)

    def make(self):
        self.lbl = Label(self.holder)
            
        """
        self.lbl = Label(
            self,text=self.kwargs['text']
            ,bg=self.kwargs['bg']
            )
        
        tags = self.lbl.bindtags()
        self.lbl.bindtags(tags+(self.tagName,))
        tags = self.bindtags()
        self.bindtags(tags+(self.tagName,))
        """
        self.addTag(self)
        self.addTag(self.lbl)
        self.addTag(self.holder)

        self.bind_class(self.tagName,'<ButtonPress-1>',self._press)
        self.bind_class(self.tagName,'<ButtonRelease-1>',self._release)
        self.bind_class(self.tagName, '<Enter>', self._enter)
        self.bind_class(self.tagName, '<Leave>', self._leave)
        #super(self.__class__,self).bind('<Enter>',self._enter)
        #super(self.__class__,self).bind('<Leave>',self._leave)

        self.config(**self.kwargs)

    def addTag(self, widget):
        tags = widget.bindtags()
        widget.bindtags(tags+(self.tagName,))
        
    def config(self,*args,**kwargs):
        #print('SELFKWARGS',self.kwargs)
        #kwargs = copy.copy(kwargs)
        for item in self.default:
            if item not in kwargs:
                if item in self.kwargs:
                    kwargs[item] = self.kwargs[item]
                else:
                    kwargs[item] = self.default[item]

        #print('FILL OLD KWARGS',kwargs)
        self.kwargs = copy.copy(kwargs)
        """
        self.kwargs copy is done here so that
        any unspecified args remain that way

        e.g. if you set self.kwargs['pressBg'] from None
        to kwargs['bg'], later on explicitly specifying bg
        will not result pressBg to follow suit, which is not
        expected button behavior

        so non specified arguments are left empty in self.kwargs
        but are filled in kwargs which get passed on to config
        """

        if kwargs['bg'] == None:
            label = Label(self)
            bg = self.cget('bg')
            #print(bg,"BELIgirENT")
            kwargs['bg'] = bg

        if kwargs['hoverBg'] == None:
            kwargs['hoverBg'] = kwargs['bg']
        if kwargs['hoverFg'] == None:
            kwargs['hoverFg'] = kwargs['fg']
        if kwargs['pressBg'] == None:
            kwargs['pressBg'] = kwargs['bg']
        if kwargs['pressFg'] == None:
            kwargs['pressFg'] = kwargs['fg']

        #print('FILL REMAINDER',kwargs)

        self.hoverBg = kwargs['hoverBg']
        self.hoverFg = kwargs['hoverFg']
        self.pressFg = kwargs['pressFg']
        self.pressBg = kwargs['pressBg']

        self.border = kwargs['highlightthickness']
        del kwargs['highlightthickness']
        self.borderColor = kwargs['highlightbackground']
        del kwargs['highlightbackground']

        if 'onPress' in kwargs:
            self.onPress = kwargs['onPress']
            del kwargs['onPress']
        if 'onRelease' in kwargs:
            self.onRelease = kwargs['onRelease']
            del kwargs['onRelease']
        if 'onEnter' in kwargs:
            self.onEnter = kwargs['onEnter']
            del kwargs['onEnter']
        if 'onLeave' in kwargs:
            self.onLeave = kwargs['onLeave']
            del kwargs['onLeave']

        del kwargs['hoverBg']
        del kwargs['hoverFg']
        del kwargs['pressBg']
        del kwargs['pressFg']
        #print(kwargs)

        #print(self.pressed,self.hovered)
        if self.pressed == True:
            kwargs['bg'] = self.pressBg
            kwargs['fg'] = self.pressFg
        elif self.hovered == True:
            kwargs['bg'] = self.hoverBg
            kwargs['fg'] = self.hoverFg

        #print(self.kwargs,kwargs)
        self.lbl.config(*args,**kwargs)
        self.holder.config(bg=kwargs['bg'])

        self['bg'] = self.borderColor
        self.holder.grid(
            row=100,column=100,sticky='nsew',
            padx=self.border,pady=self.border
            )

    def _press(self,event):
        self.pressed = True
        self.configColour(self.pressBg,self.pressFg)
        #print('PRESSED',self.pressed,self.hovered)
        event = self.configEvent(event)
        self.onPress(event)
            
    def _release(self,event):
        self.pressed = False
        #print('RELEASED',self.pressed,self.hovered)
        if self.hovered == False:
            #print('CHEAK FAlSE')
            self.configColour(self.kwargs['bg'],self.kwargs['fg'])
        else:
            #print('CHEAK TRUE')
            self.configColour(self.hoverBg,self.hoverFg)

        event = self.configEvent(event)
        self.onRelease(event)
            
    def _leave(self,event):
        self.hovered = False
        #print('LEAVE',self.pressed,self.hovered)
        if self.pressed == False:
            self.configColour(self.kwargs['bg'],self.kwargs['fg'])
        event = self.configEvent(event)
        self.onLeave(event)
        
    def _enter(self,event):
        self.hovered = True
        #print('ENTER',self.pressed,self.hovered)
        if self.pressed == False:
            self.configColour(self.hoverBg,self.hoverFg)
        event = self.configEvent(event)
        self.onEnter(event)

    def configEvent(self,event):
        event.widget = self
        return(event)

    def configColour(self,bg,fg):
        if self.enable == True:
            #print('CONFIGURING COLOUR')
            self.lbl.config(bg=bg,fg=fg)
            self.holder.config(bg=bg)
            #self['bg'] = bg
        #self.update_idletasks()

    def grid(self,*args,**kwargs):
        #print('INITIING')
        frmKwargs = copy.deepcopy(kwargs)
        
        itemList = list(frmKwargs)
        for item in itemList:
            if item in ['ipadx','ipady']:
                del frmKwargs[item]

        #print(frmKwargs)
        self.Frame.grid(self,*args,**frmKwargs)

        itemList = list(kwargs)
        for item in itemList:
            if item in ['padx','pady','row','column']:
                del kwargs[item]

        itemList = list(kwargs)
        for item in itemList:
            if item in ['ipadx','ipady']:
                kwargs[item[1:]] = kwargs[item]
                del kwargs[item]
            else:
                del kwargs[item]

        #print(kwargs)
        self.lbl.grid(kwargs)
        self.lbl.grid(row=100,column=100)
        self.holder.rowconfigure(100,weight=1)
        self.holder.columnconfigure(100,weight=1)
        self.rowconfigure(100,weight=1)
        self.columnconfigure(100,weight=1)

    def getText(self):
        return self.lbl.cget("text")

class PlusFrame(Frame):
    def __init__(self,master,bindScroll=False):
        Frame.__init__(self,master)
        if bindScroll == True:
            self.bindScroll()
            
        self.grid()

    def bindScroll(self):
        self.onScroll = lambda x:None
        self.bind_all("<MouseWheel>", self.scrollHandler)
        super().bind_all("<MouseWheel>", self.scrollHandler)
        
    def center(self):
        self.update_idletasks()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        size = tuple(
            int(a) for a in self.master.geometry()
            .split('+')[0].split('x')
            )
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        self.master.geometry("+%d+%d"%(x,y))

    def addTag(self,widget,tagName):
        tags = widget.bindtags()
        assert(tagName not in tags)
        widget.bindtags(tags+(tagName,))

    def scrollHandler(self,event,*args,**kwargs):
        #print(type(self).__name__)
        #print(self.onScroll)
        self.onScroll(event,*args,**kwargs)

    def grid(self,*args,**kwargs):
        super().grid(*args,**kwargs)

    def pack(self,*args,**kwargs):
        super().pack(*args,**kwargs)

    def makeTestFrame(self):
        test = Toplevel(self)
        w, h = test.winfo_screenwidth(), test.winfo_screenheight()
        test.overrideredirect(1)
        test.geometry("%dx%d+0+0" % (w,h))
    
        test.withdraw()
        return(test)

class WidgetList(PlusFrame):
    ID = 0
    
    def __init__(self,master):
        PlusFrame.__init__(self,master)
        self['bg'] = 'white'

        self.WidLabel = WidLabelMaker.makeWidLabel()
        self.widgetCount = lambda: 0
        self.defaultWidget = lambda: None
        self.passive = False

        self.master.onScroll = self.onMouseWheel
        self.initialHeight = 266

        self.enableScroll = True
        self.pressed = False #person 'option' pressed
        self.entered = False #person 'option' entered

        self.bind('<Enter>',self.enter)
        self.bind('<Leave>',self.leave)

        self.dkType = 'dk.WidgetList'
        self.tagName = self.dkType+':'+str(self.ID)
        type(self).ID += 1
        
        self.make()
        self.grid(padx=(25,0))

    def make(self):
        self.makeFrames()        
        self.lift(self.scrolly)
        self.scrolly.grid()
        print('SCROLL ALR SET')

    def exists(self,name):
        #print('EXISTS VARLIST',self.WidLabel.exists(name))
        return(self.WidLabel.exists(name))

    def acquire(self,nameOrFrame):
        return(self.WidLabel.acquire(nameOrFrame))

    def acqWidgetList(self):
        return(self.WidLabel.acqWidgetList())

    def acqWidgetDict(self):
        return(self.WidLabel.acqWidgetDict())

    def enter(self,event):
        self.entered = True
    def leave(self,event):
        self.entered = False

    def fillCnvHeight(self):
        if len(WidLabel.widgets) == 0:
            test = self.makeTestFrame()
            
            wrapFrame = Frame(test)
            wrapFrame.grid()
            pplFrame = self.makeWidLbl(wrapFrame)
            test.update_idletasks()
            width = wrapFrame.winfo_width()
            self.widHolder.config(width = width)
            wrapFrame.destroy()

    def delWidFrame(self,widget):
        #self.widList.delWidFrame(True,list(self.widList.widgets)[0][0])
        #print('DELCOMMENCE')
        
        for name in self.WidLabel.widgets:
            inWid = self.WidLabel.widgets[name]
            
            if inWid == widget:
                del self.WidLabel.widgets[name]
                widget.destroy()
                return
            elif inWid == widget.master:
                del self.WidLabel.widgets[name]
                widget.destroy()
                return

    def wipe(self):
        self.WidLabel.wipe()
        pass
        
        """
        keys = list(self.WidLabel.widgets.keys())
        
        for name in keys:
            self.WidLabel.widgets[name].destroy()
            del self.WidLabel.widgets[name]
        """
            
    def setScrollRegion(self,passive=False):
        if passive == False:
            self.update_idletasks()
            
        #print(self.widHolder.winfo_height(),'derps')
        #self.widHolderCnv.config(bg='green')
        #self.widHolder.config(bg='blue')
        #print(list(self.widgets)[0][0].winfo_width())
        #print(self.widHolder.winfo_width(),'derpettes')
        height = self.widHolderFrm.winfo_height()
        self.widHolderCnv.config(scrollregion=(0,0,0,height))

        self.widHolderCnv.config(width=self.widHolder.winfo_width())
        self.cheakIfScroll(frmHeight=height)

    def fillCnvWidth(self,width):
        self.widHolder.config(width=width)
            
    def makeWidLbl(self,frame=None,name=None):
        #print(frame)
        if frame == None: wrapFrame = self.widHolder
        else: wrapFrame = frame
        
        widFrame = self.WidLabel(wrapFrame,name=name)
        #widFrame.config(bg='grey82')
        widFrame.grid(row=widFrame.widID,padx=2,pady=1)

        #self.scrolly.config(command=self.widHolderCnv.yview)

        """
        widFrame.bind('<Enter>',self.onHover)
        widFrame.bind('<Leave>',self.onLeave)
        widFrame.bind_class(
            widFrame.tagName,'<ButtonPress-1>',self.onPress
            )
        widFrame.bind_class(
            widFrame.tagName,'<ButtonRelease-1>',self.onRelease
            )

        #print(widFrame.widgets)
        #self.lift(self.scrolly)
        #self.setCnvHeight()
        """
        return(widFrame)

    def update(self):
        self.setCnvHeight()
        self.setScrollRegion()

    def passiveUpdate(self):
        self.setCnvHeight(passive=True)
        self.setScrollRegion(passive=True)

    def onPress(self,event):
        #print('widLIST ONPRESS TRIGGER')
        holdFrame = event.widget.winfo_parent()
        holdFrame = self._nametowidget(holdFrame)
        widFrame = holdFrame.winfo_parent()
        widFrame = self._nametowidget(widFrame)

        item = WidLabel.exists(widFrame)
        if item == False: return(None)
        
        self.pressed = True
        
    def onRelease(self,event):
        self.pressed = False

    def onHover(self,event):
        if self.pressed == False:
            #print(event.widget)
            widFrame = event.widget.winfo_parent()
            widFrame = self._nametowidget(widFrame)

            item = self.WidLabel.exists(widFrame)
            if item == False: return(None)

            widLabel = self.widgets[widPair]['widLabel']
            #print('WIDIING',widPair)
            widLabel = self._nametowidget(widLabel)
            text = widLabel.cget('text')
            if '>' not in text:
                text='> '+text
                
            widLabel.config(text=text)
            self.update_idletasks()

    def onLeave(self,event):
        if self.pressed == False:
            widFrame = event.widget.winfo_parent()
            widFrame = self._nametowidget(widFrame)

            item = self.WidLabel.exists(widFrame)
            if item == False: return(None)

            widLabel = self.widgets[widPair]['widLabel']
            widLabel = self._nametowidget(widLabel)
            text = widLabel.cget('text')

            while '>' in text:
                ###############################
                # PEP-2
                ###############################
                # ValueError when you click too fast
                # might occur. Therefore i'm now using using
                # safe '>' removal
                # REVISION: ValueError only occured with long
                # blocking print calls. Probably redundant 
                # under typical use
                ###############################
                text=text[text.index('>')+1:]
                                
            widLabel.config(text=text.lstrip())
            self.update_idletasks()
        
    def onMouseWheel(self,event):
        # event.delta equantion is not cross-platform
        # WINDOWS ONLY
        
        if (self.entered and self.enableScroll) == True:
            self.widHolderCnv.yview("scroll",-event.delta//120,"units")

    def makeFrames(self):
        print('MAKE FRAMES')
        self.frame = Frame(self,bg='grey82')
        self.frame.grid(row=100,column=100,sticky='ns')
        self.rowconfigure(100,weight=1)
        
        self.canvasFrame = Frame(self.frame,bg='grey82')
        self.canvasFrame.grid(
            row=200,column=100#,padx=(0,30)
            ,sticky='ns'
            )
        self.frame.rowconfigure(200,weight=1)
        self.canvasFrame.bind('<Configure>',self.setCnvHeight)
        
        self.widHolderCnv = Canvas(
            self.canvasFrame,bd=0,highlightthickness=0
            ,bg='grey82'
            )
        self.widHolderCnv.grid(row=100,column=100)
        self.widHolderFrm = Frame(self.widHolderCnv,bg='grey82')
        self.widHolderFrm.grid(row=100,column=100)
        self.widHolder = Frame(self.widHolderFrm,bg='grey82')
        self.widHolder.grid(row=100,column=100,pady=1)

        #self.rowconfigure(200,weight=1)
        self.widHolderCnv.create_window(
            (0,0),window=self.widHolderFrm,anchor='nw'
            )

        self.scrolly = ttk.Scrollbar(
            self,command=self.widHolderCnv.yview
            )
        self.widHolderCnv.config(
            yscrollcommand=self.scrolly.set
            ,height=self.initialHeight
            )

        self.scrolly.grid(
            row=100,column=2000,sticky='ns'
            ,padx=(10,0)
            )
        self.rowconfigure(100,weight=1)
        
        #print(self.scrolly)

    def setCnvHeight(self,event=None,passive=False):
        """
        grows the widHolderCnv when widFrame is expanded
        does not shrink widHolderCnv when widFrame itself shrinks

        setCnvHeight and setHeight could probably be refactored
        into a single function. However, (partial) window resizability
        support will be cut though thats likely not needed anyway
        """
        #print('SET CNV HEIGHT')
        if self.passive == False and passive == False:
            self.update_idletasks()

        if event == None:
            height = self.canvasFrame.winfo_height()
        else:
            height = event.height
            
        #self.widHolderCnv.config(height=height)
        #print(height)
        self.widHolderCnv.config(height=height)
        self.cheakIfScroll(cnvHeight=height)

    def cheakIfScroll(self,frmHeight=None,cnvHeight=None):
        #self.update_idletasks()
        """
        note to self:
        canvasFrame is parent widget to widHolderCnv
        canvasFrame configured to expand to excess space

        canvases (e.g. widHolderCnv) cannot expand to space
        so widHolderCnv is made as child of canvasFrame
        and canvasFrame <Configure> event is bound to
        self.setCnvHeight, which resizes widHolderCnv to new
        size of canvasFrame
        """
        if frmHeight == None:
            frmHeight = self.widHolderFrm.winfo_height()
        if cnvHeight == None:
            cnvHeight = self.canvasFrame.winfo_height()

        if cnvHeight >= frmHeight:
            #print('ENABLE SCROLL EEZ FALSE')
            self.enableScroll = False
        else:
            #print('ENABLE SCROLL EEZ TRUE')
            self.enableScroll = True

class WidLabelMaker(object):
    """
    WTF is static functions in a class
    doing in a static function in a class 
    """

    @staticmethod
    def makeWidLabel():
        class WidLabel(PlusFrame):
            widgets = {}
            maxWidID = 1000
            widID = 0
            
            def __init__(self,master,name=None):
                PlusFrame.__init__(self,master)
                self['bg'] = 'white'
                
                self.make(name)
                self.grid(pady=0)

            def make(self,name=None):
                #print("WIDLIST NAME:",name)
                #self.displayWidgets()
                if name != None:
                    assert type(name) == str
                    self.name = name
                else:
                    self.name = self.widID+1
                    
                assert self.name not in self.widgets
                self.widgets[self.name] = self
                self.tagName = type(self).__name__+':'+str(self.widID)
                assert len(self.widgets) < self.maxWidID

                ID = self.widID+1
                while ID in self.widgets:
                    ID = (ID+1)%self.maxWidID

                #print(ID)
                type(self).widID = ID
                    
                #self.holdFrame = Frame(self)
                #self.addTag(self.holdFrame,self.tagName)

            @staticmethod
            def wipe():
                for name in WidLabel.widgets:
                    WidLabel.widgets[name].destroy()

                WidLabel.widgets = {}
                WidLabel.widID = 0

            @staticmethod
            def acquire(nameOrFrame):
                widgets = WidLabel.widgets
                
                if type(nameOrFrame) in (str,int):
                    try:
                        return(widgets[nameOrFrame])
                    except KeyError:
                        return(None)
                    
                else:
                    for name in widgets:
                        if widgets[name] == nameOrFrame:
                            return(name)

                    return(None)
                        
            @staticmethod
            def exists(varFrame):
                # could take from acquire
                if type(varFrame) == str:
                    try:
                        WidLabel.widgets[varFrame]
                        return(True)
                    
                    except KeyError:
                        return(False)
                    
                else:
                    widgets = WidLabel.acqWidgetList()
                    for widget in widgets:
                        if widget == varFrame:
                            return(True)

                    return(False)

            def displayWidgets(self):
                print(self.acqWidgetList())

            @staticmethod
            def acqWidgetList():
                return(list(WidLabel.widgets.keys()))

            @staticmethod
            def acqWidgetDict():
                answer = {}
                names = list(WidLabel.widgets.keys())
                for name in names:
                    answer[name] = WidLabel.widgets[name].grid_info()

                return answer
    
            def remove(self):
                self.destroy()
                del self.widgets[self.name]

        return(WidLabel)

if __name__ == '__main__':
    root = Tk()
    def press(event):
        pass #print(event.widget,event.x,event.y)
        
    bttn = Button(
        root,text='hi',onPress=press,bg='red'
        ,pressBg='pink'#,hoverBg='green'
        ,highlightthickness = 4
        ,highlightbackground = 'blue'
        )
    bttn.grid(ipadx=22,ipady=5,padx=5)
    root.mainloop()
