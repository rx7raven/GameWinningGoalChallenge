# GameWinningGoalChallenge Application
-Kevin Farver (rx7raven)

The Game Winnning Goal application was developed in conjuction with /u/tickle_me_grover and was created for the Game Winning Goal Challenge on reddit. During the NHL playoffs a post is made  once a day.  Users then comment with a name(s) of the player who scores the game winning goal.

Originally, we would use a python script and modify the code manually to enter thread id, username/password, name of players who scored game winning goal,and messages to be sent for correct/wrong answers.  This became tedious and at times hard to manage.

This is where the Game Winning Goal Challenge Application steps in to make the lives of /r/rx7raven and /u/tickle_me_grover easier (espically on those early weekend games).

Game Winning Goal Challenge Application  
Inputs  
	Thread ID  
	Username/Password  
	GWG Name  
	Correct/Wrong Messages to be sent  
Outputs  
	Application has a logger in the center to give the user some output.  It will check to see whether the send message and build leader boards are checked to ensure the correct settings are made.  
Buttons
	Save name to list  
	Clear All  
	Save Messages(message only sent if box is checked)  
	Check names against Thread  
	Build Scoreboard(builds from current text file)  
	Close  
