import sys
import os
import pickle
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QScrollArea, QFrame, QSizePolicy, QGridLayout, QLineEdit, QFileDialog,\
        QMainWindow
)
from PySide6.QtGui import  QFont, QFontMetrics,QPixmap, QDragEnterEvent, QDropEvent,QIcon, QAction
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QSplitter, QListWidget, QListWidgetItem, QWidget, QLabel
from PySide6.QtCore import QMimeData, QSize

from aiclass import AI

class Init_Dialog(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deepseek Desktop")
        self.resize(400, 150)
        widget = QWidget()
        layout = QGridLayout(widget)
        
        label1 = QLabel("API Key :")
        label2 = QLabel("MCP Files :")
        
        button1 = QPushButton("Select MCP Files")
        button2 = QPushButton("Done")
        
        self.line_edit1 = QLineEdit()
        self.line_edit1.setPlaceholderText("sk-xxxxxx...")
        
        
        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.line_edit1, 0, 1)
        layout.addWidget(label2, 1, 0)
        layout.addWidget(button1, 1, 1)
        layout.addWidget(button2, 2, 1)
        button1.clicked.connect(self.read_mcp_files)
        
        self.DS_API_KEY = ""
        self.mcp_files = []
        
        layout.setSpacing(10)
        #layout.setAlignment(button1, Qt.AlignTop | Qt.AlignLeft)
        layout.setRowStretch(0, 1)
        layout.setColumnStretch(1, 1)
        self.setLayout(layout)
        
        button2.clicked.connect(self.close_wid)
    
    def close_wid(self):
        self.DS_API_KEY = self.line_edit1.text()
        self.close()
    
    def read_mcp_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Choose MCP Files")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        selected_files, _ = file_dialog.getOpenFileNames(self, "Open File", "", "Python Files (*.py);;JSON Files (*.json)")
        if selected_files:
            self.mcp_files = selected_files
            print(f"Selected MCP file: {selected_files}")


class ChatBox(QWidget):
    def __init__(self):
        super().__init__()
        self.init_dialog = None
        
        self.current_chat_target = "Chat A"  # 当前聊天对象标识，默认设置为"好友A"
        self.history_path = "chathistory"  # 历史记录文件夹
        os.makedirs(self.history_path, exist_ok=True)  # 创建历史记录文件夹
        self.chat_records = {}   # 聊天记录存储：{对象标识: [消息列表]}
        self.initUI()
        self.load_chat_history()  # 加载聊天历史
        
        
        
    def show_init_dialog(self):
        if self.init_dialog is None:
            self.init_dialog = Init_Dialog()
        self.init_dialog.show()    
        
        
    def initUI(self):
        self.setWindowTitle('Deepseek Desktop')
        self.setGeometry(100, 100, 1000, 600)  # 扩大窗口初始尺寸

        # 加载窗口logo
        logo_folder = os.path.join(self.history_path, "avatars")
        logo_path = os.path.join(logo_folder, "logo.ico")
        if os.path.isfile(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        else:
            print(f"无法加载窗口logo: {logo_path}")

        # 主布局改为左右分栏
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧聊天对象列表（移除固定宽度限制，允许拖动调整）
        self.contact_list = QListWidget()
        # 原固定宽度设置已移除，改为通过QSplitter控制尺寸
        
        # 增加好友列表项（使用标准方法）
        self.add_contact_item("Chat 1")
        self.add_contact_item("Chat 2")
        self.contact_list.itemClicked.connect(self.switch_chat_target)
        
        # 右侧聊天区域（原主内容）
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)

        # 新增垂直分栏用于聊天显示区和输入区的高度调整
        chat_splitter = QSplitter(Qt.Vertical)

        # 滚动区域（原聊天记录区域）
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_container.setLayout(self.chat_layout)
        self.scroll_area.setWidget(self.chat_container)
        chat_splitter.addWidget(self.scroll_area)  # 添加到垂直分栏

        # 输入区域优化（扩大输入框）
        input_layout = QVBoxLayout()  # 使用垂直布局
        self.input_box = QTextEdit()
        self.input_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.input_box.setAcceptDrops(True)  # 开启拖拽功能

        # 创建按钮布局（将按钮放在右下角）
        button_layout = QGridLayout()
        self.send_button = QPushButton('发送')
        self.send_button.setShortcut('ctrl+return')
        self.send_button.clicked.connect(self.send_message)
        
        self.init_but = QPushButton('设置初始值')
        self.init_but.clicked.connect(self.show_init_dialog)
        
        # self.reply_button = QPushButton('好友回复')
        # self.reply_button.clicked.connect(self.send_friend_message)
        button_layout.addWidget(self.send_button, 0, 1)
        button_layout.addWidget(self.init_but, 0, 0)
        # button_layout.addWidget(self.reply_button)

        # 添加到垂直布局中
        input_layout.addWidget(self.input_box)
        input_layout.addLayout(button_layout)

        # 创建输入区域容器并设置布局
        input_container = QWidget()
        input_container.setLayout(input_layout)
        chat_splitter.addWidget(input_container)  # 添加到垂直分栏

        # 设置初始高度比例（显示区:输入区 = 3:2）
        chat_splitter.setSizes([300, 200])  # 初始窗口高度600px，按3:2分配

        # 组装右侧布局（将垂直分栏添加到右侧主布局）
        right_layout.addWidget(chat_splitter)

        # 主分栏添加左右组件
        main_splitter.addWidget(self.contact_list)
        main_splitter.addWidget(right_container)

        # 设置初始分隔比例（左侧初始200像素，右侧自动填充剩余空间）
        main_splitter.setSizes([200, 800])

        # 主窗口布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

        # 初始化好友A的聊天记录
        self.switch_chat_target(QListWidgetItem("Chat 1"))

    def add_contact_item(self, name: str):
        """添加聊天对象条目"""
        # 构建头像路径
        avatar_folder = os.path.join(self.history_path, "avatars")
        default_avatar_path = os.path.join(avatar_folder, "default.png")
        avatar_path = os.path.join(avatar_folder, f"{name}.png")

        # 检查头像文件是否存在
        if not os.path.isfile(avatar_path):
            avatar_path = default_avatar_path

        # 加载头像图片
        pixmap = QPixmap(avatar_path)
        if pixmap.isNull():
            print(f"无法加载头像图片: {avatar_path}")
        else:
            # 调整图片大小
            pixmap = pixmap.scaled(32, 32)

        item = QListWidgetItem(name)
        if not pixmap.isNull():
            item.setIcon(QIcon(pixmap))
        # 为每个好友创建一个默认的聊天记录列表
        if name not in self.chat_records:
            self.chat_records[name] = []
        if not self.contact_list.count():
            # 默认选中第一个好友
            item.setSelected(True)
        self.contact_list.addItem(item)

    def switch_chat_target(self, item: QListWidgetItem):
        """切换聊天对象时刷新聊天记录"""
        self.current_chat_target = item.text()
        self.clear_chat_layout()
        # 加载对应好友的聊天记录
        for msg in self.chat_records.get(self.current_chat_target, []):
            self.add_message(msg["text"], msg["is_sender"], msg.get("file_path"))

    def clear_chat_layout(self):
        """清空聊天记录布局"""
        for i in reversed(range(self.chat_layout.count())):
            widget = self.chat_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def save_chat_history(self):
        """保存聊天记录到文件"""
        for friend, messages in self.chat_records.items():
            file_path = os.path.join(self.history_path, f"{friend}.his")
            try:
                with open(file_path, 'wb') as f:
                    pickle.dump(messages, f)
            except Exception as e:
                print(f"保存聊天历史出错: {e}")

    def load_chat_history(self):
        """加载聊天历史记录"""
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
        message = self.input_box.toPlainText().strip()
        if message:
            self.chat_records[self.current_chat_target].append({
                "text": message,
                "is_sender": True,
                "file_path": None
            })
            self.add_message(message, is_sender=True)
            self.input_box.clear()
            return message
        return ''

    def ai_reply_message(self, msg:str):
        """AI 回复消息"""
        friend_message = msg  # 可扩展为从输入框获取内容
        self.chat_records[self.current_chat_target].append({
            "text": friend_message,
            "is_sender": False,
            "file_path": None
        })
        self.add_message(friend_message, is_sender=False)

    def add_message(self, message: str, is_sender: bool, file_path: str = None):
        # 计算当前聊天区域的宽度
        chat_width = self.scroll_area.viewport().width() if self.scroll_area.viewport() else 600
        max_bubble_width = min(int(chat_width * 0.66), 400)  # 最大宽度为聊天窗口的2/3，不超过400px
        
        # 创建消息容器
        message_widget = QWidget()
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(0, 0, 0, 0)

        # 气泡样式
        bubble_style = f"""
            QWidget#chatBubble {{
                background-color: {"#313131" if is_sender else "#000000"}; /* 发送消息为浅绿色，接收为米色 */
                border-radius: 15px;
                padding: 10px;
                max-width: {max_bubble_width}px;
            }}
        """

        # 内容部件
        content_widget = QWidget()
        content_widget.setObjectName("chatBubble")
        content_widget.setStyleSheet(bubble_style)
        
        # 文本标签设置为可选中
        content_label = QLabel(message)
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_label.setStyleSheet("background: transparent;")
        content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)  # 允许文本选中

        # 根据文本计算气泡宽度
        font = content_label.font()
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(message)
        bubble_width = max(100, min(text_width + 40, max_bubble_width))  # 最小宽度100px，文本宽度 + 内边距

        # 设置气泡最小高度
        text_lines = message.count('\n') + 1
        bubble_height = max(40, fm.lineSpacing() * text_lines + 20)  # 最小高度40px，文本高度 + 内边距

        # 手动设置气泡大小
        content_widget.setFixedSize(bubble_width, bubble_height)
        content_label.setMaximumWidth(bubble_width - 20)  # 减去内边距

        content_layout = QVBoxLayout(content_widget)
        content_layout.addWidget(content_label)

        message_layout.addWidget(content_widget)

        # 对齐方式
        message_layout.setAlignment(Qt.AlignmentFlag.AlignRight if is_sender else Qt.AlignmentFlag.AlignLeft)

        self.chat_layout.addWidget(message_widget)
        self.chat_layout.addSpacing(10)  # 增加消息间隔
        self.scroll_to_bottom()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                self.send_message(file_path=file_path)

    def scroll_to_bottom(self):
        scroll_bar = self.findChild(QScrollArea).verticalScrollBar()
        QTimer.singleShot(100, lambda: scroll_bar.setValue(scroll_bar.maximum()))

    def closeEvent(self, event):
        # 保存聊天记录
        self.save_chat_history()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_box = ChatBox()
    chat_box.show()
    sys.exit(app.exec())