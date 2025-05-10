import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QDialog
from PySide6.QtGui import QPixmap, QIcon, QFontDatabase, QFont
from PySide6.QtCore import Qt, QFile, QTextStream
from Backend.offline import OfflineWindow
from Backend.online import OnlineWindow
from Log.auth_window import LoginDialog
from Log.admin_panel import AdminPanel

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.show_login_dialog()  # 先登录
        self.init_ui()  # 再初始化界面


    def init_ui(self):
        # ---------- 样式和字体初始化 ----------
        # 加载样式表
        style_file = QFile("assets/Style/style.qss")
        style_file.open(QFile.ReadOnly | QFile.Text)
        self.setStyleSheet(QTextStream(style_file).readAll())

        # 加载字体
        font_id = QFontDatabase.addApplicationFont("assets/Font/TitilliumWeb-Bold.ttf")
        app_font = QFont("Titillium Web" if font_id != -1 else "Arial")
        QApplication.instance().setFont(app_font)

        # ---------- 窗口基本设置 ----------
        self.setWindowTitle("IdentiFace")
        self.setFixedSize(500, 200)
        self.setWindowIcon(QIcon("assets/Icons/favicon-black.png"))
        self.center_window()

        # ---------- 主界面布局 ----------
        main_layout = QVBoxLayout()

        # Logo
        logo_label = QLabel(alignment=Qt.AlignCenter)
        logo_label.setPixmap(QPixmap("assets/Icons/logo.png"))
        main_layout.addWidget(logo_label)

        # 按钮布局
        btn_layout = QHBoxLayout()
        self.online_btn = QPushButton("视频模式")
        self.offline_btn = QPushButton("照片模式")
        self.admin_btn = QPushButton("管理面板")  # 新增按钮
        self.admin_btn.setVisible(False)  # 默认隐藏

        # 绑定事件
        self.online_btn.clicked.connect(self.open_online_window)
        self.offline_btn.clicked.connect(self.open_offline_window)
        self.admin_btn.clicked.connect(self.open_admin_panel)

        # 添加到布局
        btn_layout.addWidget(self.online_btn)
        btn_layout.addWidget(self.offline_btn)
        btn_layout.addWidget(self.admin_btn)  # 添加管理按钮

        # 根据权限显示按钮
        if self.current_user.get("is_admin"):
            self.admin_btn.setVisible(True)
            self.admin_btn.setEnabled(True)  # 确保启用按钮
        else:
            self.admin_btn.setVisible(False)
            self.admin_btn.setEnabled(False)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def center_window(self):
        """窗口居中显示"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def show_login_dialog(self):
        """显示登录对话框"""
        login_dialog = LoginDialog(self)
        if login_dialog.exec() == QDialog.Accepted:
            self.current_user = {
                'id': login_dialog.user_id,
                'is_admin': login_dialog.is_admin
            }
            self.show()  # 登录成功显示主窗口
        else:
            sys.exit()  # 取消登录直接退出

    def open_admin_panel(self):
        self.admin_panel = AdminPanel()
        self.admin_panel.show()
        self.hide()

    # ---------- 功能方法保持原样 ----------
    def open_online_window(self):
        self.online_window = OnlineWindow()
        self.online_window.show()
        self.hide()

    def open_offline_window(self):
        self.offline_window = OfflineWindow()
        self.offline_window.show()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome_window = WelcomeWindow()
    welcome_window.show()
    sys.exit(app.exec())
