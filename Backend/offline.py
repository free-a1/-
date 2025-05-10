import time  # 用于生成时间戳
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QHBoxLayout, QGroupBox, QFormLayout, QMessageBox
)
from PySide6.QtGui import QPixmap, QIcon, QFont
from PySide6.QtCore import Qt, QThread, Signal,QFile, QTextStream
from Backend.model_manager import model_manager
from Backend.functions import Functions 

class ModelLoaderThread(QThread):
    models_loaded = Signal()

    def __init__(self):
        super().__init__()
        self.models_loaded_flag = False  # Flag indicating whether the models are loaded

    def run(self):
        if not self.models_loaded_flag:
            # Load the models only if they are not already loaded
            model_manager.load_models()

            # Update the flag to indicate that models are loaded
            self.models_loaded_flag = True

        # Notify that models are loaded
        self.models_loaded.emit()

class OfflineWindow(QWidget):
    def __init__(self):
        super().__init__()

        # === 新增代码：设置基础字体 ===
        base_font = QFont()
        base_font.setPointSize(12)  # 全局默认字号
        self.setFont(base_font)  # 应用于整个窗口

        # Load the style sheet
        style_file = QFile("assets\\Style\\style.qss")
        if style_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(style_file)
            self.setStyleSheet(stream.readAll())
        else:
            print("Failed to open style file:", style_file.errorString())

        self.setWindowTitle("照片模式")
        self.setFixedSize(800, 500)
        icon_path = "assets/Icons/favicon-favicon-black.png"
        self.setWindowIcon(QIcon(icon_path))

        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        layout = QVBoxLayout()

        upload_button = QPushButton("上传图片")
        upload_button.clicked.connect(self.upload_image)
        upload_button.setFixedWidth(150)

        online_button = self.create_online_button()

        upload_layout = QHBoxLayout()
        upload_layout.addWidget(upload_button, alignment=Qt.AlignHCenter)
        upload_layout.addWidget(online_button, alignment=Qt.AlignHCenter)

        layout.addLayout(upload_layout)
        second_row_layout = QHBoxLayout()
        self.uploaded_image_label = QLabel()
        self.uploaded_image_label.setAlignment(Qt.AlignCenter)
        self.uploaded_image_label.setScaledContents(True)
        second_row_layout.addWidget(self.uploaded_image_label)

        self.preprocessed_image_label = QLabel()
        self.preprocessed_image_label.setAlignment(Qt.AlignCenter)
        self.preprocessed_image_label.setScaledContents(True)
        second_row_layout.addWidget(self.preprocessed_image_label)
        layout.addLayout(second_row_layout)

        third_row_layout = QHBoxLayout()

        self.predict_shape_button = QPushButton("预测脸型")
        self.predict_gender_button = QPushButton("预测性别")
        self.predict_emotion_button = QPushButton("预测表情")

        # 在预测按钮布局中添加导出按钮
        prediction_buttons_layout = QVBoxLayout()
        prediction_buttons_layout.addWidget(self.predict_shape_button)
        prediction_buttons_layout.addWidget(self.predict_gender_button)
        prediction_buttons_layout.addWidget(self.predict_emotion_button)

        for button in [self.predict_shape_button, self.predict_gender_button, self.predict_emotion_button]:
            button.setFixedWidth(160)
            button.setEnabled(False)
            button.hide()

        prediction_buttons_layout = QVBoxLayout()
        prediction_buttons_layout.addWidget(self.predict_shape_button)
        prediction_buttons_layout.addWidget(self.predict_gender_button)
        prediction_buttons_layout.addWidget(self.predict_emotion_button)
        third_row_layout.addLayout(prediction_buttons_layout)

        # Connect the predict buttons to their respective methods
        self.predict_shape_button.clicked.connect(self.predict_shape)
        self.predict_gender_button.clicked.connect(self.predict_gender)
        self.predict_emotion_button.clicked.connect(self.predict_emotion)

        self.results_group_box = QGroupBox("结果")
        self.results_layout = QFormLayout()

        self.loading_label = QLabel("加载中...")
        self.results_layout.addRow("Status:", self.loading_label)

        # Create QLabel widgets for predictions
        self.shape_prediction_label = QLabel("脸型预测:")
        self.gender_prediction_label = QLabel("性别预测:")
        self.emotion_prediction_label = QLabel("表情预测:")
        # +++ 新增导出按钮 +++
        self.export_button = QPushButton("导出结果")
        self.export_button.setFixedWidth(160)
        self.export_button.setEnabled(False)  # 初始不可用
        self.export_button.clicked.connect(self.export_results)
        prediction_buttons_layout.addWidget(self.export_button)
        third_row_layout.addLayout(prediction_buttons_layout)

        # Add the QLabel widgets to the layout and hide them initially
        self.results_layout.addRow(self.shape_prediction_label)
        self.results_layout.addRow(self.gender_prediction_label)
        self.results_layout.addRow(self.emotion_prediction_label)
        self.shape_prediction_label.hide()
        self.gender_prediction_label.hide()
        self.emotion_prediction_label.hide()

        self.results_group_box.setLayout(self.results_layout)
        self.results_group_box.hide()

        third_row_layout.addWidget(self.results_group_box)
        layout.addLayout(third_row_layout)

        self.model_loader_thread = ModelLoaderThread()
        self.model_loader_thread.models_loaded.connect(self.on_models_loaded)

        self.file_path = None  # Store the file path for prediction

        self.setLayout(layout)

        # 添加结果存储变量
        self.current_results = {
            'shape': '未检测',
            'gender': '未检测',
            'emotion': '未检测'
        }

        # === 结果标签字体设置 ===
        result_font = QFont()
        result_font.setPointSize(13)  # 比基础字号大1pt

        self.shape_prediction_label.setFont(result_font)
        self.gender_prediction_label.setFont(result_font)
        self.emotion_prediction_label.setFont(result_font)


    def upload_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.JPG)")
        if file_path:
            print(f"File Path: {file_path}")
            self.file_path = file_path

            pixmap = QPixmap(file_path)

            resized_uploaded_pixmap = pixmap.scaled(300, 400, Qt.KeepAspectRatio)
            self.uploaded_image_label.setPixmap(resized_uploaded_pixmap)

            result = Functions.preprocess("offline",file_path)

            if result is not None:
                processed_image_path, normalized_face = result

                processed_pixmap = QPixmap(processed_image_path)
                resized_processed_pixmap = processed_pixmap.scaled(300, 400, Qt.KeepAspectRatio)
                self.preprocessed_image_label.setPixmap(resized_processed_pixmap)

                # Clear existing predictions
                self.clear_predictions("脸型预测")
                self.clear_predictions("性别预测")
                self.clear_predictions("表情预测")

                # Clear text of prediction labels
                self.shape_prediction_label.setText("脸型预测:")
                self.gender_prediction_label.setText("性别预测:")
                self.emotion_prediction_label.setText("表情预测:")

                self.predict_shape_button.show()
                self.predict_gender_button.show()
                self.predict_emotion_button.show()
                self.results_group_box.show()

                if not self.model_loader_thread.models_loaded_flag:
                    # If models are not loaded, start the thread to load them
                    self.model_loader_thread.start()
                else:
                    # Models are already loaded, update the UI accordingly
                    self.on_models_loaded()

            else:
                self.preprocessed_image_label.setPixmap(QPixmap())
                self.predict_shape_button.hide()
                self.predict_gender_button.hide()
                self.predict_emotion_button.hide()
                self.results_group_box.hide()

                error_message = "处理图像时出错。请选择一个有效的图像。"
                QMessageBox.critical(self, "Error", error_message, QMessageBox.Ok)

    def on_models_loaded(self):
        self.loading_label.setText("模型已加载!")
        for button in [self.predict_shape_button, self.predict_gender_button, self.predict_emotion_button]:
            button.setEnabled(True)
        self.results_group_box.show()

        # Show prediction labels when models are loaded
        self.shape_prediction_label.show()
        self.gender_prediction_label.show()
        self.emotion_prediction_label.show()

        QMessageBox.information(self, "Notification", "模型已加载!", QMessageBox.Ok)

    def predict_shape(self):
        if model_manager.shape_model is not None:
            predicted_class, predictions = Functions.predict_shape("offline",self.file_path, model_manager.shape_model)
            # Display the prediction under the "Prediction" section in the results box
            self.display_prediction("脸型预测", predicted_class, predictions, self.shape_prediction_label)
        else:
            QMessageBox.warning(self, "警告", "模型未加载.", QMessageBox.Ok)

    def predict_gender(self):
        if model_manager.gender_model and model_manager.recognizer is not None:
            predicted_class, predictions = Functions.predict_gender("offline", self.file_path,model_manager.gender_model)
            try:
                labels = 'Models/labels-vgg.txt'
                recognized = Functions.recognizer("offline", self.file_path, model_manager.recognizer, labels)
                # Display the prediction under the "Prediction" section in the results box
                self.display_prediction("性别预测", predicted_class + "     " + recognized, predictions, self.gender_prediction_label)
            except Exception as e:
                # Handle the exception and display a warning
                QMessageBox.warning(self, "警告", f"O只检测到性别，由于图像质量差，无法进行识别 ", QMessageBox.Ok)
                self.display_prediction("性别预测", predicted_class , predictions, self.gender_prediction_label)
        else:
            QMessageBox.warning(self, "警告", "性别模型未加载.", QMessageBox.Ok)


    def predict_emotion(self):
        # Uncomment the following lines when the emotion model is available
        if model_manager.emotion_model is not None:
             predicted_class, predictions = Functions.predict_emotion("offline",self.file_path, model_manager.emotion_model)
             # Display the prediction under the "Prediction" section in the results box
             self.display_prediction("表情预测", predicted_class, predictions, self.emotion_prediction_label)
        else:
            QMessageBox.warning(self, "警告", "模型未加载.", QMessageBox.Ok)

    def clear_predictions(self, title):
        # Clear existing predictions with the specified title
        for i in reversed(range(self.results_layout.rowCount())):
            item = self.results_layout.itemAt(i, QFormLayout.LabelRole)
            if item is not None and title in item.widget().text():
                self.results_layout.removeRow(i)

    def display_prediction(self, title, predicted_class, predictions, label_widget):
        # Update the QLabel widget with the prediction
        label_widget.setText(f"{title}:  {predicted_class}")
        # +++ 新增数据存储逻辑 +++
        if '脸型' in title:
            self.current_results['shape'] = predicted_class
        elif '性别' in title:
            self.current_results['gender'] = predicted_class
        elif '表情' in title:
            self.current_results['emotion'] = predicted_class

        # 当任意预测完成时激活导出按钮
        if any(val != '未检测' for val in self.current_results.values()):
            self.export_button.setEnabled(True)
    
    def create_online_button(self):
        online_button = QPushButton("选择视频模式")
        online_button.clicked.connect(self.switch_to_online_mode)
        online_button.setFixedWidth(150)
        return online_button

    def switch_to_online_mode(self):
        from Backend.online import OnlineWindow
        self.online_window = OnlineWindow()
        self.online_window.show()
        self.close()

    # +++ 新增导出方法 +++
    def export_results(self):
        # 弹出文件保存对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存结果",
            f"识别结果_{time.strftime('%Y%m%d%H%M%S')}",  # 默认带时间戳的文件名
            "CSV文件 (*.csv);;文本文件 (*.txt)"
        )

        if not file_path:
            return  # 用户取消保存

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # 写入CSV头
                f.write("检测时间,脸型预测,性别预测,表情预测\n")
                # 写入数据
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')},")
                f.write(f"{self.current_results['shape']},")
                f.write(f"{self.current_results['gender']},")
                f.write(f"{self.current_results['emotion']}\n")

            QMessageBox.information(self, "成功", f"结果已保存至:\n{file_path}", QMessageBox.Ok)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败:\n{str(e)}", QMessageBox.Ok)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    offline_window = OfflineWindow()
    offline_window.show()
    sys.exit(app.exec())
