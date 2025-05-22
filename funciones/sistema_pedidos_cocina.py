from datetime import datetime
from .base_visualizacion import BaseVisualizador

class ManejadorNotificaciones:
    """Clase para gestionar todas las notificaciones del sistema"""

    def __init__(self, sistema_mesas):
        self.sistema_mesas = sistema_mesas

    def registrar_notificacion(self, mesa_id, mensaje, tipo="general"):
        """Registra una notificación en el sistema de mesas"""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return False

        mesa = mesa_data[0]

        if 'notificaciones' not in mesa:
            mesa['notificaciones'] = []

        mesa['notificaciones'].append({
            "mensaje": mensaje,
            "hora": datetime.now().strftime("%H:%M hs"),
            "tipo": tipo
        })
        return True

    def _validar_mesa(self, mesa_id):
        """Valida que la mesa exista y devuelve la lista asociada"""
        if mesa_id not in self.sistema_mesas.mesas:
            print(f"⚠️ Error: Mesa {mesa_id} no encontrada")
            return None
        return self.sistema_mesas.mesas[mesa_id]

class SistemaPedidosCocina(BaseVisualizador):
    """Sistema de gestión de pedidos para la cocina de un restaurante."""

    def __init__(self, sistema_mesas):
        """Inicializa el sistema con dependencias necesarias."""
        super().__init__(sistema_mesas)
        self.notificaciones = ManejadorNotificaciones(sistema_mesas)
        self.estados_pedido = {
            'pendiente': '🟡 Pendiente en cocina',
            'en_preparacion': '👨‍🍳 EN PREPARACIÓN',
            'listo': '✅ LISTO PARA ENTREGAR',
            'cancelado': '🔴 CANCELADO'
        }

    def mostrar_pedidos_activos(self):
        """Muestra los pedidos activos en cocina."""
        pedidos_activos = []
        
        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            if mesa['estado'] == 'ocupada':
                pedidos = self.procesar_pedidos_mesa(mesa_id)
                pedidos_cocina = [p for p in pedidos if p.get('en_cocina', False) and not p.get('entregado', False) and not p.get('es_bebida')]
                pedidos_activos.extend(pedidos_cocina)
        
        return pedidos_activos

    def procesar_pedidos_mesa(self, mesa_id):
        """Procesa los pedidos de una mesa específica."""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return []

        mesa = mesa_data[0]
        pedidos_procesados = []

        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    pedido_info = self._crear_info_pedido(pedido, mesa_id, cliente_key, cliente)
                    pedidos_procesados.append(pedido_info)

        return pedidos_procesados

    def _crear_info_pedido(self, pedido, mesa_id, cliente_key, cliente):
        """Crea un diccionario con la información del pedido."""
        return {
            'id': pedido.get('id'),
            'mesa_id': mesa_id,
            'cliente_key': cliente_key,
            'cliente': cliente['nombre'],
            'nombre': pedido.get('nombre', 'Desconocido'),
            'cantidad': pedido.get('cantidad', 1),
            'precio': pedido.get('precio', 0),
            'estado_cocina': pedido.get('estado_cocina', self.estados_pedido['pendiente']),
            'hora_envio': pedido.get('hora_envio', ''),
            'notas': pedido.get('notas', []),
            'en_cocina': pedido.get('en_cocina', False),
            'entregado': pedido.get('entregado', False),
            'retraso_minutos': pedido.get('retraso_minutos', 0),
            'es_bebida': 'bebida' in pedido.get('nombre', '').lower()
        }

    def actualizar_estado_pedido(self, mesa_id, pedido_id, nuevo_estado):
        """Actualiza el estado de un pedido específico."""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return False

        mesa = mesa_data[0]
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    if pedido.get('id') == pedido_id:
                        # Registrar el historial de estados
                        if 'historial_estados' not in pedido:
                            pedido['historial_estados'] = []
                        
                        pedido['historial_estados'].append({
                            'estado': self.estados_pedido[nuevo_estado],
                            'hora': datetime.now().strftime("%H:%M hs")
                        })
                        
                        pedido['estado_cocina'] = self.estados_pedido[nuevo_estado]
                        try:
                            self.sistema_mesas.guardar_mesas()
                            return True
                        except Exception as e:
                            print(f"⚠️ Error al guardar mesas: {e}")
                            return False
        return False

    def obtener_pedidos_mesa(self, mesa_id):
        """Obtiene los pedidos de una mesa específica."""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return []

        mesa = mesa_data[0]
        pedidos = []

        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    if pedido.get('en_cocina', False) and not pedido.get('entregado', False):
                        pedido_info = {
                            'id': pedido.get('id'),
                            'nombre': pedido.get('nombre', 'Desconocido'),
                            'cantidad': pedido.get('cantidad', 1),
                            'cliente': cliente['nombre'],
                            'mesa_id': mesa_id,
                            'mesa_nombre': mesa['nombre'],
                            'hora': pedido.get('hora', 'No registrada'),
                            'notas': pedido.get('notas', []),
                            'estado_cocina': pedido.get('estado_cocina'),
                            'entregado': pedido.get('entregado', False),
                            'es_bebida': 'bebida' in pedido.get('nombre', '').lower()
                        }
                        pedidos.append(pedido_info)
        return pedidos