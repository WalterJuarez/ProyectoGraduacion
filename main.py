
import contextlib
import sys

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QThread, Signal

from services.diesel_service import DieselService
from services.despacho_servicio import DispatchRepository
from ui_gen.despacho_diesel_ui import Ui_frm_principal_dieselvn


# Cargar las variables de conexión desde .env
load_dotenv()

IP_PLC = "10.24.24.156"


# =========================
# WORKER DEL PLC
# =========================
class PLCWorker(QThread):
    data_updated = Signal(dict)

    def __init__(self, service, ui):
        super().__init__()

        self.service = service
        self.ui = ui
        self.running = True

        # Control del flanco de subida de GUARDAR
        self._guardar_initialized = False
        self._guardar_previous = False

    @staticmethod
    def _is_active(value):
        """Convierte una señal del PLC en un estado booleano."""
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip().lower()

            if value in {"1", "true", "on", "yes"}:
                return True

            if value in {"0", "false", "off", "no", ""}:
                return False

            return None

        if isinstance(value, bool):
            return value

        try:
            return float(value) != 0
        except (TypeError, ValueError):
            return None

    def _guardar_despacho(self, data):
        """
        Registra un despacho una sola vez por flanco 0 -> 1.
        La señal se obtiene de txt_variable10.
        """
        estado_actual = self._is_active(
            data.get("txt_variable10")
        )

        # Si la lectura falla, no modificar el estado anterior.
        if estado_actual is None:
            return

        # Al arrancar, no guardar accidentalmente un despacho
        # si la señal ya se encuentra activa.
        if not self._guardar_initialized:
            self._guardar_previous = estado_actual
            self._guardar_initialized = True
            return

        # Detectar transición de inactivo a activo.
        if estado_actual and not self._guardar_previous:
            try:
                consecutivo = DispatchRepository.insert_dispatch(data)

                print(
                    "DESPACHO REGISTRADO CORRECTAMENTE. "
                    f"CONSECUTIVO={consecutivo}"
                )

            except Exception as error:
                print(
                    "ERROR AL REGISTRAR EL DESPACHO EN MYSQL: "
                    f"{error}"
                )

        self._guardar_previous = estado_actual

    def run(self):
        while self.running:
            try:
                data = {}

                # Leer las variables de los dos puestos.
                # Por ahora, solo se registra el primer puesto.
                for i in range(1, 14):
                    var_name = f"txt_variable{i}"

                    if hasattr(self.ui, var_name):
                        tag = getattr(self.ui, var_name).text().strip()

                        if tag:
                            data[var_name] = self.service.read(tag)
                        else:
                            data[var_name] = None

                    var_name2 = f"{var_name}_2"

                    if hasattr(self.ui, var_name2):
                        tag2 = getattr(
                            self.ui, var_name2
                        ).text().strip()

                        if tag2:
                            data[var_name2] = self.service.read(tag2)
                        else:
                            data[var_name2] = None

                # Guardar antes de emitir los datos a la interfaz.
                self._guardar_despacho(data)

                # Mantener la actualización de la interfaz original.
                self.data_updated.emit(data)

            except Exception as error:
                print(f"Error PLCWorker: {error}")

            self.msleep(1000)

    def stop(self):
        print("Deteniendo PLCWorker...")
        self.running = False
        self.wait()


# =========================
# VENTANA PRINCIPAL
# =========================
class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.ui = Ui_frm_principal_dieselvn()
        self.ui.setupUi(self)

        self.service = DieselService(IP_PLC)
        self.worker = None

        if not self.service.connect():
            print(
                "No se pudo conectar al PLC. "
                "La lectura y el registro no están activos."
            )
            return

        self.worker = PLCWorker(
            self.service,
            self.ui
        )

        self.worker.data_updated.connect(
            self.update_ui
        )

        self.worker.start()

    # =========================
    # ACTUALIZAR INTERFAZ
    # =========================
    def update_ui(self, data):

        for key, value in data.items():

            textbox_name = key.replace(
                "variable", "valor"
            )

            if hasattr(self.ui, textbox_name):
                display_value = (
                    "" if value is None else str(value)
                )

                getattr(
                    self.ui, textbox_name
                ).setText(display_value)

            # Indicador de marcaje original
            if textbox_name == "txt_valor2":
                if hasattr(self.ui, "lbl_marcaje"):
                    self.ui.lbl_marcaje.setText(
                        "" if value is None else str(value)
                    )

            # LCD del despacho original
            if textbox_name == "txt_valor5":
                try:
                    numero = (
                        float(value)
                        if value is not None
                        else 0.0
                    )
                except (TypeError, ValueError):
                    numero = 0.0

                if hasattr(self.ui, "lcd_despacho1"):
                    self.ui.lcd_despacho1.display(numero)

    # =========================
    # CIERRE CORRECTO
    # =========================
    def closeEvent(self, event):
        print("Cerrando aplicación...")

        if self.worker is not None:
            self.worker.stop()

        with contextlib.suppress(Exception):
            if self.service.plc:
                self.service.plc.close()

        event.accept()


# =========================
# INICIO DE LA APLICACIÓN
# =========================
def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
