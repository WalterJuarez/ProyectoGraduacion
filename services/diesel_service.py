from pycomm3 import SLCDriver


class DieselService:

    def __init__(self, ip):
        self.ip = ip
        self.plc = None

    def connect(self):
        try:
            self.plc = SLCDriver(self.ip)
            self.plc.open()

            if self.plc.connected:
                print("✅ PLC conectado")
                return True
            else:
                print("❌ PLC no conectado")
                return False

        except Exception as e:
            print("❌ Error conexión:", e)
            return False

    def read(self, tag):
        try:
            r = self.plc.read(tag)
            return r.value if r else None
        except Exception as e:
            print(f"Error leyendo {tag}: {e}")
            return None