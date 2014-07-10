#Fill the content of each Frame
#Define the events related to displaying widgets

from PyQt4 import QtGui, QtCore

class MainFrame(QtGui.QFrame):
	def __init__(self, parent):
        	super(MainFrame, self).__init__(parent)

        	groupBox = QtGui.QGroupBox("Choose the DIAG operation")

       		self.sf = QtGui.QPushButton("SF Function")
       		self.map = QtGui.QPushButton("SF Map")
       		self.sequence = QtGui.QPushButton("Sequence")
       		self.classRules = QtGui.QPushButton("Classification rules")
       		self.allSF = QtGui.QPushButton("All SF Maps of a SF Function")
       		self.allMaps = QtGui.QPushButton("All SF Maps")

	    	self.vbox = QtGui.QVBoxLayout(self)
		self.vbox.addWidget(self.sf)
		self.vbox.addWidget(self.map)
		self.vbox.addWidget(self.sequence)
		self.vbox.addWidget(self.classRules)
		self.vbox.addWidget(self.allSF)
		self.vbox.addWidget(self.allMaps)
		groupBox.setLayout(self.vbox)

	    	self.vmainBox = QtGui.QVBoxLayout(self)
		self.vmainBox.addWidget(groupBox)
		self.setLayout(self.vmainBox)


class SF_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(SF_Frame, self).__init__(parent)

		#Box1
	    	hbox1 = QtGui.QHBoxLayout()
		self.index_l = QtGui.QLabel("Content")
		hbox1.addWidget(self.index_l)
        	hbox1.addStretch()

		#Box2
	    	hbox2 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.start = QtGui.QPushButton("Start")
		hbox2.addWidget(self.back)
		hbox2.addWidget(self.start)

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.Label = QtGui.QLabel("Empty")
		self.vbox.addWidget(self.Label)
		self.vbox.addLayout(hbox1)
		self.vbox.addLayout(hbox2)
		self.setLayout(self.vbox)

class SFMap_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(SFMap_Frame, self).__init__(parent)

		#Box1
	    	hbox1 = QtGui.QHBoxLayout()
		self.index_l = QtGui.QLabel("Content")
		hbox1.addWidget(self.index_l)
        	hbox1.addStretch()

		#Box2
	    	hbox2 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.start = QtGui.QPushButton("Start")
		hbox2.addWidget(self.back)
		hbox2.addWidget(self.start)

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.Label = QtGui.QLabel("Empty")
		self.vbox.addWidget(self.Label)
		self.vbox.addLayout(hbox1)
		self.vbox.addLayout(hbox2)
		self.setLayout(self.vbox)

class Sequence_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(Sequence_Frame, self).__init__(parent)

		#Box1
	    	hbox1 = QtGui.QHBoxLayout()
		self.index_l = QtGui.QLabel("Content")
		hbox1.addWidget(self.index_l)
        	hbox1.addStretch()

		#Box2
	    	hbox2 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.start = QtGui.QPushButton("Start")
		hbox2.addWidget(self.back)
		hbox2.addWidget(self.start)

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.Label = QtGui.QLabel("Empty")
		self.vbox.addWidget(self.Label)
		self.vbox.addLayout(hbox1)
		self.vbox.addLayout(hbox2)
		self.setLayout(self.vbox)

class ClassRules_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(ClassRules_Frame, self).__init__(parent)

		#Box1
	    	hbox1 = QtGui.QHBoxLayout()
		self.index_l = QtGui.QLabel("Content")
		hbox1.addWidget(self.index_l)
        	hbox1.addStretch()

		#Box2
	    	hbox2 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.start = QtGui.QPushButton("Start")
		hbox2.addWidget(self.back)
		hbox2.addWidget(self.start)

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.Label = QtGui.QLabel("Empty")
		self.vbox.addWidget(self.Label)
		self.vbox.addLayout(hbox1)
		self.vbox.addLayout(hbox2)
		self.setLayout(self.vbox)

class AllSF_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(AllSF_Frame, self).__init__(parent)

		#Box1
	    	hbox1 = QtGui.QHBoxLayout()
		self.index_l = QtGui.QLabel("Content")
		hbox1.addWidget(self.index_l)
        	hbox1.addStretch()

		#Box2
	    	hbox2 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.start = QtGui.QPushButton("Start")
		hbox2.addWidget(self.back)
		hbox2.addWidget(self.start)

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.Label = QtGui.QLabel("Empty")
		self.vbox.addWidget(self.Label)
		self.vbox.addLayout(hbox1)
		self.vbox.addLayout(hbox2)
		self.setLayout(self.vbox)


class AllMaps_Frame(QtGui.QFrame):
	def __init__(self, parent):
        	super(AllMaps_Frame, self).__init__(parent)

		#Box1
	    	hbox1 = QtGui.QHBoxLayout()
		self.index_l = QtGui.QLabel("Content")
		hbox1.addWidget(self.index_l)
        	hbox1.addStretch()

		#Box2
	    	hbox2 = QtGui.QHBoxLayout()
       		self.back = QtGui.QPushButton("Back")
       		self.start = QtGui.QPushButton("Start")
		hbox2.addWidget(self.back)
		hbox2.addWidget(self.start)

		#Main Box
	    	self.vbox = QtGui.QVBoxLayout()
		self.Label = QtGui.QLabel("Empty")
		self.vbox.addWidget(self.Label)
		self.vbox.addLayout(hbox1)
		self.vbox.addLayout(hbox2)
		self.setLayout(self.vbox)


class MainWindow(QtGui.QMainWindow):

    	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)

		self.mainFrame = MainFrame(QtGui.QFrame(self))
		self.SFFrame = SF_Frame(QtGui.QFrame(self))
		self.SFMapFrame = SFMap_Frame(QtGui.QFrame(self))
		self.seqFrame =	Sequence_Frame(QtGui.QFrame(self))
		self.classRulesFrame =	ClassRules_Frame(QtGui.QFrame(self))
		self.allSFFrame = AllSF_Frame(QtGui.QFrame(self))
		self.allMapsFrame = AllMaps_Frame(QtGui.QFrame(self))


		self.central_widget = QtGui.QStackedWidget()		#Creation
       		self.central_widget.addWidget(self.mainFrame)		#Fill
       		self.central_widget.addWidget(self.SFFrame)
       		self.central_widget.addWidget(self.SFMapFrame)
       		self.central_widget.addWidget(self.seqFrame)
       		self.central_widget.addWidget(self.classRulesFrame)
       		self.central_widget.addWidget(self.allSFFrame)
       		self.central_widget.addWidget(self.allMapsFrame)
		self.central_widget.setCurrentWidget(self.mainFrame)	#Set Currrent
		self.setCentralWidget(self.central_widget)		#Add to main Window


		####################
		#Events connections#
		####################
		#Main Frame
		self.mainFrame.sf.clicked.connect(self.SF_buttonClicked)
		self.mainFrame.map.clicked.connect(self.SFMap_buttonClicked)  
		self.mainFrame.sequence.clicked.connect(self.seq_buttonClicked) 
		self.mainFrame.classRules.clicked.connect(self.classRules_buttonClicked)  
		self.mainFrame.allSF.clicked.connect(self.allSF_buttonClicked)  
		self.mainFrame.allMaps.clicked.connect(self.allMaps_buttonClicked)  

		#SF Frame
		self.SFFrame.back.clicked.connect(self.back_buttonClicked)
		self.SFFrame.start.clicked.connect(self.SFStart_buttonClicked)

		#SFMap Frame
		self.SFMapFrame.back.clicked.connect(self.back_buttonClicked)
		self.SFMapFrame.start.clicked.connect(self.SFMapStart_buttonClicked)

		#Sequence Frame
		self.seqFrame.back.clicked.connect(self.back_buttonClicked)
		self.seqFrame.start.clicked.connect(self.seqStart_buttonClicked)

		#Classification Rules Frame
		self.classRulesFrame.back.clicked.connect(self.back_buttonClicked)
		self.classRulesFrame.start.clicked.connect(self.classRulesStart_buttonClicked)

		#AllSF Frame
		self.allSFFrame.back.clicked.connect(self.back_buttonClicked)
		self.allSFFrame.start.clicked.connect(self.allSFStart_buttonClicked)

		#All Maps Frame
		self.allMapsFrame.back.clicked.connect(self.back_buttonClicked)
		self.allMapsFrame.start.clicked.connect(self.allMapsStart_buttonClicked)


		###################
		#Window Parameters#
		###################
		QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10)) 
		#self.setWindowIcon(QtGui.QIcon('network.png')) 
		self.setGeometry(300, 300, 300, 200)
		self.setWindowTitle('Troubleshooting Management')
		self.statusBar()


	def SF_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.SFFrame)

	def SFMap_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.SFMapFrame)

	def seq_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.seqFrame)

	def classRules_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.classRulesFrame)

	def allSF_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.allSFFrame)

	def allMaps_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.allMapsFrame)


	def back_buttonClicked(self): 
		self.central_widget.setCurrentWidget(self.mainFrame)


	def SFStart_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.SFFrame)

	def SFMapStart_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.SFMapFrame)

	def seqStart_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.seqFrame)

	def classRulesStart_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.classRulesFrame)

	def allSFStart_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.allSFFrame)

	def allMapsStart_buttonClicked(self):
		self.central_widget.setCurrentWidget(self.allMapsFrame)


def main():
   
	app = QtGui.QApplication(sys.argv)
   	mainw = MainWindow()
   	mainw.show()
   	sys.exit(app.exec_())
	db.close()

if __name__ == '__main__':
    	main()
