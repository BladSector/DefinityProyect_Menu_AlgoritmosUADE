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
        print("\n--- MAPA DEL RESTAURANTE ---")

        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            estado = "🟢 Libre" if mesa['estado'] == 'libre' else "🟠 Ocupada"

            print(f"\n{mesa['nombre']} [{estado}]")

            if mesa['estado'] == 'ocupada':
                for i in range(1, mesa['capacidad'] + 1):
                    cliente_key = f"cliente_{i}"
                    if mesa[cliente_key]['nombre']:
                        print(f"\n 👤 {mesa[cliente_key]['nombre']}:")
                        for pedido in mesa[cliente_key]['pedidos']:
                            self._mostrar_detalle_pedido_mapa(pedido)

    def _mostrar_detalle_pedido_mapa(self, pedido):
        """Muestra los detalles del pedido para el mapa, incluyendo notas y estado"""
        nota_texto = ""
        if 'notas' in pedido and pedido['notas']:
            nota_texto = f" (Nota: {pedido['notas'][-1]['texto']})"
        elif 'nota' in pedido:
            nota_texto = f" (Nota: {pedido['nota']})"
        estado_pedido = self.estados_pedido.get(pedido.get('estado_cocina'), '⏳ Pendiente')
        print(f"  - {pedido['cantidad']}x {pedido['nombre']} [{estado_pedido}]{nota_texto}")

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

        print(f"  - {estado} - {pedido['cantidad']}x {pedido['nombre']}{nota_texto}{entregado}{tiempo_str}{retraso}{notas_adicionales}")

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
        print("\n--- MAPA DEL RESTAURANTE ---")

        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            estado = "🟢 Libre" if mesa['estado'] == 'libre' else "🟠 Ocupada"

            print(f"\n{mesa['nombre']} [{estado}]")

            if mesa['estado'] == 'ocupada':
                for i in range(1, mesa['capacidad'] + 1):
                    cliente_key = f"cliente_{i}"
                    if mesa[cliente_key]['nombre']:
                        print(f"\n 👤 {mesa[cliente_key]['nombre']}:")
                        for pedido in mesa[cliente_key]['pedidos']:
                            self._mostrar_detalle_pedido_mapa_mapa(pedido)

    def _mostrar_detalle_pedido_mapa_mapa(self, pedido):
        """Muestra los detalles del pedido para el mapa, incluyendo estado"""
        estado_pedido = self.estados_pedido.get(pedido.get('estado_cocina'), '⏳ Pendiente')
        es_bebida = " (🥤 Bebida)" if pedido.get('es_bebida') else ""
        print(f"  - {pedido['cantidad']}x {pedido['nombre']} [{estado_pedido}{es_bebida}]")


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
            if not pedidos_cocina:
                print("  No hay pedidos de cocina activos para esta mesa.")
            else:
                for i, pedido in enumerate(pedidos_cocina, 1):
                    estado = pedido.get('estado_cocina', self.determinar_estado_pedido(pedido))
                    nota_texto = ""
                    if pedido.get('notas'):
                        nota_texto = f" (Nota: {pedido['notas'][-1]['texto']})"
                    elif pedido.get('nota'):
                        nota_texto = f" (Nota: {pedido['nota']})"
                    tiempo = self.visualizador._calcular_tiempo_transcurrido(pedido.get('hora', ''))
                    tiempo_str = f" [Hace {tiempo}]" if tiempo else ""
                    notas_adicionales = ""
                    if pedido.get('notas') and len(pedido['notas']) > 1:
                        notas_adicionales = "\n   Notas adicionales:"
                        for n in pedido['notas'][:-1]:
                            notas_adicionales += f"\n    - {n['texto']} ({n['hora']})"
                    elif pedido.get('notas') and len(pedido['notas']) == 1 and pedido.get('nota'):
                        notas_adicionales = "\n   Notas adicionales:\n    - {pedido['nota']} (antigua)"

                    print(f"{i}. {estado} - {pedido['cliente']}{tiempo_str}")
                    print(f"  {pedido['cantidad']}x {pedido['nombre']}{nota_texto}{notas_adicionales}")
                    print(f"  Hora: {pedido.get('hora', 'No registrada')}")

            # Opciones para la mesa
            print("\nOpciones:")
            print("1. Seleccionar pedido para gestión")
            print("0. Volver a lista de mesas")

            opcion_accion = input("\nSeleccione una opción: ")

            if opcion_accion == "0":
                break
            elif opcion_accion == "1":
                self._gestionar_pedido_seleccionado(mesa_id)

    def _gestionar_pedido_seleccionado(self, mesa_id):
        """Gestiona un pedido específico seleccionado por el usuario para la mesa actual"""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return

        mesa_info = mesa_data[0]
        pedidos_cocina = [p for p in self.procesar_pedidos_mesa(mesa_id) if not p.get('es_bebida')]

        try:
            num_pedido = int(input("Número de pedido a gestionar: ")) - 1
            if num_pedido < 0 or num_pedido >= len(pedidos_cocina):
                print("Número de pedido inválido")
                return

            pedido = pedidos_cocina[num_pedido]
            pedido['mesa_id'] = mesa_id # Ya tenemos el ID de la mesa
            if self._mostrar_menu_gestion_pedido(pedido):
                return # Volver a la lista de pedidos activos
        except ValueError:
            print("Por favor ingrese un número válido")

    def _mostrar_menu_gestion_pedido(self, pedido):
        """Muestra el menú de gestión para un pedido específico"""
        print(f"\nGestión del pedido: {pedido['nombre']}")
        print(f"Cliente: {pedido['cliente']}")
        print(f"Estado actual: {pedido.get('estado_cocina', 'Pendiente')}")
        if pedido.get('notas'):
            print(f"Última nota: {pedido['notas'][-1]['texto']}")
        elif pedido.get('nota'):
            print(f"Nota: {pedido['nota']}")
        try:
            while True:
                print("\n1. Marcar como en preparación")
                print("2. Marcar como listo para entregar")
                print("3. Notificar retraso")
                print("0. Volver")

                opcion_gestion = input("\nSeleccione acción: ")

                if opcion_gestion == "0":
                    return False
                elif opcion_gestion == "1":
                    if self.marcar_en_preparacion(pedido['mesa_id'], pedido):
                        return True # Volver a la lista de pedidos activos
                elif opcion_gestion == "2":
                    if self.marcar_listo_entrega(pedido['mesa_id'], pedido):
                        return True # Volver a la lista de pedidos activos
                elif opcion_gestion == "3":
                    self.notificar_retraso_interactivo(pedido['mesa_id'], pedido)
                elif opcion_gestion == "0":
                    return False
        except ValueError:
            print("Opción inválida")
        return False

    def marcar_en_preparacion(self, mesa_id, pedido):
        """Marca un pedido como en preparación y notifica"""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return False

        mesa = mesa_data[0]
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre'] == pedido['cliente']:
                for p in mesa[cliente_key]['pedidos']:
                    if p['id'] == pedido['id']:
                        p['estado_cocina'] = self.estados_pedido['en_preparacion']
                        p['hora_preparacion'] = datetime.now().strftime("%H:%M hs")

                        mensaje = f"Pedido en preparación: {pedido['nombre']} para {pedido['cliente']}"
                        if not self.notificaciones.registrar_notificacion(mesa_id, mensaje, tipo="cocina"): # Especificar tipo cocina
                            return False

                        try:
                            self.sistema_mesas.guardar_mesas()
                        except Exception as e:
                            print(f"⚠️ Error al guardar mesas (marcar_en_preparacion): {e}")
                            return False
                        print("\n👨‍🍳 Pedido marcado como en preparación")
                        return True
        print(f"⚠️ Error: No se pudo marcar como en preparación el pedido {pedido['nombre']} para la mesa {mesa_id}")
        return False

    def marcar_listo_entrega(self, mesa_id, pedido):
        """Marca un pedido como listo para entregar y notifica, verificando preparación"""
        if pedido.get('estado_cocina') != self.estados_pedido['en_preparacion']:
            print(f"\n⚠️ Error: El pedido '{pedido['nombre']}' aún no ha sido marcado como 'En Preparación'.")
            return False

        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return False

        mesa = mesa_data[0]
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre'] == pedido['cliente']:
                for p in mesa[cliente_key]['pedidos']:
                    if p['id'] == pedido['id']:
                        p['estado_cocina'] = self.estados_pedido['listo']
                        p['hora_listo'] = datetime.now().strftime("%H:%M hs")
                        p['entregado'] = False # Se marca como no entregado hasta que el mozo lo haga

                        mensaje = f"Pedido listo para entregar: {pedido['nombre']} para {pedido['cliente']}"
                        if not self.notificaciones.registrar_notificacion(mesa_id, mensaje, tipo="cocina"): # Especificar tipo cocina
                            return False

                        try:
                            self.sistema_mesas.guardar_mesas()
                        except Exception as e:
                            print(f"⚠️ Error al guardar mesas (marcar_listo_entrega): {e}")
                            return False
                        print("\n✅ Pedido marcado como listo para entregar")
                        return True
        print(f"⚠️ Error: No se pudo marcar como listo para entregar el pedido {pedido['nombre']} para la mesa {mesa_id}")
        return False

    def notificar_retraso_interactivo(self, mesa_id, pedido):
        """Notifica retraso con opciones predefinidas y asigna retraso al pedido"""
        print("\nSeleccione tiempo de retraso:")
        print("1. 10 minutos")
        print("2. 20 minutos")
        print("3. 30 minutos")
        print("0. Cancelar")

        try:
            opcion = int(input("\nOpción: "))
            minutos = {1: 10, 2: 20, 3: 30}.get(opcion)

            if minutos:
                mesa_data = self._validar_mesa(mesa_id)
                if not mesa_data:
                    return

                mesa = mesa_data[0]
                for i in range(1, mesa['capacidad'] + 1):
                    cliente_key = f"cliente_{i}"
                    if mesa[cliente_key]['nombre'] == pedido['cliente']:
                        for p in mesa[cliente_key]['pedidos']:
                            if p['id'] == pedido['id']:
                                p['retraso_minutos'] = minutos

                                mensaje = f"Retraso en pedido: {pedido['nombre']} tiene {minutos} min de retraso"
                                if not self.notificaciones.registrar_notificacion(mesa_id, mensaje, tipo="cliente"): # Notificar al cliente
                                    return

                                try:
                                    self.sistema_mesas.guardar_mesas()
                                except Exception as e:
                                    print(f"⚠️ Error al guardar mesas (notificar_retraso): {e}")
                                    return
                                print(f"\n⚠️ Notificación de retraso de {minutos} min enviada")
                                return
            elif opcion == 0:
                return
        except ValueError:
            print("Opción inválida")

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
        if pedido.get('cancelado'):
            return self.estados_pedido['cancelado']
        elif pedido.get('urgente'):
            return self.estados_pedido['preparar']
        elif pedido.get('estado_cocina'):
            return pedido['estado_cocina']
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