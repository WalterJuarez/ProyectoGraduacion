from pycomm3 import SLCDriver

IP = "10.24.24.156"


def main():
    print(f"Conectando a PLC SLC/MicroLogix en {IP}...\n")

    try:
        with SLCDriver(IP) as plc:

            print("✅ Conectado correctamente\n")

            tags = [
                "N7:0",
                "N7:1",
                "B3:0/0",
                "F8:5"
            ]

            for tag in tags:
                if result := plc.read(tag):
                    print(f"{tag} → {result.value}")
                else:
                    print(f"{tag} → ❌ Error")

    except Exception as e:
        print("❌ Error de conexión:", e)


if __name__ == "__main__":
    main()