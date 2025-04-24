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
        """Muestra el menú completo y permite seleccionar platos"""
        etapas = ["entrada", "principal", "postre", "bebida"]
        todos_platos = []  # Almacenará todos los platos con su referencia
        
        print("\n=== MENÚ COMPLETO ===")
        
        # Primero mostramos todo el menú con numeración continua
        contador_global = 1
        for etapa in etapas:
            if etapa not in self.menu['platos']:
                continue
                
            print(f"\n--- {etapa.upper()} ---")
            for categoria, platos in self.menu['platos'][etapa].items():
                print(f"\n  {categoria.capitalize()}:")
                for plato in platos:
                    # Guardamos referencia con índice global
                    todos_platos.append({
                        'etapa': etapa,
                        'categoria': categoria,
                        'plato': plato
                    })
                    
                    # Mostramos el plato
                    dietas = ", ".join(plato['dietas']) if 'dietas' in plato else ""
                    print(f"  {contador_global}. {plato['nombre']} - ${plato['precio']}")
                    print(f"     {plato['descripcion']}")
                    if dietas:
                        print(f"     🏷️ {dietas}")
                    
                    contador_global += 1
        
        # Ahora permitimos seleccionar
        while True:
            try:
                print("\n--- SELECCIÓN ---")
                print("Ingrese el número del plato que desea (0 para volver)")
                seleccion = int(input("> "))
                
                if seleccion == 0:
                    return None
                elif 1 <= seleccion <= len(todos_platos):
                    plato_seleccionado = todos_platos[seleccion-1]['plato']
                    print(f"\n✅ Seleccionaste: {plato_seleccionado['nombre']} - ${plato_seleccionado['precio']}")
                    return plato_seleccionado
                else:
                    print("⚠️ Número inválido. Intente nuevamente.")
            except ValueError:
                print("⚠️ Por favor ingrese un número.")
    
    def filtrar_por_categoria(self):
        """Filtra platos por categoría con selección directa"""
        # Obtener todas las categorías únicas
        categorias = sorted({
            categoria 
            for etapa in self.menu['platos'].values() 
            for categoria in etapa.keys()
        })
        
        while True:
            print("\n--- FILTRAR POR CATEGORÍA ---")
            print("Categorías disponibles:")
            for i, cat in enumerate(categorias, 1):
                print(f"{i}. {cat.capitalize()}")
            print("0. Volver al menú anterior")
            
            try:
                opcion = int(input("\nSeleccione categoría: "))
                if opcion == 0:
                    return None
                elif 1 <= opcion <= len(categorias):
                    categoria = categorias[opcion-1]
                    
                    # Buscar platos en todas las etapas
                    platos = [
                        plato
                        for etapa in self.menu['platos'].values()
                        for plato in etapa.get(categoria, [])
                    ]
                    
                    if not platos:
                        print("\n⚠️ No hay platos en esta categoría")
                        continue
                        
                    # Mostrar resultados
                    print(f"\n--- PLATOS EN {categoria.upper()} ---")
                    for i, plato in enumerate(platos, 1):
                        dietas = ", ".join(plato['dietas']) if 'dietas' in plato else ""
                        print(f"\n{i}. {plato['nombre']} - ${plato['precio']}")
                        print(f"   {plato['descripcion']}")
                        if dietas:
                            print(f"   🏷️ {dietas}")
                    
                    # Permitir selección directa
                    seleccion = int(input("\nSeleccione plato (0 para volver): "))
                    if seleccion == 0:
                        continue
                    elif 1 <= seleccion <= len(platos):
                        return platos[seleccion-1]
                    else:
                        print("⚠️ Número de plato inválido")
                else:
                    print("⚠️ Opción inválida")
            except ValueError:
                print("⚠️ Ingrese un número válido")

    def filtrar_por_dieta(self):
        """Filtra platos por dieta con selección directa"""
        dietas_disponibles = [
            "Vegano", "Sin gluten", "Vegetariano", 
            "Sin lactosa", "Nut-free"
        ]
        
        while True:
            print("\n--- FILTRAR POR DIETA ---")
            print("Dietas especiales disponibles:")
            for i, dieta in enumerate(dietas_disponibles, 1):
                print(f"{i}. {dieta}")
            print("0. Volver al menú anterior")
            
            try:
                opcion = int(input("\nSeleccione dieta: "))
                if opcion == 0:
                    return None
                elif 1 <= opcion <= len(dietas_disponibles):
                    dieta_seleccionada = dietas_disponibles[opcion-1].lower()
                    
                    # Buscar platos que cumplan con la dieta
                    platos = [
                        plato
                        for etapa in self.menu['platos'].values()
                        for categoria in etapa.values()
                        for plato in categoria
                        if 'dietas' in plato and 
                        any(d.lower() == dieta_seleccionada for d in plato['dietas'])
                    ]
                    
                    if not platos:
                        print(f"\n⚠️ No hay platos {dietas_disponibles[opcion-1].lower()}")
                        continue
                        
                    # Mostrar resultados
                    print(f"\n--- PLATOS {dietas_disponibles[opcion-1].upper()} ---")
                    for i, plato in enumerate(platos, 1):
                        print(f"\n{i}. {plato['nombre']} - ${plato['precio']}")
                        print(f"   {plato['descripcion']}")
                        print(f"   🏷️ {', '.join(plato['dietas'])}")
                    
                    # Permitir selección directa
                    seleccion = int(input("\nSeleccione plato (0 para volver): "))
                    if seleccion == 0:
                        continue
                    elif 1 <= seleccion <= len(platos):
                        return platos[seleccion-1]
                    else:
                        print("⚠️ Número de plato inválido")
                else:
                    print("⚠️ Opción inválida")
            except ValueError:
                print("⚠️ Ingrese un número válido")
    
    def mostrar_platos(self, platos):
        """Muestra una lista de platos"""
        if not platos:
            print("\nNo se encontraron platos con esos criterios.")
            return
        
        print("\n--- RESULTADOS ---")
        for i, plato in enumerate(platos, 1):
            print(f"\n{i}. {plato['nombre']} - ${plato['precio']}")
            print(f"   Descripción: {plato['descripcion']}")
            print(f"   Ingredientes: {', '.join(plato['ingredientes'])}")
            if 'dietas' in plato and plato['dietas']:
                print(f"   Dietas: {', '.join(plato['dietas'])}")
    
    def limpiar_mesa(self, mesa_id):
        """Reinicia el estado de una mesa después de pagar"""
        mesa = self.mesas[mesa_id][0]
        mesa['estado'] = 'libre'
        
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            mesa[cliente_key]['nombre'] = ""
            mesa[cliente_key]['pedidos'] = []
        
        mesa['comentarios_camarero'] = []
        self.guardar_mesas()   
