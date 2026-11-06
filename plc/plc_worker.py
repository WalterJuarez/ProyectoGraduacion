from PySide6.QtCore import QThread, Signal
import time


class PLCWorker(QThread):
    data_updated = Signal(dict)

    def __init__(self, service, ui):
        super().__init__()
        self.service = service
        self.ui = ui
        self.running = True

    def run(self):
        while self.running:
            try:
                data = {}

                for i in range(1, 14):

                    var_name = f"txt_variable{i}"
                    if hasattr(self.ui, var_name):
                        tag = getattr(self.ui, var_name).text()
                        value = self.service.read(tag)
                        data[var_name] = value

                    var_name2 = f"{var_name}_2"
                    if hasattr(self.ui, var_name2):
                        tag = getattr(self.ui, var_name2).text()
                        value = self.service.read(tag)
                        data[var_name2] = value

                self.data_updated.emit(data)

            except Exception as e:
                print("Error PLCWorker:", e)

            self.msleep(1000)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()  # 🔥 MUY IMPORTANTE