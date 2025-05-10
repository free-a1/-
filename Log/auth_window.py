# auth_window.py
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from Log.database import user_manager


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("用户登录")
        self.setFixedSize(300, 200)
        # 新增样式表设置背景图片
        self.setStyleSheet("""
                    QDialog {
                        background-image: url("assets/Icons/logo1.png");
                        background-repeat: no-repeat;
                        background-position: center;
                        background-size: cover;  /* 图片自适应窗口 */
                    }
                    QLineEdit, QPushButton {
                        background-color: rgba(255, 255, 255, 0.8);  /* 半透明背景 */
                        border: 1px solid #ccc;
                        padding: 5px;
                    }
                """)
        layout = QVBoxLayout()

        # 用户名输入
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("用户名")
        layout.addWidget(self.username_input)

        # 密码输入
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # 按钮布局
        button_layout = QHBoxLayout()

        # 登录按钮
        login_btn = QPushButton("登录")
        login_btn.clicked.connect(self.attempt_login)
        button_layout.addWidget(login_btn)

        # 注册按钮
        register_btn = QPushButton("注册")
        register_btn.clicked.connect(self.open_register)
        button_layout.addWidget(register_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)
        # 设置输入框字体
        input_font = QFont()
        input_font.setPointSize(12)
        self.username_input.setFont(input_font)
        self.password_input.setFont(input_font)

        # 设置按钮字体
        button_font = QFont()
        button_font.setPointSize(12)
        login_btn.setFont(button_font)
        register_btn.setFont(button_font)

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "错误", "用户名和密码不能为空")
            return

        result = user_manager.authenticate(username, password)
        if result:
            self.user_id, self.is_admin = result
            self.accept()  # 关闭对话框并返回成功
        else:
            QMessageBox.critical(self, "错误", "用户名或密码错误")

    def open_register(self):
        dialog = RegisterDialog(self)
        if dialog.exec():
            QMessageBox.information(self, "成功", "注册成功！请登录")


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("用户注册")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("用户名")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.register_btn = QPushButton("注册")
        self.register_btn.clicked.connect(self.register)
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "错误", "用户名和密码不能为空")
            return

        if user_manager.register_user(username, password):
            self.accept()
        else:
            QMessageBox.critical(self, "错误", "用户名已存在")