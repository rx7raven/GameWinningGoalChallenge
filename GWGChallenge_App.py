import wx, praw, operator, datetime

GameWinNames = []
leaderboard = open('leaderboard.txt', 'a')
SendMsgCheckBox = 0
BuildLeaderboardCheckBox = 0
guessers = 0
correct = 0

class Example(wx.Frame):
    #Initially run function when program is opened
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
        global SendMsgCheckBox
        global correct
        global guessers

        #builds the overall panel to place everything else onto
        self.panel = wx.Panel(self)

        #sets up menu and gives it 3 items
        menubar = wx.MenuBar()
        filem = wx.Menu()
        editm = wx.Menu()
        helpm = wx.Menu()

        #places File, Edit, Help on menubar and places that menu bar
        menubar.Append(filem, '&File')
        menubar.Append(editm, '&Edit')
        menubar.Append(helpm, '&Help')
        self.SetMenuBar(menubar)

        # Prompts the user for thread id,
        # username, and password.  Stores
        # all three into variables.
        ThreadIDBox = wx.TextEntryDialog(None,'What is the thread ID?','Thread ID','')
        if ThreadIDBox.ShowModal() == wx.ID_OK:
            ThreadID = ThreadIDBox.GetValue()
        UserNameBox = wx.TextEntryDialog(None,'What is your username?','Username','')
        if UserNameBox.ShowModal() == wx.ID_OK:
            Username = UserNameBox.GetValue()
        PassWordBox = wx.PasswordEntryDialog(None,'What is your password?','Password','')
        if PassWordBox.ShowModal() == wx.ID_OK:
            Password = PassWordBox.GetValue()

        #Builds the window for the application and sets the Title bar
        self.SetSize((900, 600))
        self.SetTitle('Game Winning Goal Challenge - /r/hockey')
        self.Centre()
        self.Show(True)

        #Builds the top left static text entries and combines them with variables collected from user
        #Also creates and places the gwg text box and the save to list button
        st1 = wx.StaticText(self.panel, label='http://www.reddit.com/r/hockey/'+ThreadID, style=wx.ALIGN_LEFT, pos=(5,-1))
        st2 = wx.StaticText(self.panel, label='Currently logged in as '+Username, style=wx.ALIGN_LEFT, pos=(5, 20))
        st3 = wx.StaticText(self.panel, label='Add a goal scorer: ', style=wx.ALIGN_LEFT, pos=(6, 55))
        self.gwgname = wx.TextCtrl(self, value='Enter goal scorer(s)...', pos=(125, 53), size=(140, -1))
        self.savbtn = wx.Button(self.panel, label='Save Name to list', pos=(68, 80))

        #Builds the text box and clear button which holds the list of gwg names
        self.listctrl = wx.ListCtrl(self.panel, style=wx.LC_REPORT, pos=(10,110), size=(255,150))
        self.listctrl.InsertColumn(0, 'Name', width=255)
        self.clrbtn = wx.Button(self.panel, label='Clear ALL', pos=(89,260))

        #Builds the middle logging text box
        results = wx.TextCtrl(self.panel, pos=(280,5), size=(340,400), style=wx.TE_MULTILINE|wx.TE_READONLY)
        
        #Loads logo.png file to memory and places it on panel
        imageFile = 'logo.png'
        logo = wx.Image(imageFile, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        wx.StaticBitmap(self, -1, logo, pos=(15,290))
        
        #Builds the correct/wrong text boxes
        msg_correct = wx.TextCtrl(self.panel, value='Enter message to be sent to those who guessed correctly...', pos=(640,5), size=(250,250), style=wx.TE_MULTILINE)
        msg_wrong =  wx.TextCtrl(self.panel, value='Enter message to be sent to those who guessed incorrectly...', pos=(640,300), size=(250,250), style=wx.TE_MULTILINE)

        #Creates the following buttons/checkboxes:
        #   Save Messages
        #   Write leaderboard
        #   Send Messages
        self.msgsvbtn = wx.Button(self.panel, label='Save Messages', pos=(631,260))
        self.bldldbchk = wx.CheckBox(self.panel, label='Write leaderboard?', pos=(750,255))
        self.sndmsgchk = wx.CheckBox(self.panel, label='Send Messages?', pos=(750,275))
        
        #forces checkboxes to false
        self.sndmsgchk.SetValue(False)
        self.bldldbchk.SetValue(False)
        
        #Buttons for checking the following:
        #   GWG names against the reddit thread
        #   Builds the scoreboard in console to copy at the end
        #   Closing the application window
        self.checknames = wx.Button(self.panel, label='Check names against Thread', pos=(345,410))
        scrbrdbtwn = wx.Button(self.panel, label='Build Scoreboard', pos=(385,445))
        closebtn = wx.Button(self.panel, wx.ID_CLOSE, 'Close',pos=(405,480))

        #Binding all the buttons to their events for interation.
        self.savbtn.Bind(wx.EVT_BUTTON, self.SaveName)
        self.clrbtn.Bind(wx.EVT_BUTTON, self.ClearNames)
        self.msgsvbtn.Bind(wx.EVT_BUTTON, self.SaveMessages)
        self.sndmsgchk.Bind(wx.EVT_CHECKBOX, self.SendMessage, self.sndmsgchk)
        self.bldldbchk.Bind(wx.EVT_CHECKBOX, self.BuildLeaderboard, self.bldldbchk)
        self.checknames.Bind(wx.EVT_BUTTON, self.gwg)
        closebtn.Bind(wx.EVT_BUTTON, self.OnClose)
        scrbrdbtwn.Bind(wx.EVT_BUTTON, self.BuildScoreBoard)
    
    #Function that gets called when the Build Leaderboard button is pressed.
    #It sets a variable to be used later and outputs a message to the log.
    def BuildLeaderboard(self, e):
        global BuildLeaderboardCheckBox

        if self.bldldbchk.GetValue():
            BuildLeaderboardCheckBox = 1
            self.__log('BUILDING LEADERBOARD')
        else:
            BuildLeaderboardCheckBox = 0
            self.__log('NOT BUILDING LEADERBOARD')
    
    #Function that first checks the Send Message checkbox and sets a variable
    #to be used later. Also outputs a message to the log.
    def SendMessage(self, e):
        global SendMsgCheckBox

        if self.sndmsgchk.GetValue():
            SendMsgCheckBox = 1
            self.__log('SENDING MESSAGES')
        else: 
            SendMsgCheckBox = 0
            self.__log('NOT SENDING MESSAGES')

    #Function that gets called when the Save Name to List button is pressed.
    #It saves the player name entered to a list and displays said list in
    #report box and clears input box.
    def SaveName(self, e):
        num_items = self.listctrl.GetItemCount()
        #Storing the name in lowercase
        LowerCaseName = (self.gwgname.GetValue())
        LowerCaseName = LowerCaseName.lower()
        self.listctrl.InsertStringItem(num_items, LowerCaseName)
        GameWinNames.append(self.gwgname.GetValue())
        self.gwgname.Clear()

    #Functuin that gets called when the Clear All button is pressed.
    #It clears all the unput boxes, report, and log.
    def ClearNames(self, e):
        self.listctrl.DeleteAllItems()
        results.Clear()
        msg_correct.SetValue('Enter message to be sent to those who guessed correctly...')
        msg_wrong.SetValue('Enter message to be sent to those who guessed incorrectly...')
        GameWinNames[:] = []

    #Function that gets called when the Save Messages button is pressed.
    #It saves the correct/wrong messages to variables and outputs to log.
    def SaveMessages(self, e):
        global MSG_CRT
        global MSG_WRG

        MSG_CRT = (msg_correct.GetValue())
        MSG_WRG = (msg_wrong.GetValue())
        self.__log('Messages Saved')

    #Function that is used to push messages to the logger.
    def __log(self, message):
        ''' Private method to append a string to the logger text
            control. '''
        results.AppendText('%s\n'%message)

    #Function that gets called when the Close button is pressed/
    #It closes the application window.
    def OnClose(self, e):
        self.Close()

    #Function that gets called when the Check Names Against Thread button is pressed.
    #Logs into the reddit API and pulls the thread comments/submitters and checks them
    #against what is inputted by the user.  Also outputs list to logger
    def gwg(self, e):
        r = praw.Reddit('Game Winning Goal Challenge App 1.0'
                        'by rx7raven/tickle_me_grover'
                        'https://praw.readthedocs.org/en/latest/'
                        'pages/comment_parsing.html')
        r.login(Username, Password)
        submission = r.get_submission(submission_id=ThreadID)
        flat_comments = submission.comments
        
        guessers = 0
        correct = 0
        counter = 0
        for comment in flat_comments:
           text = comment.body
           commenttimeutc = comment.created_utc
           commenttime = datetime.datetime.utcfromtimestamp(commenttimeutc)
           redditor = comment.author
           counter = counter + 1
           guessers = guessers + 1
           if any(x in text.lower() for x in GameWinNames) and redditor != None:
                leader_add = redditor.name + "\n"
                for y in GameWinNames:
                    if(y in text.lower()):
                        self.__log(str(guessers) + ' Yes ' + str(redditor) + ' ' + str(commenttime))
                        if BuildLeaderboardCheckBox == 1:
                            leaderboard.write(leader_add)
                        correct = correct + 1
                        if SendMsgCheckBox == 1:
                            redditor.send_message('GWG Challenge', MSG_CRT)
           elif redditor != None:
                self.__log(str(guessers) + ' No ' + str(redditor))
                if SendMsgCheckBox == 1:
                            redditor.send_message('GWG Challenge', MSG_WRG)
           else:
                self.__log('DELETED USERNAME')
        self.__log('Number of correct answers: ' + str(correct))

        #Closes leaderboard file
        leaderboard.close()
    
    #Function that gets called when Build Scoreboard button is pressed.
    #It opens text file, reads each line and counts how many times a user is listed.
    #Then outputs this to console in most to least order.
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