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

class VisualizadorPedidos:
    """Clase para manejar toda la visualización de pedidos"""

    def __init__(self, sistema_mesas):
        self.sistema_mesas = sistema_mesas
        self.estados_pedido = {
            'preparar': '🟢 PREPARAR AHORA',
            'normal': '🟡 NORMAL',
            'cancelado': '🔴 CANCELADO',
            'agregado': '🔵 AGREGADO',
            'en_preparacion': '👨‍🍳 EN PREPARACIÓN',
            'listo': '✅ LISTO PARA ENTREGAR'
        }

    def mostrar_mapa_mesas(self):
        """Muestra un mapa completo de todas las mesas con su estado"""
        while True:
            print("\n=== MAPA DEL RESTAURANTE ===")
            print("\nMesas disponibles:")
            
            # Primero mostrar todas las mesas y su estado
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
                    retraso = f" (⏳ Retraso: {pedido.get('retraso_minutos')} min)" if pedido.get('retraso_minutos') else ""
                    hora_envio = f" [Enviado: {pedido.get('hora_envio', 'No registrada')}]"
                    print(f"  - {pedido.get('cantidad', 1)}x {pedido.get('nombre', 'Desconocido')} {estado}{retraso}{hora_envio}")
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
                    print(f"  - {pedido.get('cantidad', 1)}x {pedido.get('nombre', 'Desconocido')} ✅ Entregado")
        else:
            print("  (No hay pedidos entregados aún)")

        input("\nPresione Enter para volver al mapa de mesas...")

    def _mostrar_detalle_pedido_mapa(self, pedido):
        """Muestra los detalles del pedido para el mapa, incluyendo notas y estado"""
        nota_texto = ""
        if 'notas' in pedido and pedido['notas']:
            nota_texto = f" (Nota: {pedido['notas'][-1]['texto']})"
        elif 'nota' in pedido:
            nota_texto = f" (Nota: {pedido['nota']})"
        
        estado_pedido = self.estados_pedido.get(pedido.get('estado_cocina'), '⏳ Pendiente')
        hora = f" [{pedido.get('hora', 'No registrada')}]"
        es_bebida = " (🥤 Bebida)" if pedido.get('es_bebida') else ""
        
        # Mostrar el historial de estados de manera concisa
        historial_estados = ""
        if 'historial_estados' in pedido and pedido['historial_estados']:
            historial_estados = " ["
            for estado_info in pedido['historial_estados']:
                historial_estados += f"{estado_info['estado']} ({estado_info['hora']}) → "
            historial_estados = historial_estados[:-3] + "]"  # Remover la última flecha
        
        print(f"  - {pedido['cantidad']}x {pedido['nombre']} [{estado_pedido}]{hora}{nota_texto}{es_bebida}{historial_estados}")

    def _mostrar_clientes_mesa(self, mesa):
        """Muestra los clientes y pedidos de una mesa"""
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre']:
                print(f"\n👤 {mesa[cliente_key]['nombre']}:")
                for pedido in mesa[cliente_key]['pedidos']:
                    self._mostrar_detalle_pedido(pedido)

    def _mostrar_detalle_pedido(self, pedido):
        """Muestra los detalles de un pedido individual, incluyendo notas y tiempo"""
        nota_texto = ""
        if 'notas' in pedido and pedido['notas']:
            nota_texto = f" (Nota: {pedido['notas'][-1]['texto']})"
        elif 'nota' in pedido:
            nota_texto = f" (Nota: {pedido['nota']})"
        entregado = " (✅ Entregado)" if pedido.get('entregado') else ""
        tiempo = self._calcular_tiempo_transcurrido(pedido.get('hora', ''))
        tiempo_str = f" [Hace {tiempo}]" if tiempo else ""
        retraso = f" (⏳ Retraso: {pedido.get('retraso_minutos')} min)" if pedido.get('retraso_minutos') else ""
        estado = pedido.get('estado_cocina', '🟡 Pendiente')
        notas_adicionales = ""
        if 'notas' in pedido and len(pedido['notas']) > 1:
            notas_adicionales = "\n   Notas adicionales:"
            for n in pedido['notas'][:-1]:
                notas_adicionales += f"\n    - {n['texto']} ({n['hora']})"
        elif 'notas' in pedido and len(pedido['notas']) == 1 and 'nota' in pedido:
            notas_adicionales = "\n   Notas adicionales:\n    - {pedido['nota']} (antigua)"

        # Mostrar el historial de estados
        historial_estados = ""
        if 'historial_estados' in pedido and pedido['historial_estados']:
            historial_estados = "\n   📋 Historial de estados:"
            for estado_info in pedido['historial_estados']:
                historial_estados += f"\n    - {estado_info['estado']} ({estado_info['hora']})"

        print(f"  - {estado} - {pedido['cantidad']}x {pedido['nombre']}{nota_texto}{entregado}{tiempo_str}{retraso}{notas_adicionales}{historial_estados}")

    def _calcular_tiempo_transcurrido(self, hora_pedido):
        """Calcula el tiempo transcurrido desde la hora del pedido en minutos"""
        if not hora_pedido:
            return None

        try:
            hora_actual = datetime.now()
            hora_pedido = datetime.strptime(hora_pedido, "%H:%M hs")
            diferencia = hora_actual - hora_pedido

            minutos = int(diferencia.total_seconds() / 60)
            return f"{minutos} min"
        except ValueError:
            return None

    def _validar_mesa(self, mesa_id):
        """Valida que la mesa exista y tenga estructura correcta"""
        if mesa_id not in self.sistema_mesas.mesas:
            return False
        if len(self.sistema_mesas.mesas[mesa_id]) == 0:
            return False
        return True

class SistemaPedidosCocina:
    """Sistema de gestión de pedidos para la cocina de un restaurante."""

    def __init__(self, sistema_mesas):
        """Inicializa el sistema con dependencias necesarias."""
        self.sistema_mesas = sistema_mesas
        self.notificaciones = ManejadorNotificaciones(sistema_mesas)
        self.estados_pedido = {
            'pendiente': '🟡 Pendiente en cocina',
            'en_preparacion': '👨‍🍳 EN PREPARACIÓN',
            'listo': '✅ LISTO PARA ENTREGAR',
            'cancelado': '🔴 CANCELADO'
        }

    def mostrar_mapa_mesas(self):
        """Muestra un mapa completo de todas las mesas con su estado"""
        while True:
            print("\n=== MAPA DEL RESTAURANTE ===")
            print("\nMesas disponibles:")
            
            # Primero mostrar todas las mesas y su estado
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
                    retraso = f" (⏳ Retraso: {pedido.get('retraso_minutos')} min)" if pedido.get('retraso_minutos') else ""
                    hora_envio = f" [Enviado: {pedido.get('hora_envio', 'No registrada')}]"
                    print(f"  - {pedido.get('cantidad', 1)}x {pedido.get('nombre', 'Desconocido')} {estado}{retraso}{hora_envio}")
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
                    print(f"  - {pedido.get('cantidad', 1)}x {pedido.get('nombre', 'Desconocido')} ✅ Entregado")
        else:
            print("  (No hay pedidos entregados aún)")

        input("\nPresione Enter para volver al mapa de mesas...")

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

    def _validar_mesa(self, mesa_id):
        """Valida que la mesa exista y devuelve su data."""
        if mesa_id not in self.sistema_mesas.mesas:
            print(f"⚠️ Error: Mesa {mesa_id} no encontrada")
            return None
        return self.sistema_mesas.mesas[mesa_id]

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
                        pedido_info = self._crear_info_pedido(pedido, mesa_id, cliente_key, cliente)
                        pedidos.append(pedido_info)
        
        return pedidos