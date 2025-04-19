import json
import os
from datetime import datetime
#https://turestaurante.com/menu/mesa-1

# Configuración de rutas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '../data')
HISTORIAL_DIR = os.path.join(DATA_DIR, 'historial')
MESAS_JSON = os.path.join(DATA_DIR, 'mesas.json')
MENU_JSON = os.path.join(DATA_DIR, 'menu.json')

class SistemaMesas:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(HISTORIAL_DIR, exist_ok=True)
        self.cargar_datos()
        
    def cargar_datos(self):
        """Carga los datos iniciales"""
        try:
            with open(MESAS_JSON, 'r') as f:
                self.mesas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error cargando mesas.json")
            self.mesas = {}
            
        try:
            with open(MENU_JSON, 'r') as f:
                self.menu = json.load(f)
                # Normalizar nombres de categoría
                for plato in self.menu['platos']:
                    if 'categoria' in plato:  # Cambiar 'categoria' a 'categoría'
                        plato['categoría'] = plato.pop('categoria')
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error cargando menu.json")
            self.menu = {'platos': []}

    def guardar_mesas(self):
        """Guarda el estado actual de las mesas"""
        with open(MESAS_JSON, 'w') as f:
            json.dump(self.mesas, f, indent=2, ensure_ascii=False)
    
    def obtener_mesa_por_url(self, qr_url):
        """Busca mesa por URL QR"""
        for mesa_id, mesa_data in self.mesas.items():
            if mesa_data[0]['qr_url'] == qr_url:
                return mesa_id, mesa_data[0]
        return None, None
    
    def registrar_cliente(self, mesa_id, nombre_cliente):
        """Registra un cliente en la mesa"""
        mesa = self.mesas[mesa_id][0]
        
        # Verificar si ya existe
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre'].lower() == nombre_cliente.lower():
                return cliente_key
                
        # Buscar espacio vacío
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if not mesa[cliente_key]['nombre']:
                mesa[cliente_key]['nombre'] = nombre_cliente
                if mesa['estado'] == 'libre':
                    mesa['estado'] = 'ocupada'
                self.guardar_mesas()
                return cliente_key
        return None
    
    def menu_principal(self):
        """Muestra el menú principal con opciones de filtrado"""
        while True:
            print("\n--- MENÚ PRINCIPAL ---")
            print("1. Ver menú completo")
            print("2. Filtrar por categoría")
            print("3. Filtrar por dieta")
            print("4. Filtrar por etapa")
            print("0. Volver al menú cliente")
            
            opcion = input("Seleccione una opción: ")
            
            if opcion == "0":
                return None
            elif opcion == "1":
                self.mostrar_menu_completo()
            elif opcion == "2":
                platos = self.filtrar_por_categoria()
                if platos is not None:
                    return platos
            elif opcion == "3":
                platos = self.filtrar_por_dieta()
                if platos is not None:
                    return platos
            elif opcion == "4":
                platos = self.filtrar_por_etapa()
                if platos is not None:
                    return platos
    
    def mostrar_menu_completo(self):
        """Muestra todo el menú organizado por categorías"""
        categorias = sorted({plato.get('categoría', 'Sin categoría') for plato in self.menu['platos']})
        
        for categoria in categorias:
            print(f"\n=== {categoria.upper()} ===")
            platos_categoria = [p for p in self.menu['platos'] if p.get('categoría') == categoria]
            
            for i, plato in enumerate(platos_categoria, 1):
                print(f"\n{i}. {plato['nombre']} - ${plato['precio']}")
                print(f"   Descripción: {plato['descripcion']}")
                print(f"   Ingredientes: {', '.join(plato['ingredientes'])}")
                if 'dietas' in plato and plato['dietas']:
                    print(f"   Dietas: {', '.join(plato['dietas'])}")
        
        input("\nPresione Enter para continuar...")
    
    def filtrar_por_categoria(self):
        """Filtra platos por categoría"""
        categorias = sorted({plato.get('categoría', 'Sin categoría') for plato in self.menu['platos']})
        
        print("\n--- CATEGORÍAS DISPONIBLES ---")
        for i, cat in enumerate(categorias, 1):
            print(f"{i}. {cat}")
        print("0. Volver")
        
        try:
            opcion = int(input("Seleccione categoría: "))
            if opcion == 0:
                return None
            categoria = categorias[opcion-1]
            
            platos = [p for p in self.menu['platos'] if p.get('categoría') == categoria]
            self.mostrar_platos(platos)
            return platos
        except (ValueError, IndexError):
            print("Opción inválida")
            return None
    
    def filtrar_por_dieta(self):
        """Filtra platos por dieta especial"""
        dietas = ["Vegano", "Sin gluten", "Vegetariano", "Sin lactosa", "Nut-free"]
        
        print("\n--- DIETAS ESPECIALES ---")
        for i, dieta in enumerate(dietas, 1):
            print(f"{i}. {dieta}")
        print("0. Volver")
        
        try:
            opcion = int(input("Seleccione dieta: "))
            if opcion == 0:
                return None
            dieta_seleccionada = dietas[opcion-1].lower()
            
            platos = [p for p in self.menu['platos'] 
                     if dieta_seleccionada in [d.lower() for d in p.get('dietas', [])]]
            self.mostrar_platos(platos)
            return platos
        except (ValueError, IndexError):
            print("Opción inválida")
            return None
    
    def filtrar_por_etapa(self):
        """Filtra platos por etapa"""
        etapas = ["entrada", "principal", "postre", "bebida"]
        
        print("\n--- ETAPAS DEL MENÚ ---")
        for i, etapa in enumerate(etapas, 1):
            print(f"{i}. {etapa.capitalize()}")
        print("0. Volver")
        
        try:
            opcion = int(input("Seleccione etapa: "))
            if opcion == 0:
                return None
            etapa = etapas[opcion-1]
            
            platos = [p for p in self.menu['platos'] if p['etapa'] == etapa]
            self.mostrar_platos(platos)
            return platos
        except (ValueError, IndexError):
            print("Opción inválida")
            return None
    
    def mostrar_platos(self, platos):
        """Muestra la lista de platos con formato detallado"""
        if not platos:
            print("No se encontraron platos en esta categoría")
            return
            
        for i, plato in enumerate(platos, 1):
            print(f"\n{i}. {plato['nombre']} - ${plato['precio']}")
            print(f"   Descripción: {plato['descripcion']}")
            print(f"   Ingredientes: {', '.join(plato['ingredientes'])}")
            if 'dietas' in plato and plato['dietas']:
                print(f"   Dietas: {', '.join(plato['dietas'])}")
    
    def hacer_pedido(self, mesa_id, cliente_key):
        """Gestiona el proceso de pedido"""
        while True:
            platos = self.menu_principal()
            if platos is None:  # Opción "Volver"
                break
                
            try:
                opcion = int(input("Seleccione plato a agregar (0 para volver): "))
                if opcion == 0:
                    continue
                if opcion < 1 or opcion > len(platos):
                    print("Número de plato inválido")
                    continue
                    
                plato = platos[opcion-1]
                cantidad = int(input(f"Cantidad de '{plato['nombre']}': "))
                
                # Agregar pedido
                nuevo_pedido = {
                    'id': plato['id'],
                    'nombre': plato['nombre'],
                    'cantidad': cantidad,
                    'precio': plato['precio'],
                    'hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                self.mesas[mesa_id][0][cliente_key]['pedidos'].append(nuevo_pedido)
                self.guardar_mesas()
                print(f"\n✅ {cantidad} x {plato['nombre']} agregado(s) a tu pedido")
                
            except ValueError:
                print("Por favor ingrese un número válido")
    
    def llamar_camarero(self, mesa_id, cliente_key):
        """Registra solicitud de camarero"""
        mensaje = input("Ingrese su solicitud (ej: 'Necesito más pan'): ")
        
        comentario = {
            "mensaje": mensaje,
            "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "resuelto": False,
            "cliente": self.mesas[mesa_id][0][cliente_key]['nombre']
        }
        
        self.mesas[mesa_id][0]['comentarios_camarero'].append(comentario)
        self.guardar_mesas()
        print("\n✅ Solicitud enviada al camarero")
    
    def pagar_cuenta(self, mesa_id):
        """Procesa el pago y guarda historial"""
        # Crear registro de historial
        registro = {
            "mesa": self.mesas[mesa_id][0]['nombre'],
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "clientes": [],
            "total": 0
        }
        
        # Calcular total y preparar historial
        for i in range(1, self.mesas[mesa_id][0]['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            cliente = self.mesas[mesa_id][0][cliente_key]
            
            if cliente['nombre']:
                total_cliente = sum(p['precio'] * p['cantidad'] for p in cliente['pedidos'])
                registro["clientes"].append({
                    "nombre": cliente['nombre'],
                    "pedidos": cliente['pedidos'],
                    "total": total_cliente
                })
                registro["total"] += total_cliente
        
        # Guardar historial
        fecha_archivo = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_historial = os.path.join(HISTORIAL_DIR, f"mesa_{mesa_id}_{fecha_archivo}.json")
        
        with open(archivo_historial, 'w') as f:
            json.dump(registro, f, indent=2, ensure_ascii=False)
        
        # Reiniciar mesa
        mesa = self.mesas[mesa_id][0]
        mesa['estado'] = 'libre'
        
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            mesa[cliente_key]['nombre'] = ""
            mesa[cliente_key]['pedidos'] = []
        
        mesa['comentarios_camarero'] = []
        self.guardar_mesas()
        print(f"\n✅ Cuenta pagada - Total: ${registro['total']}")
        print(f"Historial guardado en {archivo_historial}")

def main():
    sistema = SistemaMesas()
    
    print("=== SISTEMA DE ACCESO POR QR ===")
    qr_url = input("Ingrese URL del QR escaneado: ")
    
    mesa_id, mesa = sistema.obtener_mesa_por_url(qr_url)
    if not mesa:
        print("Mesa no encontrada")
        return
        
    print(f"\nBienvenido a {mesa['nombre']} (Capacidad: {mesa['capacidad']})")
    
    # Registro de cliente
    nombre_cliente = input("Ingrese su nombre: ")
    cliente_key = sistema.registrar_cliente(mesa_id, nombre_cliente)
    
    if not cliente_key:
        print("Mesa llena o nombre ya registrado")
        return
    
    # Menú del cliente
    while True:
        print(f"\n--- MENÚ CLIENTE: {nombre_cliente} ---")
        print("1. Ver menú y hacer pedido")
        print("2. Llamar al camarero")
        print("3. Pagar cuenta")
        print("0. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "0":
            break
        elif opcion == "1":
            sistema.hacer_pedido(mesa_id, cliente_key)
        elif opcion == "2":
            sistema.llamar_camarero(mesa_id, cliente_key)
        elif opcion == "3":
            sistema.pagar_cuenta(mesa_id)
            break

if __name__ == "__main__":
    main()