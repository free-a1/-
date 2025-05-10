# admin_panel.py
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox, QDialog, QLabel,
    QLineEdit, QFormLayout, QHBoxLayout, QCheckBox
)
from Log.database import user_manager
import shutil
import datetime
from PySide6.QtWidgets import (QTabWidget, QGroupBox, QFileDialog, QTextEdit)


class SystemSettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统设置")
        self.setFixedSize(800, 600)

        # 使用选项卡组织功能
        self.tabs = QTabWidget()

        # 1. 系统参数配置
        self.settings_tab = QWidget()
        self._create_settings_tab()
        self.tabs.addTab(self.settings_tab, "参数配置")

        # 2. 数据库管理
        self.db_tab = QWidget()
        self._create_db_tab()
        self.tabs.addTab(self.db_tab, "数据库")

        # 3. 日志管理
        self.logs_tab = QWidget()
        self._create_logs_tab()
        self.tabs.addTab(self.logs_tab, "日志管理")

        # 4. 用户审计
        self.audit_tab = QWidget()
        self._create_audit_tab()
        self.tabs.addTab(self.audit_tab, "操作审计")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)



    def _create_settings_tab(self):
        layout = QFormLayout()

        # 系统参数示例
        self.max_login_attempts = QLineEdit()
        self.session_timeout = QLineEdit()
        self.enable_audit = QCheckBox("启用操作记录")

        layout.addRow(QLabel("最大登录尝试次数:"), self.max_login_attempts)
        layout.addRow(QLabel("会话超时(分钟):"), self.session_timeout)
        layout.addRow(self.enable_audit)

        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_system_settings)
        layout.addRow(save_btn)

        self.settings_tab.setLayout(layout)

    def _create_db_tab(self):
        layout = QVBoxLayout()

        # 备份数据库
        backup_btn = QPushButton("备份数据库")
        backup_btn.clicked.connect(self.backup_database)

        # 恢复数据库
        restore_btn = QPushButton("恢复数据库")
        restore_btn.clicked.connect(self.restore_database)

        layout.addWidget(backup_btn)
        layout.addWidget(restore_btn)
        self.db_tab.setLayout(layout)

    def _create_logs_tab(self):
        layout = QVBoxLayout()

        # 日志预览
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)

        # 操作按钮
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("刷新日志")
        clear_btn = QPushButton("清理日志")
        export_btn = QPushButton("导出日志")

        refresh_btn.clicked.connect(self.load_logs)
        clear_btn.clicked.connect(self.clear_logs)
        export_btn.clicked.connect(self.export_logs)

        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addWidget(export_btn)

        layout.addWidget(self.log_view)
        layout.addLayout(btn_layout)
        self.logs_tab.setLayout(layout)

    def _create_audit_tab(self):
        layout = QVBoxLayout()

        # 审计表格
        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(4)
        self.audit_table.setHorizontalHeaderLabels(["时间", "用户", "操作", "详情"])
        self.audit_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 导出按钮
        export_btn = QPushButton("导出审计记录")
        export_btn.clicked.connect(self.export_audit_logs)

        layout.addWidget(self.audit_table)
        layout.addWidget(export_btn)
        self.audit_tab.setLayout(layout)

    # ---- 功能实现 ----
    def save_system_settings(self):
        """保存系统参数到配置文件"""
        try:
            # 示例保存逻辑
            config = {
                'max_login_attempts': self.max_login_attempts.text(),
                'session_timeout': self.session_timeout.text(),
                'enable_audit': self.enable_audit.isChecked()
            }
            # 这里添加实际保存到数据库或配置文件的代码
            QMessageBox.information(self, "成功", "系统配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def backup_database(self):
        """数据库备份"""
        path, _ = QFileDialog.getSaveFileName(
            self, "保存备份",
            f"backup_{datetime.datetime.now().strftime('%Y%m%d')}.db",
            "Database Files (*.db)"
        )
        if path:
            try:
                shutil.copyfile('users.db', path)
                QMessageBox.information(self, "成功", "数据库备份完成")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"备份失败: {str(e)}")

    def restore_database(self):
        """数据库恢复"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择备份文件",
            "", "Database Files (*.db)"
        )
        if path:
            try:
                shutil.copyfile(path, 'users.db')
                QMessageBox.information(self, "成功", "数据库已恢复，请重启系统")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"恢复失败: {str(e)}")

    def load_logs(self):
        """加载日志内容"""
        try:
            with open("system.log", "r", encoding="utf-8") as f:
                self.log_view.setText(f.read())
        except FileNotFoundError:
            self.log_view.setText("暂无日志记录")

    def clear_logs(self):
        """清理日志文件"""
        try:
            open("system.log", "w").close()
            self.load_logs()
            QMessageBox.information(self, "成功", "日志已清空")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"清理失败: {str(e)}")

    def export_logs(self):
        """导出日志"""
        path, _ = QFileDialog.getSaveFileName(
            self, "导出日志",
            f"logs_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
            "Text Files (*.txt)"
        )
        if path:
            try:
                shutil.copyfile("system.log", path)
                QMessageBox.information(self, "成功", "日志导出完成")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")

    def load_audit_logs(self):
        """加载审计日志"""
        try:
            # 示例从数据库加载审计记录
            cursor = user_manager.conn.cursor()
            cursor.execute("SELECT * FROM audit_log ORDER BY timestamp DESC")
            logs = cursor.fetchall()

            self.audit_table.setRowCount(len(logs))
            for row, (timestamp, user, action, detail) in enumerate(logs):
                self.audit_table.setItem(row, 0, QTableWidgetItem(timestamp))
                self.audit_table.setItem(row, 1, QTableWidgetItem(user))
                self.audit_table.setItem(row, 2, QTableWidgetItem(action))
                self.audit_table.setItem(row, 3, QTableWidgetItem(detail))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载失败: {str(e)}")

    def export_audit_logs(self):
        """导出审计记录"""
        path, _ = QFileDialog.getSaveFileName(
            self, "导出审计记录",
            f"audit_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        if path:
            try:
                # 示例导出逻辑
                with open(path, "w", encoding="utf-8") as f:
                    f.write("时间,用户,操作,详情\n")
                    cursor = user_manager.conn.cursor()
                    cursor.execute("SELECT * FROM audit_log")
                    for record in cursor.fetchall():
                        f.write(f"{','.join(map(str, record))}\n")
                QMessageBox.information(self, "成功", "审计记录导出完成")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")


class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统管理")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()

        # 原有用户列表和刷新按钮
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["用户名", "权限", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.load_users)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)
        self.load_users()
        # 设置表格字体
        table_font = QFont()
        table_font.setPointSize(12)
        self.table.setFont(table_font)

        # 设置按钮字体
        button_font = QFont()
        button_font.setPointSize(12)
        refresh_btn.setFont(button_font)

        # 在刷新按钮后添加系统设置按钮
        settings_btn = QPushButton("系统设置")
        settings_btn.clicked.connect(self.open_system_settings)
        settings_btn.setFont(button_font)  # 使用已有的按钮字体
        layout.addWidget(settings_btn)

    def open_system_settings(self):
        settings_dialog = SystemSettingsDialog()
        settings_dialog.exec()

    def load_users(self):
        cursor = user_manager.conn.cursor()
        cursor.execute("SELECT username, is_admin FROM users")
        users = cursor.fetchall()

        self.table.setRowCount(len(users))
        for row, (username, is_admin) in enumerate(users):
            # 用户名
            self.table.setItem(row, 0, QTableWidgetItem(username))

            # 权限状态
            status_item = QTableWidgetItem("管理员" if is_admin else "普通用户")
            self.table.setItem(row, 1, status_item)

            # 操作按钮
            toggle_btn = QPushButton("切换权限")
            toggle_btn.clicked.connect(
                lambda checked=False, u=username: self.toggle_admin(u)  # 关键修复
            )
            self.table.setCellWidget(row, 2, toggle_btn)

    def toggle_admin(self, username):
        cursor = user_manager.conn.cursor()
        cursor.execute('''
            UPDATE users SET is_admin = NOT is_admin 
            WHERE username=?
        ''', (username,))
        user_manager.conn.commit()
        self.load_users()
        QMessageBox.information(self, "成功", "权限已更新")