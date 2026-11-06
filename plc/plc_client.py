from pylogix import PLC


class PLCClient:

    def __init__(self, ip, slot=0):
        self.ip = ip
        self.slot = slot
        self.plc = PLC()
        self.plc.IPAddress = self.ip
        self.plc.ProcessorSlot = self.slot  # 🔥 IMPORTANTE

    def connect(self):
        try:
            print(f"Intentando conectar a {self.ip} slot {self.slot}...")

            test = self.plc.Read("N7:0")

            print("Status:", test.Status)

            if test.Status == "Success":
                print("✅ Conectado al PLC")
                return True
            else:
                print("❌ Error conexión PLC:", test.Status)
                return False

        except Exception as e:
            print("❌ Error conexión PLC:", e)
            return False

    def read(self, tag):
        try:
            result = self.plc.Read(tag)

            if result.Status == "Success":
                return result.Value
            print(f"Error leyendo {tag}: {result.Status}")
            return None

        except Exception as e:
            print(f"Error leyendo {tag}:", e)
            return None

    def write(self, tag, value):
        try:
            result = self.plc.Write(tag, value)

            if result.Status != "Success":
                print(f"Error escribiendo {tag}: {result.Status}")

        except Exception as e:
            print(f"Error escribiendo {tag}:", e)