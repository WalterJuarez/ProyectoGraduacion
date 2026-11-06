"""Persistencia de despachos de Diesel Villa Nueva."""
from datetime import date
from models.db import Database


def _text(value, default=""):
    if value is None:
        return default
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    return str(value).strip()


def _number(value, field_name, default=None):
    if value is None or _text(value) == "":
        if default is not None:
            return float(default)
        raise ValueError(f"El campo {field_name} no tiene valor.")
    if isinstance(value, bool):
        return float(int(value))
    raw = _text(value).replace(",", ".")
    try:
        return float(raw)
    except (TypeError, ValueError):
        raise ValueError(f"El campo {field_name} no es numérico: {raw!r}")


class DispatchRepository:
    """Inserta un despacho en DVN1_DESPACHOS usando parámetros SQL."""

    @staticmethod
    def insert_dispatch(data):
        # Mapeo según las etiquetas y direcciones del primer puesto en la UI:
        # 2 piloto, 3 código, 4 galones Modbus, 5 galones pulsos,
        # 6 correlativo, 7 densidad, 8 temperatura, 11 unidad, 12 kilometraje.
        pilot = _text(data.get("txt_variable2"))
        employee_code = _text(data.get("txt_variable3"), "0") or "0"
        unit = _text(data.get("txt_variable11")) or None

        if not pilot:
            raise ValueError("No se guardó el despacho: el campo PILOTO está vacío.")

        values = (
            unit,
            pilot,
            _number(data.get("txt_variable4"), "GALONES_MODBUS"),
            _number(data.get("txt_variable5"), "GALONES_PULSOS"),
            _number(data.get("txt_variable7"), "DENSIDAD"),
            _number(data.get("txt_variable8"), "TEMPERATURA"),
            _number(data.get("txt_variable6"), "CORRELATIVO"),
            date.today(),
            employee_code,
            _number(data.get("txt_variable12"), "KILOMETRAJE_ACTUAL"),
        )

        sql = """INSERT INTO DVN1_DESPACHOS
            (UNIDAD, PILOTO, GALONES_MODBUS, GALONES_PULSOS, DENSIDAD,
             TEMPERATURA, CORRELATIVO, FECHA, COD_EMPLEADO, KILOMETRAJE_ACTUAL)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            cursor = connection.cursor()
            cursor.execute(sql, values)
            connection.commit()
            return cursor.lastrowid
        except Exception:
            if connection is not None:
                connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()
