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
        self.visualizador = VisualizadorPedidos(sistema_mesas)
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
        self.visualizador.mostrar_mapa_mesas()

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

    def _mostrar_detalle_pedido_mapa_mapa(self, pedido):
        """Muestra los detalles del pedido para el mapa, incluyendo estado"""
        self._mostrar_detalle_pedido_mapa(pedido)

    def mostrar_pedidos_activos(self):
        """Muestra todos los pedidos activos con opciones de gestión"""
        while True:
            mesas_activas = self._recolectar_mesas_activas()
            if not mesas_activas:
                print("No hay pedidos activos en cocina")
                input("\nPresione Enter para volver...")
                return

            self._mostrar_lista_mesas(mesas_activas)
            opcion_mesa = self._solicitar_opcion_mesa(mesas_activas)

            if opcion_mesa == 0:
                return

            mesa_id = list(mesas_activas.keys())[opcion_mesa-1]
            self._gestionar_mesa_seleccionada(mesa_id)

    def _recolectar_mesas_activas(self):
        """Recolecta mesas con pedidos activos excluyendo bebidas"""
        mesas_activas = {}
        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            if not self._validar_mesa_estructura(mesa_data):
                continue

            mesa = mesa_data[0]
            if mesa['estado'] == 'ocupada':
                pedidos = self.procesar_pedidos_mesa(mesa_id)
                pedidos_cocina = [p for p in pedidos if not p.get('es_bebida')]
                if pedidos_cocina:
                    mesas_activas[mesa_id] = {
                        'nombre': mesa['nombre'],
                        'pedidos': pedidos_cocina,
                        'comentarios': mesa.get('comentarios_camarero', [])
                    }
        return mesas_activas

    def _mostrar_lista_mesas(self, mesas_activas):
        """Muestra lista numerada de mesas con pedidos activos con resumen de estado"""
        print("\n--- PEDIDOS ACTIVOS EN COCINA ---")
        print("\nMesas con pedidos activos:")
        for i, mesa_id in enumerate(mesas_activas.keys(), 1):
            num_pendientes = sum(1 for p in mesas_activas[mesa_id]['pedidos'] if p.get('estado_cocina') not in [self.estados_pedido['en_preparacion'], self.estados_pedido['listo']])
            num_en_preparacion = sum(1 for p in mesas_activas[mesa_id]['pedidos'] if p.get('estado_cocina') == self.estados_pedido['en_preparacion'])
            num_listos = sum(1 for p in mesas_activas[mesa_id]['pedidos'] if p.get('estado_cocina') == self.estados_pedido['listo'])
            print(f"{i}. {mesas_activas[mesa_id]['nombre']} (Pendientes: {num_pendientes}, En Prep: {num_en_preparacion}, Listos: {num_listos})")
        print("\n0. Volver al menú principal")

    def _solicitar_opcion_mesa(self, mesas_activas):
        """Solicita y valida la selección de mesa"""
        while True:
            try:
                opcion = int(input("Seleccione una mesa (número): "))
                if 0 <= opcion <= len(mesas_activas):
                    return opcion
                print("Número de mesa inválido")
            except ValueError:
                print("Por favor ingrese un número válido")

    def _gestionar_mesa_seleccionada(self, mesa_id):
        """Gestiona los pedidos de una mesa específica"""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return

        mesa_info = mesa_data[0]

        while True:
            print(f"\n---{mesa_info['nombre']}---")
            print("-" * 40)

            # Mostrar pedidos numerados con estado y notas (solo los de cocina)
            pedidos_cocina = [p for p in self.procesar_pedidos_mesa(mesa_id) if not p.get('es_bebida')]
            print("\n🍽️ Pedidos (Cocina):")
            
            # Separar pedidos por estado
            pedidos_nuevos = []
            pedidos_en_preparacion = []
            pedidos_listos = []
            
            for pedido in pedidos_cocina:
                if pedido.get('estado_cocina') == '✅ LISTO PARA ENTREGAR':
                    pedidos_listos.append(pedido)
                elif pedido.get('estado_cocina') == '👨‍🍳 EN PREPARACIÓN':
                    pedidos_en_preparacion.append(pedido)
                else:
                    pedidos_nuevos.append(pedido)

            # Mostrar pedidos nuevos primero
            if pedidos_nuevos:
                print("\n📝 Pedidos Nuevos:")
                for i, pedido in enumerate(pedidos_nuevos, 1):
                    hora_envio = f" [Enviado: {pedido.get('hora_envio', 'No registrada')}]"
                    print(f"{i}. {pedido['cantidad']}x {pedido['nombre']} - Cliente: {pedido['cliente']}{hora_envio}")
                    if pedido.get('notas'):
                        print(f"   📝 Notas: {pedido['notas'][-1]['texto']}")

            # Mostrar pedidos en preparación
            if pedidos_en_preparacion:
                print("\n👨‍🍳 Pedidos en Preparación:")
                for i, pedido in enumerate(pedidos_en_preparacion, len(pedidos_nuevos) + 1):
                    hora_envio = f" [Enviado: {pedido.get('hora_envio', 'No registrada')}]"
                    print(f"{i}. {pedido['cantidad']}x {pedido['nombre']} - Cliente: {pedido['cliente']}{hora_envio}")
                    if pedido.get('notas'):
                        print(f"   📝 Notas: {pedido['notas'][-1]['texto']}")

            # Mostrar pedidos listos para entregar
            if pedidos_listos:
                print("\n✅ Pedidos Listos para Entregar:")
                for i, pedido in enumerate(pedidos_listos, len(pedidos_nuevos) + len(pedidos_en_preparacion) + 1):
                    hora_envio = f" [Enviado: {pedido.get('hora_envio', 'No registrada')}]"
                    print(f"{i}. {pedido['cantidad']}x {pedido['nombre']} - Cliente: {pedido['cliente']}{hora_envio}")
                    if pedido.get('notas'):
                        print(f"   📝 Notas: {pedido['notas'][-1]['texto']}")

            print("\n0. Volver al menú anterior")

            try:
                opcion = int(input("\nSeleccione un pedido para gestionar (número): "))
                if opcion == 0:
                    return

                # Determinar en qué lista está el pedido seleccionado
                if 1 <= opcion <= len(pedidos_nuevos):
                    pedido_seleccionado = pedidos_nuevos[opcion - 1]
                elif len(pedidos_nuevos) < opcion <= len(pedidos_nuevos) + len(pedidos_en_preparacion):
                    pedido_seleccionado = pedidos_en_preparacion[opcion - len(pedidos_nuevos) - 1]
                elif len(pedidos_nuevos) + len(pedidos_en_preparacion) < opcion <= len(pedidos_nuevos) + len(pedidos_en_preparacion) + len(pedidos_listos):
                    pedido_seleccionado = pedidos_listos[opcion - len(pedidos_nuevos) - len(pedidos_en_preparacion) - 1]
                else:
                    print("Número de pedido inválido")
                    continue

                self._gestionar_estado_pedido(mesa_id, pedido_seleccionado)
            except ValueError:
                print("Por favor ingrese un número válido")

    def _gestionar_estado_pedido(self, mesa_id, pedido):
        """Gestiona el cambio de estado de un pedido específico"""
        print(f"\n--- Gestionando pedido: {pedido['cantidad']}x {pedido['nombre']} ---")
        print(f"Cliente: {pedido['cliente']}")
        
        # Si el pedido ya está listo para entregar, no permitir más cambios
        if pedido.get('estado_cocina') == '✅ LISTO PARA ENTREGAR':
            print("\n⚠️ Este pedido ya está listo para entregar y no puede ser modificado.")
            input("\nPresione Enter para volver...")
            return
        
        # Determinar opciones disponibles según el estado actual
        if pedido.get('estado_cocina') == '👨‍🍳 EN PREPARACIÓN':
            print("\n1. Marcar como LISTO PARA ENTREGAR")
            print("0. Volver")
            
            opcion = input("\nSeleccione una opción: ")
            if opcion == "1":
                self._actualizar_estado_pedido(mesa_id, pedido, 'listo')
                print("\n✅ Pedido marcado como LISTO PARA ENTREGAR")
            elif opcion == "0":
                return
            else:
                print("Opción inválida")
        else:  # Pedido nuevo
            print("\n1. Marcar como EN PREPARACIÓN")
            print("0. Volver")
            
            opcion = input("\nSeleccione una opción: ")
            if opcion == "1":
                self._actualizar_estado_pedido(mesa_id, pedido, 'en_preparacion')
                print("\n✅ Pedido marcado como EN PREPARACIÓN")
            elif opcion == "0":
                return
            else:
                print("Opción inválida")

    def _actualizar_estado_pedido(self, mesa_id, pedido, nuevo_estado):
        """Actualiza el estado de un pedido específico"""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return False

        mesa = mesa_data[0]
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre'] == pedido['cliente']:
                for p in mesa[cliente_key]['pedidos']:
                    if p['id'] == pedido['id']:
                        # Registrar el historial de estados si no existe
                        if 'historial_estados' not in p:
                            p['historial_estados'] = []
                        
                        # Agregar el nuevo estado al historial
                        p['historial_estados'].append({
                            'estado': self.estados_pedido[nuevo_estado],
                            'hora': datetime.now().strftime("%H:%M hs")
                        })
                        
                        # Actualizar el estado actual
                        p['estado_cocina'] = self.estados_pedido[nuevo_estado]
                        try:
                            self.sistema_mesas.guardar_mesas()
                            return True
                        except Exception as e:
                            print(f"⚠️ Error al guardar mesas: {e}")
                            return False
        return False

    def _validar_mesa_y_pedido(self, mesa_id, pedido):
        """Valida que existan la mesa y el pedido"""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return False

        mesa = mesa_data[0]
        pedido_encontrado = False
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre'] == pedido['cliente']:
                for p in mesa[cliente_key]['pedidos']:
                    if p['id'] == pedido['id']:
                        pedido_encontrado = True
                        break
                if pedido_encontrado:
                    break

        if not pedido_encontrado:
            print(f"⚠️ Error: Pedido con ID {pedido['id']} no encontrado en la mesa {mesa_id} para el cliente {pedido['cliente']}")
            return False

        return True

    def determinar_estado_pedido(self, pedido):
        """Determina el estado de un pedido basado en sus propiedades"""
        if pedido.get('estado_cocina'):
            return pedido['estado_cocina']
        elif pedido.get('cancelado'):
            return self.estados_pedido['cancelado']
        elif pedido.get('urgente'):
            return self.estados_pedido['preparar']
        else:
            return self.estados_pedido['normal']

    def procesar_pedidos_mesa(self, mesa_id):
        """Procesa los pedidos de una mesa específica, marcando las bebidas"""
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

                    es_bebida = 'bebida' in pedido['nombre'].lower()
                    estado_cocina = pedido.get('estado_cocina')
                    if not estado_cocina:
                        estado_cocina = self.determinar_estado_pedido(pedido)

                    pedido_procesado = {
                        'id': pedido['id'],
                        'nombre': pedido['nombre'],
                        'cantidad': pedido['cantidad'],
                        'cliente': mesa[cliente_key]['nombre'],
                        'mesa_id': mesa_id,
                        'mesa_nombre': mesa['nombre'],
                        'hora': pedido.get('hora', 'No registrada'),
                        'notas': pedido.get('notas') if 'notas' in pedido else ([{'texto': pedido['nota'], 'hora': 'antigua'}] if 'nota' in pedido else []),
                        'estado_cocina': estado_cocina,
                        'retraso_minutos': pedido.get('retraso_minutos'),
                        'es_bebida': es_bebida
                    }
                    pedidos_procesados.append(pedido_procesado)

        return pedidos_procesados

    def _validar_mesa_estructura(self, mesa_data):
        """Valida que la estructura de los datos de la mesa sea correcta"""
        if not isinstance(mesa_data, list) or len(mesa_data) == 0 or not isinstance(mesa_data[0], dict):
            print(f"⚠️ Error: Estructura de datos incorrecta para la mesa")
            return False
        return True

    def _validar_mesa(self, mesa_id):
        """Valida que la mesa exista y devuelve su data"""
        if mesa_id not in self.sistema_mesas.mesas:
            print(f"⚠️ Error: Mesa {mesa_id} no encontrada")
            return None
        return self.sistema_mesas.mesas[mesa_id]