import wx, praw, operator, datetime

GameWinNames = []
leaderboard = open('leaderboard.txt', 'a')
SaveMsgCheckBox = 0
guessers = 0
correct = 0

class Example(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Example, self).__init__(*args, **kwargs)

        self.InitUI()

    def InitUI(self):

        global ThreadID
        global Username
        global Password
        global results
        global msg_correct
        global msg_wrong
        global MSG_CRT
        global MSG_WRG
        global SaveMsgCheckBox
        global correct
        global guessers

        self.panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        menubar = wx.MenuBar()
        filem = wx.Menu()
        editm = wx.Menu()
        helpm = wx.Menu()

        menubar.Append(filem, '&File')
        menubar.Append(editm, '&Edit')
        menubar.Append(helpm, '&Help')
        self.SetMenuBar(menubar)

        ThreadIDBox = wx.TextEntryDialog(None,'What is the thread ID?','Thread ID','')

        if ThreadIDBox.ShowModal() == wx.ID_OK:
            ThreadID = ThreadIDBox.GetValue()

        UserNameBox = wx.TextEntryDialog(None,'What is your username?','Username','')

        if UserNameBox.ShowModal() == wx.ID_OK:
            Username = UserNameBox.GetValue()

        PassWordBox = wx.PasswordEntryDialog(None,'What is your password?','Password','')

        if PassWordBox.ShowModal() == wx.ID_OK:
            Password = PassWordBox.GetValue()


        st1 = wx.StaticText(self.panel, label='http://www.reddit.com/r/hockey/'+ThreadID, style=wx.ALIGN_CENTRE)
        st2 = wx.StaticText(self.panel, label='Currently logged in as '+Username, style=wx.ALIGN_CENTRE)
        st3 = wx.StaticText(self.panel, label='Add a goal scorer: ', style=wx.ALIGN_RIGHT)
        results = wx.TextCtrl(self.panel, pos=(350,5), size=(275,400), style=wx.TE_MULTILINE|wx.TE_READONLY)
        #st4 = wx.StaticText(self.panel, label='Total Guessers ' + str(guessers), style=wx.ALIGN_CENTRE)
        #st5 = wx.StaticText(self.panel, label='Total  ' + str(correct), style=wx.ALIGN_CENTRE)
        msg_correct = wx.TextCtrl(self.panel, value='Enter message to be sent to those who guessed correctly...', pos=(640,5), size=(250,250), style=wx.TE_MULTILINE)
        msg_wrong =  wx.TextCtrl(self.panel, value='Enter message to be sent to those who guessed incorrectly...', pos=(640,300), size=(250,250), style=wx.TE_MULTILINE)
        

        vbox.Add(st1, flag=wx.ALL, border=5)
        vbox.Add(st2, flag=wx.ALL, border=5)
        vbox.Add(st3, flag=wx.ALL, border=5)
        self.panel.SetSizer(vbox)


        self.SetSize((900, 600))
        self.SetTitle('Game Winning Goal Challenge - /r/hockey')
        self.Centre()
        self.Show(True)

        self.gwgname = wx.TextCtrl(self, value='Enter lowercase names...', pos=(125, 57), size=(215,-1))

        self.savbtn = wx.Button(self.panel, label='Save Name to list', pos=(165, 80))

        self.listctrl = wx.ListCtrl(self.panel, style=wx.LC_REPORT, pos=(10,110), size=(125,150))
        self.listctrl.InsertColumn(0, 'Name', width=125)

        self.clrbtn = wx.Button(self.panel, label='Clear ALL', pos=(5,260))
        imageFile = 'logo.png'
        logo = wx.Image(imageFile, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        wx.StaticBitmap(self, -1, logo, pos=(15,290))
        scrbrdbtwn = wx.Button(self.panel, label='Build Scoreboard', pos=(370,445))
        closebtn = wx.Button(self.panel, wx.ID_CLOSE, 'Close',pos=(390,500))
        
        self.msgsvbtn = wx.Button(self.panel, label='Save Messages', pos=(631,260))
        self.sndmsgchk = wx.CheckBox(self.panel, id=1, label='Send Messages?', pos=(750,265))
        self.sndmsgchk.SetValue(False)
        
        self.checknames = wx.Button(self.panel, label='Check names against Thread', pos=(135,175))

        self.sndmsgchk.Bind(wx.EVT_CHECKBOX, self.SendMessage, self.sndmsgchk)

        self.savbtn.Bind(wx.EVT_BUTTON, self.SaveName)
        self.clrbtn.Bind(wx.EVT_BUTTON, self.ClearNames)
        self.msgsvbtn.Bind(wx.EVT_BUTTON, self.SaveMessages)
        self.checknames.Bind(wx.EVT_BUTTON, self.gwg)
        closebtn.Bind(wx.EVT_BUTTON, self.OnClose)
        scrbrdbtwn.Bind(wx.EVT_BUTTON, self.BuildScoreBoard)

    def SendMessage(self, event):
        global SaveMsgCheckBox

        if self.sndmsgchk.GetValue():
            SaveMsgCheckBox = 1
            self.__log('SENDING MESSAGES')
        else: 
            SaveMsgCheckBox = 0
            self.__log('NOT SENDING MESSAGES')

    def SaveName(self, e):
        num_items = self.listctrl.GetItemCount()
        self.listctrl.InsertStringItem(num_items, self.gwgname.GetValue())
        GameWinNames.append(self.gwgname.GetValue())
        self.gwgname.Clear()

    def ClearNames(self, e):
        self.listctrl.DeleteAllItems()
        results.Clear()
        msg_correct.Clear()
        msg_wrong.Clear()
        GameWinNames[:] = []

    def SaveMessages(self, e):
        global MSG_CRT
        global MSG_WRG

        MSG_CRT = (msg_correct.GetValue())
        MSG_WRG = (msg_wrong.GetValue())
        self.__log('Messages Saved')

    def OnClose(self, e):
        self.Close()

    def __log(self, message):
        ''' Private method to append a string to the logger text
            control. '''
        results.AppendText('%s\n'%message)

    def gwg(self, e):
        r = praw.Reddit('Game Winning Goal Challenge App 1.0'
                        'by rx7raven/tickle_me_grover'
                        'https://praw.readthedocs.org/en/latest/'
                        'pages/comment_parsing.html')
        r.login(Username, Password)
        submission = r.get_submission(submission_id=ThreadID)
        flat_comments = submission.comments
        
        counter = 0
        for comment in flat_comments:
           text = comment.body
           subtimeutc = submission.created_utc
           subtime = datetime.datetime.utcfromtimestamp(subtimeutc)
           redditor = comment.author
           counter = counter + 1
           #guessers = guessers + 1
           if any(x in text.lower() for x in GameWinNames) and redditor != None:
                leader_add = redditor.name + "\n"
                for y in GameWinNames:
                    if(y in text.lower()):
                        self.__log('Yes ' + str(redditor) + ' ' + str(subtime))
                        leaderboard.write(leader_add)
                        #correct = correct + 1
                        if SaveMsgCheckBox == 1:
                            redditor.send_message('GWG Challenge', MSG_CRT)
           elif redditor != None:
                self.__log('No ' + str(redditor))
                if SaveMsgCheckBox == 1:
                            redditor.send_message('GWG Challenge', MSG_WRG)
           else:
                self.__log('DELETED USERNAME')

    def BuildScoreBoard(self, e):
        with open('leaderboard.txt') as f:
            content = f.readlines()

        print "\nSCOREBOARD\n"

        score_board = {}

        for name in content:
            if score_board.has_key(name):
                score_board[name] = score_board[name] + 1
            else:
                score_board[name] = 1
        sorted_x = sorted(score_board.iteritems(), key=operator.itemgetter(1))
        sorted_x.reverse()

        for key in sorted_x:
            string = "/u/" + key[0].rstrip('\n') + " " + str(key[1]) + "  "
            print string

def main():

    ex = wx.App()
    Example(None)
    ex.MainLoop()

if __name__ == '__main__':
    main()

#print guessers
#print correct