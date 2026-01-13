import sys
import os
import threading
import pickle
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QScrollArea, QFrame, QSizePolicy, QGridLayout, QLineEdit, QFileDialog,\
        QMainWindow, QSlider, QProgressDialog
)
from PySide6.QtGui import  QFont, QFontMetrics,QPixmap, QDragEnterEvent, QDropEvent,QIcon, QAction
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtWidgets import QSplitter, QListWidget, QListWidgetItem, QWidget, QLabel
from PySide6.QtCore import QMimeData, QSize

from aiclass import AI


# window for initialization : ask for ds_api key and mcp dirs
# set place-holder for api_key format : "sk-xxxxxx"
# apikey is must-used while mcp dirs are optional
# the button apprears when api_key is empty
# no assurance methods for whether ds_api_key is available used
# assured whether mcp_dir exists and force *.py files, *.json files

class Init_Dialog(QWidget):
    
    # signal when "done" button pressed, before closing this window.
    # args: api_key: str, mcp_dirs: list
    
    sig_done = Signal(str, list)
    
    def __init__(self):
           
        super().__init__()
        
        self.DS_API_KEY = ""
        self.mcp_files = []
        
        self.setWindowTitle("Deepseek Desktop Initialization")
        self.resize(400, 150)
        
        widget = QWidget()
        layout = QGridLayout(widget)
        
        
        # elements in widget
        api_key_label = QLabel("API Key :")
        mcp_files_label = QLabel("MCP Files :")
        self.mcp_files_display = QLabel("")
        self.mcp_files_display.setWordWrap(True)
        
        select_files_button = QPushButton("Select MCP Files")
        done_button = QPushButton("Done")
        
        
        done_button.setShortcut('return')
        
        self.api_key_line_edit = QLineEdit()
        self.api_key_line_edit.setPlaceholderText("sk-xxxxxx...")
        
        
        # grid layout for neat ui ( maybe not
        layout.addWidget(api_key_label, 0, 0)
        layout.addWidget(self.api_key_line_edit, 0, 1)
        layout.addWidget(mcp_files_label, 1, 0)
        layout.addWidget(select_files_button, 1, 1)
        layout.addWidget(self.mcp_files_display)
        layout.addWidget(done_button)
        
        layout.setSpacing(10)
        #layout.setAlignment(button1, Qt.AlignTop | Qt.AlignLeft)
        layout.setRowStretch(0, 1)
        layout.setColumnStretch(1, 1)
        self.setLayout(layout)
        
        
        # action bounding
        select_files_button.clicked.connect(self.read_mcp_files)
        done_button.clicked.connect(self.close_wid)
    
    
    # send signal of {api_key: str and mcp_files: list} and close this window
    def close_wid(self):
        self.DS_API_KEY = self.api_key_line_edit.text()
        self.sig_done.emit(self.DS_API_KEY, self.mcp_files)
        self.close()
    
    
    
    # set up the window for reading files
    # rules: multi files, Python files, JSON files 
    # read files for reading mcp file dialog, transfer data to self.selected_files
    # print selected MCP files in console
    def read_mcp_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Choose MCP Files")
        file_dialog.setFileMode(QFileDialog.ExistingFile)  
        selected_files, _ = file_dialog.getOpenFileNames(self, "Open File", "", "Python Files (*.py);;JSON Files (*.json)")
        if selected_files:
            self.mcp_files = selected_files
            self.mcp_files_display.setText(f"Selected Files : {selected_files}")
            print(f"Selected MCP files: {selected_files}")


# window for settings during chats
# contains: system_prompt, temperature
# input: current system_prompt and current temperature
# adjust default values of elements based on current ones
# temperature here is multied 10 times and is an integer
# elements: QTextEdit , QSlider(Horizontal)

class settings(QWidget):
    
    # signal: {system_prompt: str, temperature: int}
    sig_save_settings = Signal(str, int, list)
    
    def __init__(self, sys_prompt_ori: str, temperature_ori: int, mcp_files: list):
        super().__init__()
        self.setWindowTitle("Chat Settings")
        self.resize(300, 400)
        widget = QWidget()
        layout = QGridLayout(widget)
        
        self.ori_mcp_files = mcp_files
        self.addition_mcp_files = []
        
        system_prompt_label = QLabel("System Prompt :")
        temp_label = QLabel("Temperature :")
        self.mcp_files_label = QLabel(' ')
        if not mcp_files:
            self.mcp_files_label = QLabel(f'MCP Files: {mcp_files}')
        else:
            self.mcp_files_label = QLabel(f'MCP Files: ')
        self.mcp_files_label.setWordWrap(True)
        
        self.sys_prompt_edit = QTextEdit()
        self.sys_prompt_edit.setText(sys_prompt_ori)
        
        self.temp_slider = QSlider(Qt.Horizontal)  
        
        add_mcp_files_button = QPushButton("Addition MCP Files")
        done_button = QPushButton("Done")
        
        # temperature of 10 times
        self.temp_slider.setRange(0, 15)
        self.temp_slider.setSingleStep(1)
        
        # set origin of temperature
        self.temp_slider.setValue(temperature_ori)
        temp_display_label = QLabel(str(float(temperature_ori) / 10.0))
        temp_display_label.setAlignment(Qt.AlignCenter)  
        
        # update label-of-temperature-display real-time (show in float format)
        self.temp_slider.valueChanged.connect(lambda val: temp_display_label.setText(str(float(val) / 10.0)))
        
        # no format assignment for confusing QTextEdit size
        layout.addWidget(system_prompt_label, 0, 0)
        layout.addWidget(self.sys_prompt_edit)
        layout.addWidget(temp_label)
        layout.addWidget(self.temp_slider)
        layout.addWidget(temp_display_label)
        layout.addWidget(self.mcp_files_label)
        layout.addWidget(add_mcp_files_button)
        layout.addWidget(done_button)
        
        add_mcp_files_button.clicked.connect(self.add_mcp_files)
        done_button.clicked.connect(self.close_wid)
        
        layout.setSpacing(10)
        #layout.setAlignment(button1, Qt.AlignTop | Qt.AlignLeft)
        layout.setRowStretch(0, 1)
        layout.setColumnStretch(1, 1)
        self.setLayout(layout)
        
    
    # opens file dialog and add addition mcp files
    def add_mcp_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Choose Addition MCP Files")
        file_dialog.setFileMode(QFileDialog.ExistingFile)  
        selected_files, _ = file_dialog.getOpenFileNames(self, "Open File", "", "Python Files (*.py);;JSON Files (*.json)")
        if selected_files:
            self.addition_mcp_files = selected_files
            self.mcp_files_label.setText(f"MCP Files: {self.addition_mcp_files + self.ori_mcp_files}")
    
    # send signal: {system_prompt: str, temperature: int}, and close this window
    def close_wid(self):
        self.system_prompt = self.sys_prompt_edit.toPlainText()
        self.sig_save_settings.emit(self.sys_prompt_edit.toPlainText(), self.temp_slider.value(), self.addition_mcp_files)
        self.close()


# multi-threading class
# done by vibe-coding, no explainations
class AIThread(QThread):
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, ai_instance, message):
        super().__init__()
        self.ai_instance = ai_instance
        self.message = message
        
    def run(self):
        try:
            response, _ = self.ai_instance.process_user_inp(self.message)
            if response:
                self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))

# main body of GUI, the window for chat

'''
actually copied and re-written from a passage on a local chat UI 
project ( Although is hard to distinguish this since I've changed it really
a lot. Find this in readme - acknowledgements
'''

class ChatBox(QWidget):
    def __init__(self):
        super().__init__()
        
        # Init_Dialog class instance
        self.init_dialog = None
        
        # prepare for initialization window and settings window
        # also used in args of chat requested
        self.DS_API_KEY = ""
        self.mcp_files = []
        self.system_prompt = ""
        self.temperature = 10
        self.ai = None
        
        # current chat
        self.current_chat_target = "Chat A"
        
        # save chats history in this path
        # makedir when this folder not exists
        self.history_path = "chathistory"
        os.makedirs(self.history_path, exist_ok=True)
        
        # chat histroy storage: {Object: [chat, messages]}
        self.chat_records = {}
        
        # Main UI Initialization
        self.initUI()
        
        # load previous chat history
        self.load_chat_history()
        

    # act bounded to button "Initializaion", call for showing the Init_Dialog sub window
    # only called when no available api_key provided
    def show_init_dialog(self):
        if self.init_dialog is None:
            self.init_dialog = Init_Dialog()
            
            # receive signal when "Done" button pressed and Init_Dialog window closed
            # bound func 'handle_init_done' right below
            self.init_dialog.sig_done.connect(self.handle_init_done)
        self.init_dialog.show()  
    
    # act when received signal above
    # bounded above
    def handle_init_done(self, api_key: str, mcp_files: list):
        self.DS_API_KEY = api_key
        self.mcp_files = mcp_files
        
        if not self.DS_API_KEY:
            self.DS_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
            
        if (self.DS_API_KEY and self.DS_API_KEY.startswith("sk-")):
            self.init_but.setVisible(False)
            self.send_button.setVisible(True)
            self.settings_but.setVisible(True)
            
            # uncertain progress dialog
            self.progress_dialog = QProgressDialog("正在初始化 AI，请稍候...", "取消", 0, 0, self)
            self.progress_dialog.setWindowTitle("初始化中")
            self.progress_dialog.setWindowModality(Qt.WindowModal)  
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.setRange(0, 0)
            self.progress_dialog.show()
            

            try:
                self.ai = AI(mcp_paths=self.mcp_files, api_key=api_key)
                self.temperature = int(self.ai.temperature * 10)   
                self.system_prompt = self.ai.system_prompt   
                self.progress_dialog.close()
            except Exception as e:
                self.progress_dialog.close()
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "初始化错误", f"AI 初始化失败：{e}")
          
          
    # act func bounded to button "Settings" for opening the Setting window
    # proceed the args: {current_system_prompt: str, current_temperature: int} to the window
    # launch a new Setting window instance once called
    def open_settings(self, sys_prompt: str, temp: int):
        self.temperature = int(self.ai.temperature * 10)  
        self.system_prompt = self.ai.system_prompt  
        self.settings_wid = settings(sys_prompt, temp, self.mcp_files)
        
        # receive signal when "Save" button pressed and Settings window closed
        # bound func 'handle_settings_save' right below
        self.settings_wid.sig_save_settings.connect(self.handle_settings_save)
        self.settings_wid.show()
        
        
    # act when received signal above
    # bounded above
    def handle_settings_save(self, sys_prompt: str, temp : int, addition_mcp_files: list):
        self.system_prompt = sys_prompt
        self.temperature = temp
        self.ai.system_prompt = self.system_prompt
        self.mcp_files += addition_mcp_files
        self.ai.add_mcp_mods(addition_mcp_files)
        self.system_prompt = self.ai.system_prompt
        self.ai.temperature = float(self.temperature) / 10.0  
                
        
    # main body for main window ( weired sentence
    def initUI(self):
        self.setWindowTitle('Deepseek Desktop')
        self.setGeometry(100, 100, 1000, 600)

        # load logo from ./{self.history_path}/avatars/
        # load logo file "logo.ico"
        logo_folder = os.path.join(self.history_path, "avatars")
        logo_path = os.path.join(logo_folder, "logo.ico")
        if os.path.isfile(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        else:
            print(f"无法加载窗口logo: {logo_path}")


        # split the main layout into to parts [left: contacts list, right: chat]
        main_splitter = QSplitter(Qt.Horizontal)  
        
        # left list of contacts
        self.chat_list = QListWidget()
        
        
        # add objects to the contacts col
        # pre-instanced 2 chats
        # func 'add_chat_item', 'switch_chat_target' are defined below
        self.add_chat_item("Chat 1")
        self.add_chat_item("Chat 2")
        self.chat_list.itemClicked.connect(self.switch_chat_target)
        
        
        
        # right part for chats
        # only contains 'chat_splitter', defined below
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)

        # adjust freely for splitting input area and view chat area of right part
        # relatively main body of right parts
        # contains: scroll_area (for view chats), input_container (for user input)
        chat_splitter = QSplitter(Qt.Vertical)  

        # 'scroll area' for viewing chats
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_container.setLayout(self.chat_layout)
        self.scroll_area.setWidget(self.chat_container)
        # add the scroll_area to the main part of right
        chat_splitter.addWidget(self.scroll_area)


        # input area layouts
        
        # the QTextEdit for input
        self.input_box_text_edit = QTextEdit()
        self.input_box_text_edit.setAcceptRichText(False)
        self.input_box_text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # enable drags for users to enlarge size of inpux box
        self.input_box_text_edit.setAcceptDrops(True) 

        # set up buttons in input area and connect act functions below
        # button: send
        self.send_button = QPushButton('发送')
        self.send_button.setShortcut('ctrl+return')
        self.send_button.clicked.connect(self.send_message)
        
        # button: settings
        self.settings_but = QPushButton('设置')
        self.settings_but.clicked.connect(lambda: self.open_settings(self.system_prompt, self.temperature))
        
        # button: initialization
        self.init_but = QPushButton('设置初始值')
        self.init_but.clicked.connect(self.show_init_dialog)
        
        
        # control visibilities of these buttons when initialized
        # based on whether DS_API_KEY is captured once you start
        if self.DS_API_KEY:
            self.init_but.setVisible(False)
            self.send_button.setVisible(True)
            self.settings_but.setVisible(True)
        else:
            self.init_but.setVisible(True)
            self.send_button.setVisible(False)
            self.settings_but.setVisible(False)
    
    
        # a button for auto-reply left by the origin project
        # kept for observing the mechenisms behind reply 
        # act func 'send_friend_message' is changed into 'reply_message', and is rewritten and reused.
        #------self.reply_button = QPushButton('好友回复')
        #------self.reply_button.clicked.connect(self.send_friend_message)
        
        
        # build a layout in the bottom area, especially for buttons in the right area
        button_layout = QGridLayout()
        button_layout.addWidget(self.send_button, 0, 1)
        button_layout.addWidget(self.init_but, 0, 1)
        button_layout.addWidget(self.settings_but, 0, 0)
        
        # build the buttom input area of the right chat part.
        # contain button layout above and the input QTextEdit
        input_layout = QVBoxLayout()
        input_layout.addWidget(self.input_box_text_edit)
        input_layout.addLayout(button_layout)

        # add input area to the chat part
        input_container = QWidget()
        input_container.setLayout(input_layout)
        chat_splitter.addWidget(input_container)


        chat_splitter.setSizes([300, 200])

        # to the main layout of right
        right_layout.addWidget(chat_splitter)

        # add left (contact_list) and right (right_container) to the whole UI splitter
        main_splitter.addWidget(self.chat_list)
        main_splitter.addWidget(right_container)

        # set default split rates: [left: 200 pixels, right: the rest space]
        main_splitter.setSizes([200, 800])


        # main layout, contains main_splitter
        # set main layout of the whole UI
        main_layout = QVBoxLayout()
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

        # initialize the chat of Chat 1 for initialization and default
        self.switch_chat_target(QListWidgetItem("Chat 1"))

        


    def add_chat_item(self, name: str):
        """add chat instances based on its name: str
            
            usage:
            
            self.add_chat_item("Chat 1")
        """

        # set avatar of the chat
        # ./{self.history_path}/avatars/default.png
        avatar_folder = os.path.join(self.history_path, "avatars")
        default_avatar_path = os.path.join(avatar_folder, "default.png")
        avatar_path = default_avatar_path
        pixmap = QPixmap(avatar_path)
        if pixmap.isNull():
            print(f"无法加载头像图片: {avatar_path}")
        else:
            # scale icon size to 32x32
            pixmap = pixmap.scaled(32, 32)
            
        
        # new chat instance 'item', and assign the icon to it
        item = QListWidgetItem(name)
        if not pixmap.isNull():
            item.setIcon(QIcon(pixmap))
        
        # add item to chat_record list, based on key={name}, value=[a empty list]
        if name not in self.chat_records:
            self.chat_records[name] = []
            
        # select this item the default chat instance if no chat in the UI chat list
        if not self.chat_list.count():
            item.setSelected(True)
        self.chat_list.addItem(item)

    def switch_chat_target(self, item: QListWidgetItem):
        """refresh chat area when switching to other chats"""
        
        self.current_chat_target = item.text()
        self.clear_chat_layout()
        
        # load msg from current chat
        for msg in self.chat_records.get(self.current_chat_target, []):
            self.add_message(msg["text"], msg["is_sender"])

    def clear_chat_layout(self):
        """clear current chat area"""
        
        # TREMINATE every widgets in current chat_layout to CLEAR the chatting area
        for i in reversed(range(self.chat_layout.count())):
            widget = self.chat_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()


    def save_chat_history(self):
        """Save chat messages history to local files"""
        for chat, messages in self.chat_records.items():
            
            # save to {history_path}/{chat}.his
            # en..encrypted (?)
            # emm... actually simply not readable if you open this file directly via notepad (
            # no secrets in chats with AI agents, r...right ?
            file_path = os.path.join(self.history_path, f"{chat}.his")
            try:
                with open(file_path, 'wb') as f:
                    pickle.dump(messages, f)
            except Exception as e:
                print(f"保存聊天历史出错: {e}")


    def load_chat_history(self):
        """load chat history from local files created in the above function"""
        for file_name in os.listdir(self.history_path):
            if file_name.endswith('.his'):
                friend_name = file_name[:-4]
                file_path = os.path.join(self.history_path, file_name)
                try:
                    with open(file_path, 'rb') as f:
                        self.chat_records[friend_name] = pickle.load(f)
                except Exception as e:
                    print(f"加载聊天历史出错: {e}")

    def send_message(self) -> str:
        """
        send messages to AI by User.
        
        get msg input by visiting text in self.input_box_text_edit
        
        return the message: str user input       
        
        """
        
        
        message = self.input_box_text_edit.toPlainText().strip()
        if message:
            
            # record user's message in chat_records
            # for instance:
            # chat_records["chat1"].append({
            #   "text": "ilovesrc",
            #   "is_sender": True,
            #   "file_path": None    
            # })
            self.chat_records[self.current_chat_target].append({
                "text": message,
                "is_sender": True,
                "file_path": None
            })
            
            # do not render msg itself, call func 'add_message' for rendering
            self.add_message(message, is_sender=True)
            
            # clear the text_edit in the input area
            self.input_box_text_edit.clear()
            self.send_button.setEnabled(False)
            
            self.ai_thread = AIThread(self.ai, message)
            self.ai_thread.finished.connect(lambda: self.send_button.setEnabled(True))
            self.ai_thread.finished.connect(self.reply_message)
            self.ai_thread.start()
                    
            return message
        
        
        return ''
    
            

    def reply_message(self, msg: str):
        """
        reply message
        
        args:
        - msg: the message you wanna reply to sender and render in the chatting area        
        """
        reply_msg_str = msg
        
        # similar usage above in 'send_message'
        self.chat_records[self.current_chat_target].append({
            "text": reply_msg_str,
            "is_sender": False,
            "file_path": None
        })
        
        # render the reply message in the chatting area
        self.add_message(reply_msg_str, is_sender=False)


    def add_message(self, message: str, is_sender: bool):
        """
        render msg in the chatting area
        
        DO NOT support markdown currently.
        
        args:
        - message: text you wanna render
        - is_sender: True / False whether the message comes from the user
        """

        # calculate the proper max width of massage bubble
        chat_width = self.scroll_area.viewport().width() if self.scroll_area.viewport() else 600
        # max width of bubble is the 2/3 times of width of the chatting part, and no more than 400 pix
        max_bubble_width = min(int(chat_width * 0.66), 400) 
        
        # create the container of message
        message_widget = QWidget()
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(0, 0, 0, 0)

        # the CSS of message (bushi
        # I AM THE KING IN FRONTEND !!!!!
        bubble_style = f"""
            QWidget#chatBubble {{
                background-color: {"#313131" if is_sender else "#000000"}; 
                
                /*
                #313131 for the user's message's bubble,
                #000000 for the reply's message's bubble
                */
                
                border-radius: 15px;
                padding: 10px;
                max-width: {max_bubble_width}px;
            }}
        """

        # Content
        content_widget = QWidget()
        content_widget.setObjectName("chatBubble")
        content_widget.setStyleSheet(bubble_style)
        
        # Set texts' appearances of the messages
        content_label = QLabel(message)
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_label.setStyleSheet("background: transparent;")
        content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        # I AM A TAILOR FOR EVERY FONT !
        font = content_label.font()
        fm = QFontMetrics(font)
        
        # max text width = max bubble width - padding
        max_text_width = max_bubble_width - 20
        

        text_rect = fm.boundingRect(0, 0, max_text_width, 0, Qt.TextWordWrap, message)  
        
        # calculating bubble width
        bubble_width = max(100, min(text_rect.width() + 20, max_bubble_width))
        
        # calculating bubble height
        bubble_height = max(40, text_rect.height() + 20)
        
        # bubble size settings
        content_widget.setFixedSize(bubble_width, bubble_height)
        
        # max width = bubble_width - padding
        content_label.setMaximumWidth(bubble_width - 20)

        content_layout = QVBoxLayout(content_widget)
        content_layout.addWidget(content_label)

        message_layout.addWidget(content_widget)
        message_layout.setAlignment(Qt.AlignmentFlag.AlignRight if is_sender else Qt.AlignmentFlag.AlignLeft)

        self.chat_layout.addWidget(message_widget)
        self.chat_layout.addSpacing(10)
        
        # auto-scroll to the bottom
        self.scroll_to_bottom()


    # auto-scroll to the bottom when new msg comes
    def scroll_to_bottom(self):
        scroll_bar = self.findChild(QScrollArea).verticalScrollBar()  
        
        # execute with delay = 100ms for updating UI rendering
        QTimer.singleShot(100, lambda: scroll_bar.setValue(scroll_bar.maximum()))


    # overwrite Qt's dragging system
    # triggered when user dragged any object (files, text) into the window
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            # check if the dragged obj contains url, like local dir
            event.acceptProposedAction()
            # accept user to release files


    # overwrite Qt's dragging system
    # trggered when user released mouse (drop the obj) on the window dragging obj
    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                
                # how to tackle the local file_path: str
                #------self.send_message(file_path=file_path)



    # overwrite closeEvent
    # save the history before closing
    # and do things before quitting when button X is clicked
    def closeEvent(self, event):
        self.save_chat_history()
        super().closeEvent(event)


if __name__ == '__main__':
    # just a module in building a normal pyside6 project
    app = QApplication(sys.argv)
    
    chat_box = ChatBox()
    chat_box.show()
    
    sys.exit(app.exec())