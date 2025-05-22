from datetime import datetime

class BaseVisualizador:
    """Clase base para la visualización común de mesas y pedidos"""

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

    def mostrar_mapa_mesas(self):
        """Muestra un mapa completo de todas las mesas con su estado"""
        while True:
            print("\n=== MAPA DEL RESTAURANTE ===")
            print("\nMesas disponibles:")
            
            mesas_ocupadas = []
            for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
                mesa = mesa_data[0]
                estado = "🟢 Libre" if mesa['estado'] == 'libre' else "🟠 Ocupada"
                print(f"{len(mesas_ocupadas) + 1}. {mesa['nombre']} [{estado}]")
                if mesa['estado'] == 'ocupada':
                    mesas_ocupadas.append((mesa_id, mesa))

            print("\n0. Volver al menú principal")

            try:
                opcion = int(input("\nSeleccione una mesa para ver detalles (número): "))
                if opcion == 0:
                    return
                
                if 1 <= opcion <= len(mesas_ocupadas):
                    mesa_id, mesa = mesas_ocupadas[opcion - 1]
                    self._mostrar_detalles_mesa(mesa_id, mesa)
                else:
                    print("ℹ️   Mesa libre. Seleccione una mesa ocupada.")
            except ValueError:
                print("Por favor ingrese un número válido")

    def _mostrar_detalles_mesa(self, mesa_id, mesa):
        """Muestra los detalles de una mesa específica"""
        print(f"\n=== {mesa['nombre']} ===")
        
        # Pedidos pendientes de enviar
        print("\n--- PEDIDOS POR ENVIAR A COCINA ---")
        hay_pendientes = False
        clientes_pendientes = {}
        
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                pedidos_pendientes = []
                for pedido in cliente.get('pedidos', []):
                    if not pedido.get('en_cocina', False):
                        pedidos_pendientes.append(pedido)
                if pedidos_pendientes:
                    clientes_pendientes[cliente['nombre']] = pedidos_pendientes
                    hay_pendientes = True

        if hay_pendientes:
            for nombre_cliente, pedidos in clientes_pendientes.items():
                print(f"\n👤 {nombre_cliente}:")
                for pedido in pedidos:
                    print(f"  - {pedido.get('cantidad', 1)}x {pedido.get('nombre', 'Desconocido')} 🟡 Pendiente")
                    if 'notas' in pedido and pedido['notas']:
                        print("    📝 Notas:")
                        for nota in pedido['notas']:
                            print(f"      • {nota['texto']}")
        else:
            print("(No hay pedidos pendientes de enviar)")

        # Pedidos en cocina
        print("\n--- PEDIDOS EN COCINA ---")
        hay_en_cocina = False
        clientes_en_cocina = {}
        
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                pedidos_cocina = []
                for pedido in cliente.get('pedidos', []):
                    if pedido.get('en_cocina', False) and not pedido.get('entregado', False):
                        pedidos_cocina.append(pedido)
                if pedidos_cocina:
                    clientes_en_cocina[cliente['nombre']] = pedidos_cocina
                    hay_en_cocina = True

        if hay_en_cocina:
            for nombre_cliente, pedidos in clientes_en_cocina.items():
                print(f"\n👤 {nombre_cliente}:")
                for pedido in pedidos:
                    estado = pedido.get('estado_cocina', "🟢 En cocina")
                    hora_envio = f" [Enviado: {pedido.get('hora_envio', 'No registrada')}]"
                    print(f"  - {pedido.get('cantidad', 1)}x {pedido.get('nombre', 'Desconocido')} {estado}{hora_envio}")
                    if 'notas' in pedido and pedido['notas']:
                        print("    📝 Notas:")
                        for nota in pedido['notas']:
                            print(f"      • {nota['texto']}")
        else:
            print("  (No hay pedidos en cocina)")

        # Pedidos entregados
        print("\n--- PEDIDOS ENTREGADOS ---")
        hay_entregados = False
        clientes_entregados = {}
        
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                pedidos_entregados = []
                for pedido in cliente.get('pedidos', []):
                    if pedido.get('entregado', False):
                        pedidos_entregados.append(pedido)
                if pedidos_entregados:
                    clientes_entregados[cliente['nombre']] = pedidos_entregados
                    hay_entregados = True

        if hay_entregados:
            for nombre_cliente, pedidos in clientes_entregados.items():
                print(f"\n👤 {nombre_cliente}:")
                for pedido in pedidos:
                    hora_envio = f" [Enviado: {pedido.get('hora_envio', 'No registrada')}]"
                    print(f"  - {pedido.get('cantidad', 1)}x {pedido.get('nombre', 'Desconocido')} ✅ Entregado{hora_envio}")
                    if 'notas' in pedido and pedido['notas']:
                        print("    📝 Notas:")
                        for nota in pedido['notas']:
                            print(f"      • {nota['texto']}")
        else:
            print("  (No hay pedidos entregados aún)")

        input("\nPresione Enter para volver al mapa de mesas...")

    def _mostrar_detalle_pedido(self, pedido):
        """Muestra los detalles de un pedido individual"""
        nota_texto = ""
        if 'notas' in pedido and pedido['notas']:
            nota_texto = f" (Nota: {pedido['notas'][-1]['texto']})"
        elif 'nota' in pedido:
            nota_texto = f" (Nota: {pedido['nota']})"
        
        estado_pedido = self.estados_pedido.get(pedido.get('estado_cocina'), '⏳ Pendiente')
        entregado = " (✅ Entregado)" if pedido.get('entregado') else ""
        es_bebida = " (🥤 Bebida)" if pedido.get('es_bebida') else ""
        
        print(f"  - {pedido['cantidad']}x {pedido['nombre']} [{estado_pedido}{entregado}{es_bebida}]{nota_texto}")

    def _validar_mesa(self, mesa_id):
        """Valida que la mesa exista y devuelve la lista asociada"""
        if mesa_id not in self.sistema_mesas.mesas:
            print(f"⚠️ Error: Mesa {mesa_id} no encontrada")
            return None
        return self.sistema_mesas.mesas[mesa_id]

    def procesar_pedidos_mesa(self, mesa_id):
        """Procesa los pedidos de una mesa específica"""
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
                    pedidos_procesados.append(pedido_info)
        return pedidos_procesados 