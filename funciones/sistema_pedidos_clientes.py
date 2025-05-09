from datetime import datetime
import os
import json

HISTORIAL_DIR = "historial_pagos"

class SistemaPedidosClientes:
    def __init__(self, sistema_mesas):
        self.sistema_mesas = sistema_mesas
        self.cliente_actual = None # Para rastrear el cliente actual en pagos individuales

    def _obtener_mesa(self, mesa_id):
        """Método interno para obtener la información de una mesa."""
        return self.sistema_mesas.obtener_mesa(mesa_id)

    def _guardar_cambios(self):
        """Método interno para guardar los cambios en las mesas."""
        self.sistema_mesas.guardar_mesas()

    def _limpiar_mesa(self, mesa_id):
        """Método interno para limpiar una mesa."""
        self.sistema_mesas.limpiar_mesa(mesa_id)

    def hacer_pedido(self, mesa_id, cliente_key):
        """Gestiona el proceso de pedido con el menú completo integrado."""
        mesa = self._obtener_mesa(mesa_id)
        if not mesa:
            print(f"\n⚠️ Error: Mesa {mesa_id} no encontrada.")
            return

        cliente = mesa.get(cliente_key)
        if not cliente:
            print(f"\n⚠️ Error: Cliente {cliente_key} no encontrado en la mesa {mesa_id}.")
            return

        while True:
            print("\n--- HACER PEDIDO ---")
            print("1. Ver menú completo y seleccionar")
            print("2. Filtrar por categoría")
            print("3. Filtrar por dieta")
            print("0. Volver al menú principal")

            try:
                opcion_menu = int(input("Seleccione cómo buscar platos: "))

                if opcion_menu == 0:
                    break
                elif opcion_menu == 1:
                    todos_platos = self.sistema_mesas.mostrar_menu_completo()
                    plato = self._seleccionar_plato_del_menu(todos_platos)
                elif opcion_menu == 2:
                    categorias = self.sistema_mesas.filtrar_por_categoria()
                    if not categorias:
                        print("\nℹ️ No hay categorías disponibles.")
                        continue
                    categoria_seleccionada = self._seleccionar_categoria(categorias)
                    if categoria_seleccionada:
                        platos_categoria = self.sistema_mesas.obtener_platos_por_categoria(categoria_seleccionada)
                        plato = self._seleccionar_plato_de_lista(platos_categoria, f"Platos en {categoria_seleccionada.upper()}")
                    else:
                        continue
                elif opcion_menu == 3:
                    dietas = self.sistema_mesas.obtener_dietas_disponibles()
                    if not dietas:
                        print("\nℹ️ No hay dietas especiales disponibles.")
                        continue
                    dieta_seleccionada = self._seleccionar_dieta(dietas)
                    if dieta_seleccionada:
                        platos_dieta = self.sistema_mesas.obtener_platos_por_dieta(dieta_seleccionada)
                        plato = self._seleccionar_plato_de_lista(platos_dieta, f"Platos {dieta_seleccionada.upper()}")
                    else:
                        continue
                else:
                    print("Opción inválida")
                    continue

                if plato:
                    cantidad = 1
                    nuevo_pedido = {
                        'id': plato['id'],
                        'nombre': plato['nombre'],
                        'cantidad': 1,
                        'precio': plato['precio'],
                        'hora': datetime.now().strftime("%H:%M hs"),
                        'en_cocina': False
                    }
                    cliente['pedidos'].append(nuevo_pedido)
                    self._guardar_cambios()
                    print(f"\n✅ {cantidad} x {plato['nombre']} agregado(s) a tu pedido")
                    print("Recuerda enviar los pedidos a cocina cuando termines")

            except ValueError:
                print("Por favor ingrese una opción numérica válida")

    def _seleccionar_plato_del_menu(self, todos_platos):
        """Permite al usuario seleccionar un plato del menú completo."""
        while True:
            try:
                print("\n--- SELECCIÓN ---")
                print("Ingrese el número del plato que desea (0 para volver)")
                seleccion = int(input("> "))

                if seleccion == 0:
                    return None
                elif 1 <= seleccion <= len(todos_platos):
                    plato_seleccionado = todos_platos[seleccion - 1]['plato']
                    print(f"\nSeleccionaste: {plato_seleccionado['nombre']} - ${plato_seleccionado['precio']}")
                    return plato_seleccionado
                else:
                    print("⚠️ Número inválido. Intente nuevamente.")
            except ValueError:
                print("⚠️ Por favor ingrese un número.")

    def _seleccionar_categoria(self, categorias):
        """Permite al usuario seleccionar una categoría."""
        while True:
            print("\n--- SELECCIONAR CATEGORÍA ---")
            print("Categorías disponibles:")
            for i, cat in enumerate(categorias, 1):
                print(f"{i}. {cat.capitalize()}")
            print("0. Volver")
            opcion = input("Seleccione categoría: ")
            if opcion == "0":
                return None
            try:
                opcion = int(opcion)
                if 1 <= opcion <= len(categorias):
                    return categorias[opcion - 1]
                else:
                    print("⚠️ Opción inválida.")
            except ValueError:
                print("⚠️ Por favor ingrese un número.")

    def _seleccionar_dieta(self, dietas):
        """Permite al usuario seleccionar una dieta."""
        while True:
            print("\n--- SELECCIONAR DIETA ---")
            print("Dietas disponibles:")
            for i, dieta in enumerate(dietas, 1):
                print(f"{i}. {dieta}")
            print("0. Volver")
            opcion = input("Seleccione dieta: ")
            if opcion == "0":
                return None
            try:
                opcion = int(opcion)
                if 1 <= opcion <= len(dietas):
                    return dietas[opcion - 1]
                else:
                    print("⚠️ Opción inválida.")
            except ValueError:
                print("⚠️ Por favor ingrese un número.")

    def _seleccionar_plato_de_lista(self, platos, titulo):
        """Permite al usuario seleccionar un plato de una lista dada."""
        if not platos:
            print(f"\nℹ️ No hay platos disponibles en {titulo}.")
            return None
        while True:
            print(f"\n--- {titulo} ---")
            for i, plato in enumerate(platos, 1):
                dietas = ", ".join(plato.get('dietas', []))
                print(f"{i}. {plato['nombre']} - ${plato['precio']}")
                print(f"   {plato.get('descripcion', '')}")
                if dietas:
                    print(f"   🏷️ {dietas}")
            print("\nIngrese el número del plato que desea (0 para volver)")
            seleccion = input("> ")
            if seleccion == "0":
                return None
            try:
                seleccion = int(seleccion)
                if 1 <= seleccion <= len(platos):
                    return platos[seleccion - 1]
                else:
                    print("⚠️ Número inválido. Intente nuevamente.")
            except ValueError:
                print("⚠️ Por favor ingrese un número.")

    def _mostrar_pedidos_mesa(self, mesa, mostrar_total=False):
        """Función base para mostrar los pedidos de una mesa"""
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
                    retraso = f" (⏳ Retraso: {pedido.get('retraso_minutos')} min)" if pedido.get('retraso_minutos') else ""
                    print(f"  - {pedido.get('cantidad', 1)}x {pedido.get('nombre', 'Desconocido')} {estado}{retraso}")
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
                    print(f"  - {pedido.get('cantidad', 1)}x {pedido.get('nombre', 'Desconocido')} ✅ Entregado")
        else:
            print("  (No hay pedidos entregados aún)")

        # Solicitudes al camarero
        print("\n--- SOLICITUDES AL CAMARERO ---")
        hay_solicitudes = False
        solicitudes_por_cliente = {}
        
        if 'comentarios_camarero' in mesa:
            for comentario in mesa['comentarios_camarero']:
                if not comentario.get('resuelto', False):
                    cliente = comentario.get('cliente', 'Cliente')
                    if cliente not in solicitudes_por_cliente:
                        solicitudes_por_cliente[cliente] = []
                    solicitudes_por_cliente[cliente].append(comentario)
                    hay_solicitudes = True

        if hay_solicitudes:
            for nombre_cliente, solicitudes in solicitudes_por_cliente.items():
                print(f"\n👤 {nombre_cliente}:")
                for solicitud in solicitudes:
                    print(f"  📢 {solicitud.get('mensaje', '')}")
        else:
            print("  (No hay solicitudes pendientes)")

        # Mostrar total acumulado si se solicita
        if mostrar_total:
            total = sum(
                p.get('precio', 0) * p.get('cantidad', 1)
                for i in range(1, mesa.get('capacidad', 0) + 1)
                for cliente in [mesa.get(f"cliente_{i}")] if cliente and cliente.get('nombre')
                for p in cliente.get('pedidos', [])
            )
            print(f"\n💵 TOTAL ACUMULADO: ${total}")

    def mostrar_resumen_grupal(self, mesa_id):
        """Muestra el resumen grupal con estados actualizados."""
        mesa = self._obtener_mesa(mesa_id)
        if not mesa:
            print(f"\n⚠️ Error: Mesa {mesa_id} no encontrada.")
            return

        if 'capacidad' not in mesa:
            print(f"\n⚠️ Error: Información de capacidad no encontrada para la mesa {mesa_id}.")
            return

        print("\n=== RESUMEN GRUPAL ===")
        self._mostrar_pedidos_mesa(mesa, mostrar_total=True)

    def confirmar_envio_cocina(self, mesa_id):
        """Confirma el envío del pedido a cocina si hay pedidos nuevos."""
        mesa = self._obtener_mesa(mesa_id)
        if not mesa:
            print(f"\n⚠️ Error: Mesa {mesa_id} no encontrada.")
            return

        pedidos_enviados = []
        tiene_pedidos_nuevos = False

        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    if not pedido.get('en_cocina', False):
                        tiene_pedidos_nuevos = True
                        pedido['en_cocina'] = True
                        pedido['hora_envio'] = datetime.now().strftime("%H:%M hs")
                        pedidos_enviados.append(f"{pedido.get('cantidad', 1)} x {pedido.get('nombre', 'Desconocido')} ({cliente['nombre']})")

        if not tiene_pedidos_nuevos:
            print("\n⚠️ No hay nuevos pedidos para enviar a cocina")
            return

        self._guardar_cambios()
        print("\n🚀 Pedido enviado a cocina con éxito:")
        for pedido_info in pedidos_enviados:
            print(f"  - {pedido_info}")

    def agregar_nota_pedido(self, mesa_id, cliente_key):
        """Agrega o acumula notas a un pedido seleccionado."""
        mesa = self._obtener_mesa(mesa_id)
        if not mesa:
            print(f"\n⚠️ Error: Mesa {mesa_id} no encontrada.")
            return

        cliente = mesa.get(cliente_key)
        if not cliente or not cliente.get('pedidos'):
            print("\n⚠️ No tienes pedidos registrados")
            return

        while True:
            print("\n=== AGREGAR NOTA A PEDIDO ===")
            print("\n--- TUS PEDIDOS ---")
            for i, pedido in enumerate(cliente['pedidos'], 1):
                nombre_pedido = pedido.get('nombre', 'Desconocido')
                cantidad = pedido.get('cantidad', 1)
                precio = pedido.get('precio', 0)
                print(f"{i}. {nombre_pedido} - {cantidad}x (${precio * cantidad})")

                if 'notas' in pedido and pedido['notas']:
                    print("  Historial de notas:")
                    for idx, nota in enumerate(pedido['notas'], 1):
                        print(f"    {idx}. {nota['texto']} ({nota['hora']})")
                elif 'nota' in pedido:
                    print(f"  Nota actual: {pedido['nota']} (antigua)")

            print("\n0. Volver al menú anterior")
            opcion = input("\nSeleccione el número de pedido: ").strip()

            if opcion == "0":
                print("\nVolviendo al menú anterior...")
                return

            try:
                opcion = int(opcion)
                if 1 <= opcion <= len(cliente['pedidos']):
                    pedido = cliente['pedidos'][opcion - 1]

                    if 'nota' in pedido and pedido['nota']:
                        if 'notas' not in pedido:
                            pedido['notas'] = []
                        pedido['notas'].append({
                            'texto': pedido['nota'],
                            'hora': datetime.now().strftime("%H:%M hs")
                        })
                        del pedido['nota']
                        self._guardar_cambios()

                    while True:
                        print("\n--- ADMINISTRAR NOTAS ---")
                        print(f"Pedido: {pedido.get('nombre', 'Desconocido')}")
                        if 'notas' in pedido and pedido['notas']:
                            print("Notas existentes:")
                            for idx, nota in enumerate(pedido['notas'], 1):
                                print(f"  {idx}. {nota['texto']} ({nota['hora']})")

                        print("\nOpciones:")
                        print("1. Agregar nueva nota")
                        print("2. Eliminar nota específica")
                        print("0. Volver a selección de pedidos")

                        accion = input("\nSeleccione acción: ").strip()

                        if accion == "0":
                            break
                        elif accion == "1":
                            nueva_nota = input("\nIngrese la nueva nota: ").strip()
                            if nueva_nota:
                                if 'notas' not in pedido:
                                    pedido['notas'] = []
                                pedido['notas'].append({
                                    'texto': nueva_nota,
                                    'hora': datetime.now().strftime("%H:%M hs")
                                })
                                self._guardar_cambios()
                                print("\n✅ Nota agregada al historial")
                            else:
                                print("\n⚠️ La nota no puede estar vacía")
                        elif accion == "2":
                            if 'notas' not in pedido or not pedido['notas']:
                                print("\nℹ️ No hay notas para eliminar")
                                continue

                            try:
                                num_nota = int(input("Ingrese número de nota a eliminar (0 para cancelar): "))
                                if num_nota == 0:
                                    continue
                                if 1 <= num_nota <= len(pedido['notas']):
                                    eliminada = pedido['notas'].pop(num_nota - 1)
                                    self._guardar_cambios()
                                    print(f"\n🗑️ Nota eliminada: '{eliminada['texto']}'")
                                else:
                                    print("\n⚠️ Número de nota inválido")
                            except ValueError:
                                print("\n⚠️ Entrada inválida. Intente nuevamente.")
                else:
                    print("\n⚠️ Número de pedido inválido")
            except ValueError:
                print("\n⚠️ Entrada inválida. Intente nuevamente.")

    def llamar_camarero(self, mesa_id, cliente_key):
        """Registra solicitud de camarero con validación."""
        mesa = self._obtener_mesa(mesa_id)
        if not mesa:
            print(f"\n⚠️ Error: Mesa {mesa_id} no encontrada.")
            return False

        cliente = mesa.get(cliente_key)
        if not cliente or not cliente.get('nombre'):
            print(f"\n⚠️ Error: Cliente {cliente_key} no encontrado o sin nombre en la mesa {mesa_id}.")
            return False

        while True:
            print("\n--- LLAMAR AL CAMARERO ---")
            print("Ingrese su solicitud (ej: 'Necesito más pan')")
            print("o escriba '0' para volver al menú anterior")

            mensaje = input("Mensaje: ").strip()

            if mensaje == "0":
                print("\nVolviendo al menú anterior...")
                return False

            if not mensaje:
                print("\n⚠️ Error: No puede enviar una solicitud vacía.")
                continue

            comentario = {
                "mensaje": mensaje,
                "hora": datetime.now().strftime("%H:%M hs"),
                "resuelto": False,
                "cliente": cliente['nombre']
            }

            if 'comentarios_camarero' not in mesa:
                mesa['comentarios_camarero'] = []
            mesa['comentarios_camarero'].append(comentario)

            self._guardar_cambios()
            print("\n✅ Solicitud enviada al camarero")
            return True

    def pagar_cuenta(self, mesa_id):
        """Procesa el pago con validación de entrega y opciones individual/grupal."""
        mesa = self._obtener_mesa(mesa_id)
        if not mesa:
            print(f"\n⚠️ Error: Mesa {mesa_id} no encontrada.")
            return False

        tiene_pedidos = any(
            cliente.get('pedidos')
            for i in range(1, mesa.get('capacidad', 0) + 1)
            if (cliente := mesa.get(f"cliente_{i}")) and cliente.get('pedidos')
        )
        if not tiene_pedidos:
            print("\n⚠️ No hay ningún plato registrado para cobrar")
            return False

        pedidos_no_entregados = []
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente = mesa.get(f"cliente_{i}")
            if cliente and cliente.get('pedidos'):
                for pedido in cliente['pedidos']:
                    if not pedido.get('entregado', False):
                        pedidos_no_entregados.append(pedido['nombre'])

        if pedidos_no_entregados:
            print("\n⚠️ No se puede pagar la cuenta:")
            print("  Los siguientes pedidos aún no han sido entregados:")
            for pedido in set(pedidos_no_entregados):
                print(f"  - {pedido}")
            print("  Por favor, espere a que todos los pedidos sean entregados.")
            return False

        clientes_en_mesa = sum(1 for i in range(1, mesa.get('capacidad', 0) + 1) if mesa.get(f"cliente_{i}", {}).get('nombre'))
        if clientes_en_mesa > 1:
            while True:
                print("\n--- OPCIONES DE PAGO ---")
                print("1. Pagar cuenta individual")
                print("2. Pagar cuenta grupal (todos los clientes)")
                print("0. Volver")
                opcion_pago = input("Seleccione una opción: ")

                if opcion_pago == "1":
                    return self._pagar_individual(mesa)
                elif opcion_pago == "2":
                    return self._pagar_grupal(mesa_id, mesa)
                elif opcion_pago == "0":
                    print("\nVolviendo al menú anterior...")
                    return False
                else:
                    print("\n⚠️ Opción inválida.")
        else:
            return self._pagar_individual(mesa)

    def _pagar_grupal(self, mesa_id, mesa):
        """Procesa el pago grupal de todos los clientes en la mesa."""
        registro_grupal = {
            "mesa": mesa.get('nombre', f"Mesa ID: {mesa_id}"),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "clientes": [],
            "total": 0,
            "notificaciones": mesa.get('notificaciones', []),
            "comentarios_camarero": mesa.get('comentarios_camarero', [])
        }

        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                total_cliente = sum(p.get('precio', 0) * p.get('cantidad', 1) for p in cliente.get('pedidos', []))
                registro_grupal["clientes"].append({
                    "nombre": cliente['nombre'],
                    "pedidos": cliente.get('pedidos', []),
                    "total": total_cliente
                })
                registro_grupal["total"] += total_cliente

        historial_dir = os.path.join("data", "historial_pagos")
        os.makedirs(historial_dir, exist_ok=True)
        fecha_archivo = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_historial = os.path.join(historial_dir, f"mesa_{mesa_id}_{fecha_archivo}.json")

        try:
            with open(archivo_historial, 'w', encoding='utf-8') as f:
                json.dump(registro_grupal, f, indent=2, ensure_ascii=False)
            print(f"📁 Historial de pago grupal guardado en: {archivo_historial}")
        except Exception as e:
            print(f"⚠️ Error al guardar el historial de pago grupal: {e}")
            return False

        # Limpiar la mesa y liberarla
        mesa['estado'] = 'libre'
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            mesa[cliente_key] = {
                'nombre': '',
                'pedidos': []
            }
        
        # Limpiar cualquier notificación o comentario pendiente
        if 'notificaciones' in mesa:
            del mesa['notificaciones']
        if 'comentarios_camarero' in mesa:
            del mesa['comentarios_camarero']

        self._guardar_cambios()

        print(f"\n✅ Cuenta grupal pagada - Total: ${registro_grupal['total']}")
        print("✅ Mesa liberada y lista para nuevos clientes")
        return True

    def _pagar_individual(self, mesa):
        """Procesa el pago individual del cliente actual."""
        cliente_actual_key = self.cliente_actual
        cliente = mesa.get(cliente_actual_key)

        if not cliente or not cliente.get('nombre'):
            print("\n⚠️ Error: No se pudo identificar al cliente actual para el pago individual.")
            return False

        registro_individual = {
            "mesa": mesa.get('nombre', f"Mesa (sin ID)"),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "cliente": cliente['nombre'],
            "pedidos": cliente.get('pedidos', []),
            "total": sum(p.get('precio', 0) * p.get('cantidad', 1) for p in cliente.get('pedidos', [])),
            "notificaciones": mesa.get('notificaciones', []),
            "comentarios_camarero": mesa.get('comentarios_camarero', [])
        }

        historial_dir = os.path.join("data", "historial_pagos")
        os.makedirs(historial_dir, exist_ok=True)
        fecha_archivo = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_historial = os.path.join(historial_dir, f"individual_{cliente['nombre'].replace(' ', '_')}_{fecha_archivo}.json")

        try:
            with open(archivo_historial, 'w', encoding='utf-8') as f:
                json.dump(registro_individual, f, indent=2, ensure_ascii=False)
            print(f"📁 Historial de pago individual guardado para {cliente['nombre']} en: {archivo_historial}")
        except Exception as e:
            print(f"⚠️ Error al guardar el historial de pago individual: {e}")
            return False

        # Limpiar los pedidos del cliente actual
        cliente['pedidos'] = []
        cliente['nombre'] = ''

        # Verificar si quedan otros clientes en la mesa
        quedan_clientes = False
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key].get('nombre'):
                quedan_clientes = True
                break

        # Si no quedan clientes, liberar la mesa
        if not quedan_clientes:
            mesa['estado'] = 'libre'
            # Limpiar cualquier notificación o comentario pendiente
            if 'notificaciones' in mesa:
                del mesa['notificaciones']
            if 'comentarios_camarero' in mesa:
                del mesa['comentarios_camarero']
            print("\n✅ Mesa liberada y lista para nuevos clientes")

        self._guardar_cambios()

        print(f"\n✅ Cuenta individual pagada por {cliente['nombre']} - Total: ${registro_individual['total']}")
        return True

    def mostrar_mapa_mesas(self):
        """Muestra un mapa completo de todas las mesas con su estado"""
        print("\n=== MAPA DEL RESTAURANTE ===")

        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            estado = "🟢 Libre" if mesa['estado'] == 'libre' else "🟠 Ocupada"

            print(f"\n{mesa['nombre']} [{estado}]")

            if mesa['estado'] == 'ocupada':
                self._mostrar_pedidos_mesa(mesa, mostrar_total=False)