from datetime import datetime

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

class VisualizadorPedidosMozo:
    """Clase para manejar toda la visualización de pedidos para el mozo"""

    def __init__(self, sistema_mesas):
        self.sistema_mesas = sistema_mesas
        self.estados_pedido = {
            'preparar': '🟢 PREPARAR AHORA',
            'normal': '🟡 NORMAL',
            'cancelado': '🔴 CANCELADO',
            'agregado': '🔵 AGREGADO',
            'en_preparacion': '👨‍🍳 EN PREPARACIÓN',
            'listo': '✅ LISTO PARA ENTREGAR',
            'entregado': '🍽️ ENTREGADO'
        }
        self.estados_comentario = {
            'pendiente': '💬 Pendiente',
            'realizado': '✅ Realizado'
        }

    def mostrar_mapa_mesas(self):
        """Muestra un mapa completo de todas las mesas con su estado, clientes, pedidos y comentarios"""
        print("\n--- MAPA DEL RESTAURANTE ---")

        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            estado_mesa = "🟢 Libre" if mesa['estado'] == 'libre' else "🟠 Ocupada"

            print(f"\n{mesa['nombre']} [{estado_mesa}]")

            if mesa['estado'] == 'ocupada':
                for i in range(1, mesa['capacidad'] + 1):
                    cliente_key = f"cliente_{i}"
                    if mesa[cliente_key]['nombre']:
                        print(f"\n 👤 {mesa[cliente_key]['nombre']}:")
                        for pedido in mesa[cliente_key]['pedidos']:
                            self._mostrar_detalle_pedido_mapa(pedido)
                        self._mostrar_comentarios_cliente_mapa(mesa, cliente_key)

    def _mostrar_detalle_pedido_mapa(self, pedido):
        """Muestra los detalles del pedido para el mapa, incluyendo estado y notas"""
        nota_texto = ""
        if 'notas' in pedido and pedido['notas']:
            nota_texto = f" (Nota: {pedido['notas'][-1]['texto']})"
        elif 'nota' in pedido:
            nota_texto = f" (Nota: {pedido['nota']})"
        estado_pedido = self.estados_pedido.get(pedido.get('estado_cocina'), '⏳ Pendiente')
        entregado = " (✅ Entregado)" if pedido.get('entregado') else ""
        es_bebida = " (🥤 Bebida)" if pedido.get('es_bebida') else ""
        print(f"  - {pedido['cantidad']}x {pedido['nombre']} [{estado_pedido}{entregado}{es_bebida}]{nota_texto}")

    def _mostrar_comentarios_cliente_mapa(self, mesa, cliente_key):
        """Muestra los comentarios pendientes de un cliente en el mapa"""
        if 'comentarios' in mesa and mesa['comentarios']:
            comentarios_cliente = [
                comentario for comentario in mesa['comentarios']
                if comentario['cliente'] == mesa[cliente_key]['nombre'] and comentario['estado'] == 'pendiente'
            ]
            if comentarios_cliente:
                print("  📝 Comentarios:")
                for comentario in comentarios_cliente:
                    estado_comentario = self.estados_comentario.get(comentario['estado'], '❓ Desconocido')
                    print(f"   - {comentario['texto']} [{estado_comentario}]")

    def _validar_mesa(self, mesa_id):
        """Valida que la mesa exista y tenga estructura correcta"""
        if mesa_id not in self.sistema_mesas.mesas:
            return False
        if len(self.sistema_mesas.mesas[mesa_id]) == 0:
            return False
        return True

class SistemaPedidosMozos:
    """Sistema de gestión de pedidos para los mozos de un restaurante."""

    def __init__(self, sistema_mesas):
        """Inicializa el sistema con dependencias necesarias."""
        self.sistema_mesas = sistema_mesas
        self.notificaciones = ManejadorNotificaciones(sistema_mesas)
        self.visualizador = VisualizadorPedidosMozo(sistema_mesas)
        self.estados_comentario = {
            'pendiente': '💬 Pendiente',
            'realizado': '✅ Realizado'
        }

    def mostrar_mapa_mesas(self):
        """Muestra el mapa de mesas con clientes, pedidos y comentarios."""
        self.visualizador.mostrar_mapa_mesas()

    def gestionar_comentarios(self):
        """Permite al mozo ver y marcar comentarios como realizados."""
        while True:
            comentarios_pendientes = self._obtener_comentarios_pendientes()
            if not comentarios_pendientes:
                print("\nNo hay comentarios pendientes.")
                input("Presione Enter para volver al menú...")
                return

            print("\n--- COMENTARIOS PENDIENTES ---")
            for i, comentario_info in enumerate(comentarios_pendientes, 1):
                print(f"{i}. Mesa: {comentario_info['mesa_nombre']}, Cliente: {comentario_info['cliente']}, Comentario: {comentario_info['texto']}")
            print("\n0. Volver al menú principal")

            opcion = input("Seleccione un comentario para marcar como realizado (número) o 0 para volver: ")
            if opcion == '0':
                return
            try:
                indice = int(opcion) - 1
                if 0 <= indice < len(comentarios_pendientes):
                    comentario = comentarios_pendientes[indice]
                    if self._marcar_comentario_realizado(comentario['mesa_id'], comentario['cliente'], comentario['texto']):
                        print("Comentario marcado como realizado.")
                    else:
                        print("Error al marcar el comentario como realizado.")
                else:
                    print("Número de comentario inválido.")
            except ValueError:
                print("Por favor, ingrese un número válido.")

    def _obtener_comentarios_pendientes(self):
        """Obtiene todos los comentarios pendientes de todas las mesas."""
        comentarios_pendientes = []
        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            if 'comentarios' in mesa:
                for comentario in mesa['comentarios']:
                    if comentario['estado'] == 'pendiente':
                        comentarios_pendientes.append({
                            'mesa_id': mesa_id,
                            'mesa_nombre': mesa['nombre'],
                            'cliente': comentario['cliente'],
                            'texto': comentario['texto']
                        })
        return comentarios_pendientes

    def _marcar_comentario_realizado(self, mesa_id, cliente_nombre, comentario_texto):
        """Marca un comentario específico como realizado."""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return False

        mesa = mesa_data[0]
        if 'comentarios' in mesa:
            for comentario in mesa['comentarios']:
                if comentario['cliente'] == cliente_nombre and comentario['texto'] == comentario_texto and comentario['estado'] == 'pendiente':
                    comentario['estado'] = 'realizado'
                    try:
                        self.sistema_mesas.guardar_mesas()
                        return True
                    except Exception as e:
                        print(f"⚠️ Error al guardar mesas (marcar_comentario_realizado): {e}")
                        return False
        return False

    def gestionar_entregas(self):
        """Permite al mozo marcar pedidos como entregados."""
        while True:
            pedidos_listos = self._obtener_pedidos_listos_para_entregar()
            if not pedidos_listos:
                print("\nNo hay pedidos listos para entregar.")
                input("Presione Enter para volver al menú...")
                return

            print("\n--- PEDIDOS LISTOS PARA ENTREGAR ---")
            for i, pedido_info in enumerate(pedidos_listos, 1):
                print(f"{i}. Mesa: {pedido_info['mesa_nombre']}, Cliente: {pedido_info['cliente']}, Pedido: {pedido_info['nombre']}")
            print("\n0. Volver al menú principal")

            opcion = input("Seleccione un pedido para marcar como entregado (número) o 0 para volver: ")
            if opcion == '0':
                return
            try:
                indice = int(opcion) - 1
                if 0 <= indice < len(pedidos_listos):
                    pedido = pedidos_listos[indice]
                    if self._marcar_pedido_entregado(pedido['mesa_id'], pedido['cliente'], pedido['id']):
                        print(f"Pedido '{pedido['nombre']}' marcado como entregado.")
                    else:
                        print("Error al marcar el pedido como entregado.")
                else:
                    print("Número de pedido inválido.")
            except ValueError:
                print("Por favor, ingrese un número válido.")

    def _obtener_pedidos_listos_para_entregar(self):
        """Obtiene todos los pedidos marcados como 'listo' y no entregados."""
        pedidos_listos = []
        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            if mesa['estado'] == 'ocupada':
                for i in range(1, mesa['capacidad'] + 1):
                    cliente_key = f"cliente_{i}"
                    if mesa[cliente_key]['nombre']:
                        for pedido in mesa[cliente_key]['pedidos']:
                            if pedido.get('estado_cocina') == '✅ LISTO PARA ENTREGAR' and not pedido.get('entregado'):
                                pedidos_listos.append({
                                    'mesa_id': mesa_id,
                                    'mesa_nombre': mesa['nombre'],
                                    'cliente': mesa[cliente_key]['nombre'],
                                    'nombre': pedido['nombre'],
                                    'id': pedido['id']
                                })
        return pedidos_listos

    def _marcar_pedido_entregado(self, mesa_id, cliente_nombre, pedido_id):
        """Marca un pedido específico como entregado."""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return False

        mesa = mesa_data[0]
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre'] == cliente_nombre:
                for pedido in mesa[cliente_key]['pedidos']:
                    if pedido['id'] == pedido_id:
                        pedido['entregado'] = True
                        try:
                            self.sistema_mesas.guardar_mesas()
                            return True
                        except Exception as e:
                            print(f"⚠️ Error al guardar mesas (marcar_pedido_entregado): {e}")
                            return False
        return False

    def _validar_mesa(self, mesa_id):
        """Valida que la mesa exista y devuelve la lista asociada"""
        if mesa_id not in self.sistema_mesas.mesas:
            print(f"⚠️ Error: Mesa {mesa_id} no encontrada")
            return None
        return self.sistema_mesas.mesas[mesa_id]

    def _validar_mesa_estructura(self, mesa_data):
        """Valida que la estructura de los datos de la mesa sea correcta"""
        if not isinstance(mesa_data, list) or len(mesa_data) == 0 or not isinstance(mesa_data[0], dict):
            print(f"⚠️ Error: Estructura de datos incorrecta para la mesa")
            return False
        return True

    def procesar_pedidos_mesa(self, mesa_id):
        """Procesa los pedidos de una mesa específica (incluyendo bebidas)."""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return []

        mesa = mesa_data[0]
        pedidos_procesados = []

        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre']:
                for pedido in mesa[cliente_key]['pedidos']:
                    nota_texto = ""
                    if pedido.get('notas'):
                        nota_texto = pedido['notas'][-1]['texto']
                    elif pedido.get('nota'):
                        nota_texto = pedido['nota']

                    pedido_procesado = {
                        'id': pedido['id'],
                        'nombre': pedido['nombre'],
                        'cantidad': pedido['cantidad'],
                        'cliente': mesa[cliente_key]['nombre'],
                        'mesa_id': mesa_id,
                        'mesa_nombre': mesa['nombre'],
                        'hora': pedido.get('hora', 'No registrada'),
                        'notas': pedido.get('notas') if 'notas' in pedido else ([{'texto': pedido['nota'], 'hora': 'antigua'}] if 'nota' in pedido else []),
                        'estado_cocina': pedido.get('estado_cocina'),
                        'retraso_minutos': pedido.get('retraso_minutos'),
                        'entregado': pedido.get('entregado', False),
                        'es_bebida': 'bebida' in pedido['nombre'].lower()
                    }
                    pedidos_procesados.append(pedido_procesado)
        return pedidos_procesados

    def mostrar_menu(self):
        """Muestra el menú principal del sistema de mozos."""
        while True:
            print("\n--- SISTEMA DE MOZOS ---")
            print("1. Mostrar mapa de mesas")
            print("2. Gestionar comentarios pendientes")
            print("3. Gestionar entregas de pedidos")
            print("0. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                self.mostrar_mapa_mesas()
                input("Presione Enter para volver al menú...")
            elif opcion == '2':
                self.gestionar_comentarios()
            elif opcion == '3':
                self.gestionar_entregas()
            elif opcion == '0':
                print("Saliendo del sistema de mozos.")
                break
            else:
                print("Opción inválida. Por favor, intente nuevamente.")

# Ejemplo de uso (necesitarías una instancia de SistemaMesas para que funcione)
if __name__ == "__main__":
    class SistemaMesasSimulado:
        def __init__(self):
            self.mesas = {
                "Mesa 1": [
                    {
                        'nombre': 'Mesa 1',
                        'estado': 'ocupada',
                        'capacidad': 2,
                        'cliente_1': {'nombre': 'Ana', 'pedidos': [{'id': '1', 'nombre': 'Milanesa', 'cantidad': 1, 'notas': [{'texto': 'Sin sal', 'hora': '12:00'}], 'estado_cocina': '✅ LISTO PARA ENTREGAR', 'entregado': False, 'es_bebida': False}, {'id': '2', 'nombre': 'Agua', 'cantidad': 1, 'es_bebida': True, 'entregado': False}]},
                        'cliente_2': {'nombre': 'Juan', 'pedidos': [{'id': '3', 'nombre': 'Pizza', 'cantidad': 1, 'nota': 'Con extra queso', 'estado_cocina': '👨‍🍳 EN PREPARACIÓN', 'es_bebida': False}]},
                        'comentarios': [{'cliente': 'Ana', 'texto': 'Necesita más pan', 'estado': 'pendiente'}, {'cliente': 'Juan', 'texto': 'La pizza fría', 'estado': 'pendiente'}]
                    }
                ],
                "Mesa 2": [
                    {
                        'nombre': 'Mesa 2',
                        'estado': 'libre',
                        'capacidad': 4,
                        'cliente_1': {'nombre': '', 'pedidos': []},
                        'cliente_2': {'nombre': '', 'pedidos': []},
                        'cliente_3': {'nombre': '', 'pedidos': []},
                        'cliente_4': {'nombre': '', 'pedidos': []},
                        'comentarios': []
                    }
                ]
            }

        def guardar_mesas(self):
            print("Simulando guardado de mesas...")

    sistema_mesas_simulado = SistemaMesasSimulado()
    sistema_mozos = SistemaPedidosMozos(sistema_mesas_simulado)
    sistema_mozos.mostrar_menu()