import sys
import time
import cv2
import dlib
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox,
    QHBoxLayout, QSpacerItem, QSizePolicy, QGroupBox, QFileDialog
)
from PySide6.QtGui import QPixmap, QIcon, QImage, QMovie, QFont
from PySide6.QtCore import Qt, QThread, Signal, QTimer,QFile, QTextStream
from Backend.functions import Functions 
from Backend.model_manager import model_manager

class ModelLoaderThread(QThread):
    models_loaded = Signal()

    def __init__(self):
        super().__init__()
        self.models_loaded_flag = False
        

    def run(self):
        if not self.models_loaded_flag:
            model_manager.load_models()
            self.models_loaded_flag = True

        self.models_loaded.emit()

class OnlineWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Load the style sheet
        style_file = QFile("assets/Style/style.qss")
        if style_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(style_file)
            self.setStyleSheet(stream.readAll())
        else:
            print("Failed to open style file:", style_file.errorString())

        self.last_prediction_time = time.time()
        self.frame_counter = 0
        self.prediction_interval = 150 #frames
        self.predicted_text = ""

        self.setWindowTitle("视频模式")
        self.setFixedSize(800, 500)
        icon_path = "assets/Icons/favicon-favicon-black.png"
        self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout()

        # Button layout for "Go Online!" and "Switch to Offline Mode" buttons
        button_layout = QHBoxLayout()

        # Add stretch before the buttons
        button_layout.addStretch()

        # Go online!
        self.detection_button = QPushButton("选择视频!")
        self.detection_button.setDisabled(True)
        self.detection_button.setFixedWidth(150)
        self.detection_button.clicked.connect(self.start_video_capture)
        button_layout.addWidget(self.detection_button, alignment=Qt.AlignTop | Qt.AlignCenter)


        offline_button = self.create_offline_button()
        offline_button.setFixedWidth(150)
        button_layout.addWidget(offline_button, alignment=Qt.AlignTop | Qt.AlignCenter)

        # Add stretch after the buttons
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Split the window into two columns
        columns_layout = QHBoxLayout()

        # Left column (logo, status, instructions)
        left_column_layout = QVBoxLayout()

        # Add vertical spacer at the top
        left_column_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Logo and Status layout
        logo_status_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/Icons/favicon-white.png")
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_status_layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        # Status Text
        self.status_label = QLabel("加载中...")
        self.status_label.setAlignment(Qt.AlignCenter)
        logo_status_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        left_column_layout.addLayout(logo_status_layout)

        # Instruction Text
        instruction_label = QLabel("请确保在采光充足的地方并且直视摄像头。")
        instruction_label.setAlignment(Qt.AlignCenter)  # Center align instruction label
        left_column_layout.addWidget(instruction_label)

        # Results Box
        self.results_groupbox = QGroupBox("结果")
        self.results_box = QVBoxLayout(self.results_groupbox)

        # Predicted Shape
        self.predicted_shape_label = QLabel("预测脸型:")
        self.results_box.addWidget(self.predicted_shape_label)

        # Predicted Gender
        self.predicted_gender_label = QLabel("预测性别:")
        self.results_box.addWidget(self.predicted_gender_label)

        # Predicted Emotion
        self.predicted_emotion_label = QLabel("预测表情:")
        self.results_box.addWidget(self.predicted_emotion_label)

        # 添加导出按钮
        self.export_button = QPushButton("导出记录")
        self.export_button.clicked.connect(self.export_history)
        self.results_box.addWidget(self.export_button)

        # 添加历史记录存储
        self.history_records = []
        self.last_prediction = {}

        # Hide the results box initially
        self.results_groupbox.hide()

        left_column_layout.addWidget(self.results_groupbox)

        # Add vertical spacer at the bottom
        left_column_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        columns_layout.addLayout(left_column_layout)

        # Add a vertical spacer item
        columns_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Right column (video capture)
        right_column_layout = QVBoxLayout()

        # Add vertical spacer at the top
        right_column_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # QLabel for displaying the GIF
        self.movie = QMovie("assets/Icons/loading.gif")
        self.gif_label = QLabel(self)
        self.gif_label.setMovie(self.movie)
        self.movie.start()
        self.gif_label.setAlignment(Qt.AlignCenter)  # Set alignment to center
        right_column_layout.addWidget(self.gif_label, alignment=Qt.AlignCenter)  # Set alignment for the widget

        # Add vertical spacer in the middle
        right_column_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Video display
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)  # Center align video label
        right_column_layout.addWidget(self.video_label)

        columns_layout.addLayout(right_column_layout)

        layout.addLayout(columns_layout)

        self.setLayout(layout)
        # Model loader thread
        self.model_loader_thread = ModelLoaderThread()
        self.model_loader_thread.models_loaded.connect(self.on_models_loaded)
        self.model_loader_thread.start()

        # Video capture
        self.video_capture = None
        self.face_detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor("Models/shape_predictor_68_face_landmarks.dat")

        # Timer for controlling frame rate
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_frame)

        # Connect key press event to the function that handles it
        self.keyPressEvent = self.handle_key_press

        # 设置结果标签字体
        result_font = QFont()
        result_font.setPointSize(14)
        result_font.setBold(True)
        self.predicted_shape_label.setFont(result_font)
        self.predicted_emotion_label.setFont(result_font)
        self.predicted_gender_label.setFont(result_font)

    def on_models_loaded(self):
        self.status_label.setText("模型已加载!")
        QMessageBox.information(self, "Notification", "模型已加载! 你可以使用线上模型了.", QMessageBox.Ok)
        self.detection_button.setEnabled(True)

        # Replace the GIF with the video_label
        self.movie.stop()
        self.gif_label.hide()
        self.video_label.show()

        # Enable the results box
        self.results_groupbox.setEnabled(True)

    def create_offline_button(self):
        offline_button = QPushButton("转换为离线")
        offline_button.clicked.connect(self.switch_to_offline_mode)
        offline_button.setFixedWidth(150)
        return offline_button

    def start_video_capture(self):
        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

        self.detection_button.setDisabled(True)
        self.status_label.setText("检测中...")

        # Start the timer to control frame rate
        self.timer.start()

        # show the results box
        self.results_groupbox.show()

    def handle_key_press(self, event):
        if event.key() == Qt.Key_Q:
            self.stop_video_capture()
            # hide the results box
            self.results_groupbox.hide()

    def stop_video_capture(self):
        if self.video_capture is not None and self.video_capture.isOpened():
            self.video_capture.release()
            self.timer.stop()  # Stop the timer
            self.video_label.clear()
            self.status_label.setText("视频捕捉已停止。")
            self.detection_button.setEnabled(True)

    def update_video_frame(self):
        ret, frame = self.video_capture.read()
        predicted_shape = ""
        predicted_gender = ""
        
        if ret:
            # Draw on the frame without color conversion for capturing in real color
            faces = self.face_detector(frame)

            for face in faces:
                landmarks = self.landmark_predictor(frame, face)
                self.draw_landmarks(frame, landmarks)

                x, y, w, h = face.left(), face.top(), face.width(), face.height()

                # Change rectangle color to black
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)

                # Calculate position for displaying predictions
                text_x = x
                text_y = y + h + 20

            # Check if it's time to make predictions
            if self.frame_counter % self.prediction_interval == 0:
                # Reset the frame counter
                self.frame_counter = 0

                # Make predictions
                predicted_shape, predictions = Functions.predict_shape("online", frame, model_manager.shape_model)
                predicted_gender, predictions = Functions.predict_gender("online", frame, model_manager.gender_model)
                predicted_emotion, predictions = Functions.predict_emotion("online", frame, model_manager.emotion_model)
                # Update the predicted text variable
                self.predicted_text = f"Shape: {predicted_shape}\nGender: {predicted_gender}\nEmotion: {predicted_emotion}"

                # Update the labels in the results box
                self.predicted_shape_label.setText(f"脸型预测: {predicted_shape}")
                self.predicted_gender_label.setText(f"性别预测: {predicted_gender}")
                self.predicted_emotion_label.setText(f"表情预测: {predicted_emotion}")

                # 存储当前预测结果
                self.last_prediction = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "shape": predicted_shape,
                    "gender": predicted_gender,
                    "emotion": predicted_emotion
                }
                self.history_records.append(self.last_prediction)

            # Display the predicted values with thick red text
            for i, line in enumerate(self.predicted_text.split('\n')):
                # Change text color to red and make it thick
                cv2.putText(frame, line, (text_x, text_y + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2,
                            cv2.LINE_AA)

        # Convert back to BGR before displaying
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.video_label.setPixmap(pixmap)
        self.video_label.setScaledContents(True)

        # Increment the frame counter for the next iteration
        self.frame_counter += 1


    def draw_landmarks(self, frame, landmarks):
        for i in range(68):
            x, y = landmarks.part(i).x, landmarks.part(i).y
            cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

    def switch_to_offline_mode(self):
        if self.video_capture is not None and self.video_capture.isOpened():
            self.stop_video_capture()

        from Backend.offline import OfflineWindow
        self.offline_window = OfflineWindow()
        self.offline_window.show()
        self.close()

    def export_history(self):
        if not self.history_records:
            QMessageBox.warning(self, "警告", "没有可导出的记录", QMessageBox.Ok)
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存历史记录",
            "",
            "CSV文件 (*.csv);;文本文件 (*.txt)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("时间戳,脸型,性别,表情\n")
                    for record in self.history_records:
                        f.write(f"{record['timestamp']},{record['shape']},{record['gender']},{record['emotion']}\n")
                QMessageBox.information(self, "成功", "历史记录已保存!", QMessageBox.Ok)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}", QMessageBox.Ok)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    online_window = OnlineWindow()
    online_window.show()
    sys.exit(app.exec())

