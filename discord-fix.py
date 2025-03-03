from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QDesktopWidget, QMainWindow
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, Qt, QSize
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtGui import QIcon
import sys
import os
import subprocess


class Bridge(QObject):
    def __init__(self, bat_folder="discord-fix-service/"):
        super().__init__()
        self.bat_folder = bat_folder
        self.process = None 

    @pyqtSlot(result='QStringList')
    def getBatFiles(self):
        try:
            return [f for f in os.listdir(self.bat_folder) if f.endswith(".bat")]
        except Exception as e:
            print(f"Ошибка при получении .bat файлов: {e}")
            return []

    @pyqtSlot(str, result='QVariantMap')
    def runBatFile(self, bat_file):
        try:
            if self.process is None:
                bat_path = os.path.join(self.bat_folder, bat_file)
                self.process = subprocess.Popen(["cmd.exe", "/c", bat_path], shell=True)
                return {"success": True, "message": f"Режим {os.path.splitext(bat_file)[0]} успешно запущен."}
            else:
                if self.process:
                    self.process.terminate()
                    self.process.wait() 
                    self.process = None
                self.killWinwsProcess()
                if self.checkWinwsProcess():
                    return {"success": False, "error": "Процесс discord-fix-service.exe все еще запущен."}
                else:
                    return {"success": True, "message": f"Режим {os.path.splitext(bat_file)[0]} остановлен."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def killWinwsProcess(self):
        try:
            subprocess.run(["taskkill", "/f", "/im", "discord-fix-service.exe", "/T"], shell=True)
        except Exception as e:
            print(f"Ошибка при завершении процесса discord-fix-service.exe: {e}")

    @pyqtSlot(result='bool')
    def checkWinwsProcess(self):
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq discord-fix-service.exe"],
                capture_output=True,
                text=True,
                shell=True
            )
            return "discord-fix-service.exe" in result.stdout
        except Exception as e:
            print(f"Ошибка при проверке процесса discord-fix-service.exe: {e}")
            return False


class WebApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initTray()
        self.isQuitting = False  
        self.web_view = None 
        self.initWebView()  

    def initUI(self):
        self.setWindowTitle("Discord-fix 1.0.0.1.02.03.2025")
        self.setFixedSize(QSize(800, 600))
        self.setWindowIcon(QIcon(".web/icons/icon.ico"))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinimizeButtonHint & ~Qt.WindowMaximizeButtonHint)
        self.move(
            (QDesktopWidget().screenGeometry().width() - self.frameGeometry().width()) // 2,
            (QDesktopWidget().screenGeometry().height() - self.frameGeometry().height()) // 2
        )

    def initWebView(self):
        if self.web_view:
            self.web_view.deleteLater()  
        self.web_view = QWebEngineView(self)
        self.setCentralWidget(self.web_view)
        self.bridge = Bridge()
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        html_path = os.path.join(os.getcwd(), ".web/index.html")
        self.web_view.setUrl(QUrl.fromLocalFile(html_path))

    def initTray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon(".web/icons/icon.ico"))
        self.tray_menu = QMenu()
        self.toggle_window_action = self.tray_menu.addAction("Скрыть окно")
        self.toggle_window_action.triggered.connect(self.toggleWindow)
        self.tray_menu.addSeparator()
        quit_action = self.tray_menu.addAction("Выход")
        quit_action.triggered.connect(self.quitApp)
        self.tray.setContextMenu(self.tray_menu)
        self.tray.show()
        self.tray.activated.connect(self.trayIconClicked)

    def toggleWindow(self):
        if self.isVisible():
            self.hide()
        else:
            self.showNormal()

    def updateToggleWindowAction(self):
        if self.isVisible():
            self.toggle_window_action.setText("Скрыть окно")
        else:
            self.toggle_window_action.setText("Показать окно")

    def trayIconClicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.toggleWindow()

    def quitApp(self):
        self.isQuitting = True
        self.tray.hide() 
        self.killDiscordFixService() 
        QApplication.quit()

    def closeEvent(self, event):
        if not self.isQuitting:
            event.ignore()
            self.hide()
        else:
            self.killDiscordFixService()
            event.accept()

    def killDiscordFixService(self):
        try:
            subprocess.run(["taskkill", "/f", "/im", "discord-fix-service.exe", "/T"], shell=True)
        except Exception as e:
            print(f"Ошибка при завершении процесса discord-fix-service.exe: {e}")

    def hide(self):
        super().hide()
        if self.web_view:
            self.web_view.setUrl(QUrl("about:blank")) 
            self.web_view.deleteLater()
            self.web_view = None
        self.updateToggleWindowAction()

    def showNormal(self):
        super().showNormal()
        if not self.web_view:
            self.initWebView()  
        self.updateToggleWindowAction()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet('''QMenuBar {
                background-color: #2c2f33;
                color: #ffffff;
                padding: 5px;
            }

            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }

            QMenuBar::item:selected {
                background-color: #40444b;
            }

            QMenu {
                background-color: #2c2f33;
                color: #ffffff;
                border: 1px solid #40444b;
                padding: 5px;
            }

            QMenu::item {
                padding: 5px 20px;
                background-color: transparent;
            }

            QMenu::item:selected {
                background-color: #40444b;
            }

            QMenu::separator {
                height: 1px;
                background-color: #40444b;
                margin: 5px 0;
            }''')

    import pywinstyles
    web_app = WebApp()
    pywinstyles.apply_style(web_app, 'dark')
    web_app.show()
    sys.exit(app.exec_())
