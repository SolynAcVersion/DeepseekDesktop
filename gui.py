from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton

app = QApplication([])

#创建一个窗口
widget = QWidget()
#设置窗口的位置和大小
widget.setGeometry(300,300,400,200)

#创建一个水平布局管理器，参数widget代表把布局管理器放在widget组件中
layout = QHBoxLayout(widget)

#创建两个按钮
button1=QPushButton('Button 1')
button2=QPushButton('Button 2')

#将两个按钮组将添加布局管理器中
layout.addWidget(button1)
layout.addWidget(button2)

widget.show()
app.exec()