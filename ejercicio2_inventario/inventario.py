
import sqlite3, os

# Uso de IA, Se implementó la IA para el formateo y el embellicimiento a la hora de mostrar por consola
# La logica, conexión a BD y funcionamiento general fue realizado por mi

DB = "inventario.db"


class Producto:
    def __init__(self, id, nombre, precio_base, stock, categoria):
        self.__id         = id
        self.__nombre     = nombre
        self.__precio_base = float(precio_base)
        self.__stock      = int(stock)
        self.__categoria  = categoria

    @property
    def id(self):          return self.__id
    @property
    def nombre(self):      return self.__nombre
    @property
    def precio_base(self): return self.__precio_base
    @property
    def stock(self):       return self.__stock
    @property
    def categoria(self):   return self.__categoria

    def _descuento_tipo(self, precio):
        return precio

    def calcular_precio_final(self):
        precio = self._descuento_tipo(self.__precio_base)
        if self.__stock > 50:
            precio *= 0.95
        if precio < 5000:
            print(f"  [!] Revision de Margen Necesaria: {self.__nombre}")
        return round(precio, 2)


class ProductoFisico(Producto):
    def __init__(self, id, nombre, precio_base, stock, categoria, peso_kg):
        super().__init__(id, nombre, precio_base, stock, categoria)
        self.__peso_kg = float(peso_kg)

    @property
    def peso_kg(self): return self.__peso_kg

    def _descuento_tipo(self, precio):
        return precio 


class ProductoDigital(Producto):
    def __init__(self, id, nombre, precio_base, stock, categoria, url):
        super().__init__(id, nombre, precio_base, stock, categoria)
        self.__url = url

    @property
    def url(self): return self.__url

    def _descuento_tipo(self, precio):
        return precio * 0.85


# ─── Base de datos ────────────────────────────────────────────────────────────

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS categoria (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS producto (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre      TEXT NOT NULL,
                precio_base REAL NOT NULL,
                stock       INTEGER NOT NULL DEFAULT 0,
                tipo        TEXT NOT NULL CHECK(tipo IN ('F','D')),
                categoria_id INTEGER REFERENCES categoria(id),
                peso_kg     REAL,
                url         TEXT
            );
        """)

def row_to_obj(r):
    if r["tipo"] == "F":
        return ProductoFisico(r["id"], r["nombre"], r["precio_base"], r["stock"],
                              r["categoria"] or "Sin categoria", r["peso_kg"] or 0)
    return ProductoDigital(r["id"], r["nombre"], r["precio_base"], r["stock"],
                           r["categoria"] or "Sin categoria", r["url"] or "")

# ─── Menu ─────────────────────────────────────────────────────────────────────

SEP = "-" * 60

def listar():
    sql = """
        SELECT p.*, COALESCE(c.nombre,'Sin categoria') AS categoria
        FROM producto p LEFT JOIN categoria c ON c.id = p.categoria_id
        ORDER BY p.tipo, p.nombre
    """
    with get_conn() as c:
        rows = c.execute(sql).fetchall()
    if not rows:
        print("  Sin productos."); return
    print(f"\n  {'ID':<4} {'Nombre':<22} {'Tipo':<8} {'Categoria':<14} {'Base':>9} {'Final':>9} {'Stock':>6}")
    print("  " + SEP)
    for r in rows:
        p = row_to_obj(r)
        pf = p.calcular_precio_final()
        tipo = "Digital" if r["tipo"] == "D" else "Fisico"
        low = " [LOW]" if p.stock < 10 else ""
        print(f"  {p.id:<4} {p.nombre:<22} {tipo:<8} {p.categoria:<14}"
              f" ${p.precio_base:>8,.0f} ${pf:>8,.0f} {p.stock:>6}{low}")

def agregar():
    tipo = input("  Tipo (F)isico / (D)igital: ").strip().upper()
    if tipo not in ("F", "D"):
        print("  [!] Tipo invalido."); return
    nombre = input("  Nombre: ").strip()
    precio = float(input("  Precio base: "))
    stock  = int(input("  Stock: "))
    cat    = input("  Categoria: ").strip() or "General"

    with get_conn() as c:
        row = c.execute("SELECT id FROM categoria WHERE nombre=?", (cat,)).fetchone()
        cat_id = row["id"] if row else c.execute(
            "INSERT INTO categoria (nombre) VALUES (?)", (cat,)).lastrowid

        if tipo == "F":
            peso = float(input("  Peso (kg): ") or 0)
            c.execute("INSERT INTO producto (nombre,precio_base,stock,tipo,categoria_id,peso_kg)"
                      " VALUES (?,?,?,?,?,?)", (nombre, precio, stock, "F", cat_id, peso))
        else:
            url = input("  URL de descarga: ").strip()
            c.execute("INSERT INTO producto (nombre,precio_base,stock,tipo,categoria_id,url)"
                      " VALUES (?,?,?,?,?,?)", (nombre, precio, stock, "D", cat_id, url))
    print("  [OK] Producto agregado.")

def eliminar():
    pid = input("  ID a eliminar: ").strip()
    with get_conn() as c:
        c.execute("DELETE FROM producto WHERE id=?", (pid,))
    print("  [OK] Eliminado.")

def stock_bajo():
    sql = """
        SELECT p.nombre, p.stock, COALESCE(c.nombre,'Sin categoria') AS categoria
        FROM producto p LEFT JOIN categoria c ON c.id = p.categoria_id
        WHERE p.stock < 10 ORDER BY p.stock
    """
    with get_conn() as c:
        rows = c.execute(sql).fetchall()
    if not rows:
        print("  No hay productos con stock bajo.")
    for r in rows:
        print(f"  {r['nombre']:<25} stock: {r['stock']:>4}  cat: {r['categoria']}")

def promedio_categorias():
    sql = """
        SELECT c.nombre AS categoria, ROUND(AVG(p.precio_base),2) AS promedio, COUNT(*) AS total
        FROM producto p JOIN categoria c ON c.id = p.categoria_id
        GROUP BY c.nombre ORDER BY promedio DESC
    """
    with get_conn() as c:
        rows = c.execute(sql).fetchall()
    if not rows:
        print("  No hay datos.")
    for r in rows:
        print(f"  {r['categoria']:<20} promedio: ${r['promedio']:>10,.0f}  ({r['total']} productos)")

def menu():
    os.system("clear")
    while True:
        print(f"\n{SEP}")
        print("  EMAST INVENTARIO")
        print(SEP)
        print("  1. Listar productos")
        print("  2. Agregar producto")
        print("  3. Eliminar producto")
        print("  4. [SQL] Stock bajo (< 10)")
        print("  5. [SQL] Promedio por categoria")
        print("  0. Salir")
        print(SEP)
        op = input("  Opcion: ").strip()
        if   op == "1": listar()
        elif op == "2": agregar()
        elif op == "3": eliminar()
        elif op == "4": stock_bajo()
        elif op == "5": promedio_categorias()
        elif op == "0": break
        else: print("  [!] Opcion invalida.")
        input("\n  [ENTER para continuar]")
        os.system("clear")

if __name__ == "__main__":
    init_db()
    menu()
