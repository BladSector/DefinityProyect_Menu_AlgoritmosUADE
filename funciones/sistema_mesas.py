import json
import os
from datetime import datetime

# Configuración de rutas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '../data')
HISTORIAL_DIR = os.path.join(DATA_DIR, 'historial_pagos')
MESAS_JSON = os.path.join(DATA_DIR, 'mesas.json')
MESAS_TEMP_JSON = MESAS_JSON + ".temp" # Archivo temporal
MENU_JSON = os.path.join(DATA_DIR, 'menu.json')

class SistemaMesas:
    def __init__(self):
        self.mesas = {}
        self.menu = {}
        self.cargar_mesas()
        self.cargar_menu()
        
    def cargar_mesas(self):
        """Carga las mesas desde el archivo JSON"""
        try:
            if os.path.exists(MESAS_JSON):
                with open(MESAS_JSON, 'r', encoding='utf-8') as f:
                    self.mesas = json.load(f)
            else:
                self.inicializar_mesas()
        except Exception as e:
            print(f"Error al cargar mesas: {str(e)}")
            self.inicializar_mesas()

    def cargar_menu(self):
        """Carga el menú desde el archivo JSON"""
        try:
            if os.path.exists(MENU_JSON):
                with open(MENU_JSON, 'r', encoding='utf-8') as f:
                    self.menu = json.load(f)
            else:
                self.inicializar_menu()
        except Exception as e:
            print(f"Error al cargar menú: {str(e)}")
            self.inicializar_menu()

    def inicializar_mesas(self):
        """Inicializa las mesas con valores predeterminados"""
        self.mesas = {
            'mesa_1': [{
                'nombre': 'Mesa 1',
                'capacidad': 4,
                'estado': 'libre',
                'url_qr': 'http://localhost:5000/mesa/1',
                'cliente_1': {'nombre': '', 'pedidos': [], 'notas': []},
                'cliente_2': {'nombre': '', 'pedidos': [], 'notas': []},
                'cliente_3': {'nombre': '', 'pedidos': [], 'notas': []},
                'cliente_4': {'nombre': '', 'pedidos': [], 'notas': []}
            }],
            'mesa_2': [{
                'nombre': 'Mesa 2',
                'capacidad': 2,
                'estado': 'libre',
                'url_qr': 'http://localhost:5000/mesa/2',
                'cliente_1': {'nombre': '', 'pedidos': [], 'notas': []},
                'cliente_2': {'nombre': '', 'pedidos': [], 'notas': []}
            }],
            'mesa_3': [{
                'nombre': 'Mesa 3',
                'capacidad': 6,
                'estado': 'libre',
                'url_qr': 'http://localhost:5000/mesa/3',
                'cliente_1': {'nombre': '', 'pedidos': [], 'notas': []},
                'cliente_2': {'nombre': '', 'pedidos': [], 'notas': []},
                'cliente_3': {'nombre': '', 'pedidos': [], 'notas': []},
                'cliente_4': {'nombre': '', 'pedidos': [], 'notas': []},
                'cliente_5': {'nombre': '', 'pedidos': [], 'notas': []},
                'cliente_6': {'nombre': '', 'pedidos': [], 'notas': []}
            }]
        }
        self.guardar_mesas()
        
    def guardar_mesas(self):
        """Guarda las mesas en el archivo JSON"""
        try:
            with open(MESAS_TEMP_JSON, 'w', encoding='utf-8') as f_temp:
                json.dump(self.mesas, f_temp, indent=2, ensure_ascii=False)
            os.replace(MESAS_TEMP_JSON, MESAS_JSON)
        except Exception as e:
            print(f"⚠️ Error al guardar mesas (escritura atómica): {e}")
            if os.path.exists(MESAS_TEMP_JSON):
                try:
                    os.remove(MESAS_TEMP_JSON)
                except OSError as e_remove:
                    print(f"⚠️ Error al eliminar archivo temporal fallido: {e_remove}")
            return False
        return True

    def inicializar_menu(self):
        """Inicializa el menú con valores predeterminados"""
        self.menu = {
            'platos': {
                'entrada': {
                    'entradas': [
                        {
                            'id': 'entrada_1',
                            'nombre': 'Ensalada César',
                            'descripcion': 'Lechuga romana, pollo a la parrilla, crutones, queso parmesano y aderezo césar',
                            'precio': 1200,
                            'dietas': ['vegetariano', 'sin gluten']
                        }
                    ]
                },
                'principal': {
                    'carnes': [
                        {
                            'id': 'carne_1',
                            'nombre': 'Bife de Chorizo',
                            'descripcion': '300g con papas fritas y ensalada',
                            'precio': 2500,
                            'dietas': []
                        }
                    ]
                },
                'postre': {
                    'postres': [
                        {
                            'id': 'postre_1',
                            'nombre': 'Tiramisú',
                            'descripcion': 'Clásico postre italiano con café y mascarpone',
                            'precio': 800,
                            'dietas': ['vegetariano']
                        }
                    ]
                }
            }
        }
        self.guardar_menu()

    def guardar_menu(self):
        """Guarda el menú en el archivo JSON"""
        try:
            with open(MENU_JSON, 'w', encoding='utf-8') as f:
                json.dump(self.menu, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error al guardar menú: {e}")
            return False
        return True

    def obtener_mesa_por_url(self, url):
        """Obtiene una mesa por su URL QR"""
        for mesa_id, mesa_data in self.mesas.items():
            if mesa_data[0]['url_qr'] == url:
                return mesa_id, mesa_data[0]
        return None, None
        
    def registrar_cliente(self, mesa_id, nombre):
        """Registra un cliente en una mesa"""
        if mesa_id not in self.mesas:
            return None
            
        mesa = self.mesas[mesa_id][0]
        
        # Verificar si el nombre ya está registrado
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f'cliente_{i}'
            if mesa[cliente_key]['nombre'] == nombre:
                return None
                
        # Buscar un espacio libre
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f'cliente_{i}'
            if not mesa[cliente_key]['nombre']:
                mesa[cliente_key]['nombre'] = nombre
                mesa['estado'] = 'ocupada'
                self.guardar_mesas()
                return cliente_key
                
        return None
        
    def reiniciar_mesa(self, mesa_id):
        """Reinicia una mesa a su estado inicial"""
        if mesa_id not in self.mesas:
            return False
            
        mesa = self.mesas[mesa_id][0]
        mesa['estado'] = 'libre'
        
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f'cliente_{i}'
            mesa[cliente_key] = {
                'nombre': '',
                'pedidos': [],
                'notas': []
            }
            
        self.guardar_mesas()
        return True

    def obtener_mesa(self, mesa_id):
        """Obtiene la información de una mesa por su ID."""
        try:
            # Convertir el ID a string para asegurar consistencia
            mesa_id = str(mesa_id)
            mesa_data = self.mesas.get(mesa_id)
            if not mesa_data:
                print(f"⚠️ Error: Mesa {mesa_id} no encontrada")
                return None
            return mesa_data
        except Exception as e:
            print(f"⚠️ Error al obtener mesa {mesa_id}: {str(e)}")
            return None

    def limpiar_mesa(self, mesa_id):
        """Reinicia el estado de una mesa después de pagar."""
        mesa = self.obtener_mesa(mesa_id)
        if mesa:
            mesa['estado'] = 'libre'
            for i in range(1, mesa['capacidad'] + 1):
                cliente_key = f"cliente_{i}"
                mesa[cliente_key]['nombre'] = ""
                mesa[cliente_key]['pedidos'] = []
            mesa['comentarios_camarero'] = []
            mesa['notificaciones'] = []
            self.guardar_mesas()

    def mostrar_menu_completo(self):
        """Muestra el menú completo y devuelve la lista de todos los platos."""
        etapas = sorted(self.menu['platos'].keys())
        todos_platos = []
        contador_global = 1

        print("\n=== MENÚ COMPLETO ===")

        for etapa in etapas:
            print(f"\n--- {etapa.upper()} ---")
            for categoria, platos in sorted(self.menu['platos'][etapa].items()):
                print(f"\n  {categoria.capitalize()}:")
                for plato in platos:
                    todos_platos.append({'etapa': etapa, 'categoria': categoria, 'plato': plato, 'index': contador_global})
                    dietas = ", ".join(plato.get('dietas', []))
                    print(f"  {contador_global}. {plato['nombre']} - ${plato['precio']}")
                    print(f"      {plato.get('descripcion', '')}")
                    if dietas:
                        print(f"      🏷️ {dietas}")
                    contador_global += 1
        return todos_platos

    def _normalizar_categoria(self, categoria):
        """Normaliza el nombre de la categoría para comparación."""
        return categoria.lower().replace('/', ' ').strip()

    def filtrar_por_categoria(self):
        """Filtra platos por categoría."""
        categorias = set()
        for etapa in self.menu['platos'].values():
            for cat in etapa.keys():
                cat_normalizada = self._normalizar_categoria(cat)
                print(f"Normalizando categoría del menú: '{cat}' -> '{cat_normalizada}'")
                categorias.add(cat_normalizada)
        return sorted(list(categorias))

    def obtener_platos_por_categoria(self, categoria):
        """Obtiene todos los platos de una categoría específica."""
        platos_categoria = []
        categoria_normalizada = self._normalizar_categoria(categoria)
        print(f"Buscando platos para categoría normalizada: '{categoria_normalizada}'")
        
        for etapa in self.menu['platos'].values():
            for cat_nombre, platos in etapa.items():
                cat_nombre_normalizado = self._normalizar_categoria(cat_nombre)
                print(f"Comparando con categoría del menú: '{cat_nombre}' -> '{cat_nombre_normalizado}'")
                if cat_nombre_normalizado == categoria_normalizada:
                    platos_categoria.extend(platos)
        
        return platos_categoria

    def obtener_dietas_disponibles(self):
        """Obtiene la lista de dietas disponibles en el menú."""
        dietas = set()
        for etapa in self.menu['platos'].values():
            for categoria in etapa.values():
                for plato in categoria:
                    if 'dietas' in plato:
                        dietas.update(plato['dietas'])
        return sorted(list(dietas))

    def obtener_platos_por_dieta(self, dieta):
        """Obtiene todos los platos que cumplen con una dieta específica."""
        platos_dieta = []
        for etapa in self.menu['platos'].values():
            for categoria in etapa.values():
                for plato in categoria:
                    if 'dietas' in plato and dieta.lower() in [d.lower() for d in plato['dietas']]:
                        platos_dieta.append(plato)
        return platos_dieta

    def obtener_etapas_menu(self):
        """Obtiene la lista de etapas del menú."""
        return sorted(self.menu['platos'].keys())

    def obtener_platos_por_etapa(self, etapa):
        """Obtiene los platos de una etapa específica."""
        return self.menu['platos'].get(etapa, {})

    def obtener_mesas(self):
        """Obtiene todas las mesas disponibles."""
        return {mesa_id: mesa_data[0] for mesa_id, mesa_data in self.mesas.items()}

    def ocupar_mesa(self, mesa_id, clientes):
        """Ocupa una mesa con los clientes especificados."""
        if mesa_id not in self.mesas:
            print(f"⚠️ Error: Mesa {mesa_id} no encontrada")
            return False

        mesa = self.mesas[mesa_id][0]
        
        # Verificar si la mesa está libre
        if mesa['estado'] != 'libre':
            print(f"⚠️ Error: Mesa {mesa_id} ya está ocupada")
            return False

        # Verificar si hay suficiente capacidad
        if len(clientes) > mesa['capacidad']:
            print(f"⚠️ Error: La mesa {mesa_id} no tiene suficiente capacidad para {len(clientes)} clientes")
            return False

        # Registrar cada cliente
        for i, nombre_cliente in enumerate(clientes, 1):
            cliente_key = f"cliente_{i}"
            mesa[cliente_key] = {
                'nombre': nombre_cliente,
                'pedidos': []
            }

        # Marcar la mesa como ocupada
        mesa['estado'] = 'ocupada'
        mesa['comentarios_camarero'] = []
        mesa['notificaciones'] = []

        # Guardar los cambios
        return self.guardar_mesas()

    def agregar_cliente_mesa(self, mesa_id, nombre_cliente):
        """Agrega un nuevo cliente a una mesa existente si hay espacio disponible."""
        if mesa_id not in self.mesas:
            print(f"⚠️ Error: Mesa {mesa_id} no encontrada")
            return False

        mesa = self.mesas[mesa_id][0]
        
        # Verificar si la mesa está ocupada
        if mesa['estado'] != 'ocupada':
            print(f"⚠️ Error: Mesa {mesa_id} no está ocupada")
            return False

        # Verificar si el cliente ya existe en la mesa
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key].get('nombre') == nombre_cliente:
                print(f"⚠️ Error: El cliente {nombre_cliente} ya está en la mesa")
                return False

        # Buscar un espacio libre
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if not mesa[cliente_key].get('nombre'):
                mesa[cliente_key] = {
                    'nombre': nombre_cliente,
                    'pedidos': []
                }
                return self.guardar_mesas()

        print(f"⚠️ Error: No hay espacio disponible en la mesa {mesa_id}")
        return False