import json
import os

# Configuración de rutas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '../data')
HISTORIAL_DIR = os.path.join(DATA_DIR, 'historial_pagos')
MESAS_JSON = os.path.join(DATA_DIR, 'mesas.json')
MESAS_TEMP_JSON = MESAS_JSON + ".temp" # Archivo temporal
MENU_JSON = os.path.join(DATA_DIR, 'menu.json')

class SistemaMesas:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(HISTORIAL_DIR, exist_ok=True)
        self.cargar_datos()

    def cargar_datos(self):
        """Carga los datos iniciales de mesas y menú."""
        try:
            with open(MESAS_JSON, 'r', encoding='utf-8') as f:
                self.mesas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error cargando mesas.json")
            self.mesas = {}

        try:
            with open(MENU_JSON, 'r', encoding='utf-8') as f:
                self.menu = json.load(f)
                self._normalizar_menu()
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error cargando menu.json")
            self.menu = {'platos': {}}

    def _normalizar_menu(self):
        """Normaliza los nombres de las categorías del menú."""
        if 'platos' in self.menu:
            for etapa, categorias in self.menu['platos'].items():
                nuevas_categorias = {}
                for categoria, platos in categorias.items():
                    nuevas_platos = []
                    for plato in platos:
                        if 'categoria' in plato:
                            plato['categoría'] = plato.pop('categoria')
                        nuevas_platos.append(plato)
                    nuevas_categorias[categoria] = nuevas_platos
                self.menu['platos'][etapa] = nuevas_categorias

    def guardar_mesas(self):
        """Guarda el estado actual de las mesas de forma atómica."""
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

    def obtener_mesa(self, mesa_id):
        """Obtiene la información de una mesa por su ID."""
        mesa_data = self.mesas.get(mesa_id)
        return mesa_data[0] if mesa_data else None

    def obtener_mesa_por_url(self, qr_url):
        """Busca una mesa por su URL QR."""
        for mesa_id, mesa_data in self.mesas.items():
            if mesa_data[0]['qr_url'] == qr_url:
                return mesa_id, mesa_data[0]
        return None, None

    def registrar_cliente(self, mesa_id, nombre_cliente):
        """Registra un cliente en una mesa específica."""
        if mesa_id not in self.mesas:
            print(f"⚠️ Error: Mesa {mesa_id} no encontrada")
            return None

        mesa = self.mesas[mesa_id][0]
        
        # Primero buscar si el cliente ya existe en la mesa
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre'] == nombre_cliente:
                mesa['estado'] = 'ocupada'
                self.guardar_mesas()
                return cliente_key

        # Si no existe, buscar un espacio libre
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if not mesa[cliente_key]['nombre']:
                mesa[cliente_key]['nombre'] = nombre_cliente
                mesa['estado'] = 'ocupada'
                self.guardar_mesas()
                return cliente_key
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

    def filtrar_por_categoria(self):
        """Filtra platos por categoría."""
        categorias = sorted(set(cat for etapa in self.menu['platos'].values() for cat in etapa.keys()))
        return categorias

    def obtener_platos_por_categoria(self, categoria):
        """Obtiene todos los platos de una categoría específica."""
        platos_categoria = []
        for etapa in self.menu['platos'].values():
            if categoria in etapa:
                platos_categoria.extend(etapa[categoria])
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