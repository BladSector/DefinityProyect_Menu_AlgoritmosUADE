from datetime import datetime
import os
import json
from sistema_pedidos_cocina import SistemaPedidosCocina

HISTORIAL_DIR = os.path.join("data", "historial_pagos")

class SistemaPedidosClientes:
    def __init__(self, sistema_mesas):
        self.sistema_mesas = sistema_mesas
        self.cliente_actual = None # Para rastrear el cliente actual en pagos individuales
        self.historial_dir = HISTORIAL_DIR
        if not os.path.exists(self.historial_dir):
            os.makedirs(self.historial_dir)

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

        # Generar un ID único para el pedido usando timestamp y un contador por cliente
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        if 'contador_pedidos' not in cliente:
            cliente['contador_pedidos'] = 0
        cliente['contador_pedidos'] += 1
        pedido_id = f"{timestamp}_{cliente['contador_pedidos']}"
        self._guardar_cambios()  # Guardar el incremento del contador

        while True:
            print("\n--- HACER PEDIDO ---")
            print("1. Ver menú completo y seleccionar")
            print("2. Filtrar por categoría")
            print("3. Filtrar por dieta")
            print("4. Cancelar pedido")
            print("0. Volver al menú principal")

            try:
                opcion_menu = int(input("Seleccione una opción: "))

                if opcion_menu == 0:
                    break
                elif opcion_menu == 4:
                    self._cancelar_pedido_pendiente(mesa_id)
                    continue
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
                        'id': pedido_id,  # ID único del pedido
                        'plato_id': plato['id'],  # ID del plato en el menú
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
                    break  # Salir del bucle después de agregar un pedido

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
                if p.get('estado_cocina') not in ['🔴 CANCELADO']
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

        # Crear instancia temporal de SistemaPedidosCocina para acceder a los estados
        sistema_cocina = SistemaPedidosCocina(self.sistema_mesas)

        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    if not pedido.get('en_cocina', False):
                        tiene_pedidos_nuevos = True
                        pedido['en_cocina'] = True
                        pedido['hora_envio'] = datetime.now().strftime("%H:%M hs")
                        # Establecer estado inicial del pedido usando el valor correcto
                        pedido['estado_cocina'] = sistema_cocina.estados_pedido['pendiente']
                        
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
            pedidos_activos = [p for p in cliente['pedidos'] if not p.get('entregado', False)]
            
            if not pedidos_activos:
                print("\n⚠️ No tienes pedidos activos para agregar notas")
                input("\nPresione Enter para volver al menú anterior...")
                return

            for i, pedido in enumerate(pedidos_activos, 1):
                nombre_pedido = pedido.get('nombre', 'Desconocido')
                cantidad = pedido.get('cantidad', 1)
                precio = pedido.get('precio', 0)
                estado = pedido.get('estado_cocina', '🟡 Pendiente')
                print(f"{i}. {nombre_pedido} - {cantidad}x (${precio * cantidad}) [{estado}]")

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
                if 1 <= opcion <= len(pedidos_activos):
                    pedido = pedidos_activos[opcion - 1]

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

    def _guardar_historial_pago(self, mesa_id, cliente, total, metodo_pago):
        """Guarda el historial del pago en un archivo JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_historial = os.path.join(self.historial_dir, f"pago_{mesa_id}_{timestamp}.json")
        
        historial = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M hs"),
            "mesa_id": mesa_id,
            "cliente": cliente.get('nombre', ''),
            "pedidos": cliente.get('pedidos', []),
            "total": total,
            "metodo_pago": metodo_pago
        }
        
        with open(archivo_historial, 'w', encoding='utf-8') as f:
            json.dump(historial, f, ensure_ascii=False, indent=4)

    def _guardar_ticket(self, mesa_id, mesa, platos_agrupados, total, metodo_pago, es_grupal):
        """Guarda el ticket de pago en un archivo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_ticket = os.path.join(self.historial_dir, "tickets", f"ticket_{mesa_id}_{timestamp}.txt")
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(archivo_ticket), exist_ok=True)
        
        with open(archivo_ticket, 'w', encoding='utf-8') as f:
            f.write("=" * 40 + "\n")
            f.write("           TICKET DE PAGO\n")
            f.write("=" * 40 + "\n\n")
            
            # Información de la mesa
            f.write(f"Mesa: {mesa['nombre']}\n")
            f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write("-" * 40 + "\n\n")
            
            # Información de los clientes
            f.write("Clientes:\n")
            for i in range(1, mesa.get('capacidad', 0) + 1):
                cliente_key = f"cliente_{i}"
                cliente = mesa.get(cliente_key)
                if cliente and cliente.get('nombre'):
                    f.write(f"- {cliente['nombre']}\n")
            f.write("\n")
            
            # Detalle de pedidos
            f.write("DETALLE DE PEDIDOS:\n")
            f.write("-" * 40 + "\n")
            for nombre, datos in platos_agrupados.items():
                if datos['cantidad'] > 1:
                    f.write(f"{datos['cantidad']}x {nombre}\n")
                    f.write(f"   Precio unitario: ${datos['precio_unitario']}\n")
                    f.write(f"   Subtotal: ${datos['subtotal']}\n")
                else:
                    f.write(f"1x {nombre} - ${datos['precio_unitario']}\n")
                f.write("\n")
            
            f.write("-" * 40 + "\n")
            f.write(f"TOTAL A PAGAR: ${total}\n")
            f.write(f"Método de pago: {metodo_pago}\n")
            f.write("=" * 40 + "\n")
            f.write("¡Gracias por su visita!\n")
            f.write("=" * 40 + "\n")

    def _verificar_todos_pagaron(self, mesa):
        """Verifica si todos los clientes han pagado sus pedidos."""
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre') and cliente.get('pedidos'):
                return False
        return True

    def _contar_clientes_activos(self, mesa):
        """Cuenta cuántos clientes activos hay en la mesa."""
        contador = 0
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                contador += 1
        return contador

    def pagar_cuenta(self, mesa_id, cliente_key):
        """Permite al cliente pagar su cuenta."""
        mesa = self._obtener_mesa(mesa_id)
        if not mesa:
            print(f"\n⚠️ Error: Mesa {mesa_id} no encontrada.")
            return False

        cliente = mesa.get(cliente_key)
        if not cliente:
            print(f"\n⚠️ Error: Cliente {cliente_key} no encontrado en la mesa {mesa_id}.")
            return False

        pedidos_cliente = cliente.get('pedidos', [])
        
        # Filtrar pedidos no cancelados (ni por cliente ni por cocina)
        pedidos_activos = [p for p in pedidos_cliente if p.get('estado_cocina') not in ['🔴 CANCELADO']]
        
        if not pedidos_activos:
            print("\n⚠️ No hay pedidos activos para pagar.")
            return False

        # Verificar si hay pedidos pendientes (solo entre los no cancelados)
        pedidos_pendientes = [p for p in pedidos_activos if not p.get('entregado') and p.get('estado_cocina') != '🔴 CANCELADO']
        if pedidos_pendientes:
            print("\n⚠️ No se puede pagar aún. Todos los pedidos deben estar marcados como 'entregado' en mesa.")
            return False

        # Verificar si hay más de un cliente en la mesa
        num_clientes = self._contar_clientes_activos(mesa)
        tipo_pago = "1"  # Por defecto, pago individual

        if num_clientes > 1:
            # Preguntar si es pago grupal o individual
            print("\n¿Cómo desea realizar el pago?")
            print("1. Pago individual")
            print("2. Pago grupal")
            print("0. Volver")
            
            tipo_pago = input("\nSeleccione el tipo de pago: ")
            
            if tipo_pago == "0":
                return False
            elif tipo_pago not in ["1", "2"]:
                print("\n⚠️ Opción inválida")
                return False

        # Si es pago grupal, mostrar el resumen de todos los clientes
        if tipo_pago == "2":
            print("\n=== RESUMEN GRUPAL ===")
            
            # Agrupar platos repetidos y calcular totales para pago grupal
            platos_agrupados = {}
            total = 0
            
            # Recolectar todos los pedidos de todos los clientes
            for i in range(1, mesa.get('capacidad', 0) + 1):
                cliente_key = f"cliente_{i}"
                cliente_actual = mesa.get(cliente_key)
                if cliente_actual and cliente_actual.get('nombre'):
                    for pedido in cliente_actual.get('pedidos', []):
                        if pedido.get('estado_cocina') not in ['🔴 CANCELADO']:
                            nombre = pedido.get('nombre', 'Desconocido')
                            precio = pedido.get('precio', 0)
                            cantidad = pedido.get('cantidad', 1)
                            
                            if nombre not in platos_agrupados:
                                platos_agrupados[nombre] = {
                                    'cantidad': 0,
                                    'precio_unitario': precio,
                                    'subtotal': 0
                                }
                            
                            platos_agrupados[nombre]['cantidad'] += cantidad
                            platos_agrupados[nombre]['subtotal'] += precio * cantidad
                            total += precio * cantidad

            # Mostrar el detalle de la cuenta grupal
            print("\n=== DETALLE DE LA CUENTA GRUPAL ===")
            for nombre, datos in platos_agrupados.items():
                if datos['cantidad'] > 1:
                    print(f"{datos['cantidad']}x {nombre}")
                    print(f"   Precio unitario: ${datos['precio_unitario']}")
                    print(f"   Subtotal: ${datos['subtotal']}")
                else:
                    print(f"1x {nombre} - ${datos['precio_unitario']}")
                print()

            print(f"\n💵 TOTAL A PAGAR: ${total}")
            
            print("\n¿Desea continuar con el pago grupal?")
            print("1. Sí, continuar")
            print("2. No, volver")
            confirmacion = input("\nSeleccione una opción: ")
            if confirmacion != "1":
                return False
        else:
            # Agrupar platos repetidos y calcular totales para pago individual
            platos_agrupados = {}
            total = 0
            for pedido in pedidos_activos:
                nombre = pedido.get('nombre', 'Desconocido')
                precio = pedido.get('precio', 0)
                cantidad = pedido.get('cantidad', 1)
                
                if nombre not in platos_agrupados:
                    platos_agrupados[nombre] = {
                        'cantidad': 0,
                        'precio_unitario': precio,
                        'subtotal': 0
                    }
                
                platos_agrupados[nombre]['cantidad'] += cantidad
                platos_agrupados[nombre]['subtotal'] += precio * cantidad
                total += precio * cantidad

            # Mostrar el detalle de la cuenta individual
            print("\n=== DETALLE DE LA CUENTA INDIVIDUAL ===")
            for nombre, datos in platos_agrupados.items():
                if datos['cantidad'] > 1:
                    print(f"{datos['cantidad']}x {nombre}")
                    print(f"   Precio unitario: ${datos['precio_unitario']}")
                    print(f"   Subtotal: ${datos['subtotal']}")
                else:
                    print(f"1x {nombre} - ${datos['precio_unitario']}")
                print()

            print(f"\n💵 TOTAL A PAGAR: ${total}")

        # Simular proceso de pago
        print("\n1. Pagar con efectivo")
        print("2. Pagar con tarjeta")
        print("0. Volver")
        
        opcion = input("\nSeleccione el método de pago: ")
        if opcion in ["1", "2"]:
            metodo_pago = "Efectivo" if opcion == "1" else "Tarjeta"
            print("\n✅ Pago procesado exitosamente")
            
            # Guardar historial del pago y crear ticket
            self._guardar_historial_pago(mesa_id, cliente, total, metodo_pago)
            self._guardar_ticket(mesa_id, mesa, platos_agrupados, total, metodo_pago, tipo_pago == "2")
            
            # Limpiar solo los pedidos del cliente actual
            cliente['pedidos'] = []
            
            # Si es pago grupal o todos los clientes han pagado, limpiar la mesa
            if tipo_pago == "2" or self._verificar_todos_pagaron(mesa):
                mesa['estado'] = 'libre'
                for i in range(1, mesa.get('capacidad', 0) + 1):
                    cliente_key = f"cliente_{i}"
                    if cliente_key in mesa:
                        mesa[cliente_key] = {'nombre': '', 'pedidos': []}
                print("\n👋 ¡Gracias por su visita! La mesa ha sido liberada.")
            else:
                print("\n👋 ¡Gracias por su pago! La mesa permanecerá ocupada hasta que todos los clientes paguen.")
            
            self._guardar_cambios()
            return True
        elif opcion == "0":
            return False
        else:
            print("\n⚠️ Opción inválida")
            return False

    def mostrar_mapa_mesas(self):
        """Muestra un mapa completo de todas las mesas con su estado"""
        print("\n=== MAPA DEL RESTAURANTE ===")

        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            estado = "🟢 Libre" if mesa['estado'] == 'libre' else "🟠 Ocupada"

            print(f"\n{mesa['nombre']} [{estado}]")

            if mesa['estado'] == 'ocupada':
                self._mostrar_pedidos_mesa(mesa, mostrar_total=False)

    def _cancelar_pedido_pendiente(self, mesa_id):
        """Permite al cliente cancelar un pedido que aún no ha sido enviado a cocina"""
        mesa = self._obtener_mesa(mesa_id)
        if not mesa:
            print(f"\n⚠️ Error: Mesa {mesa_id} no encontrada.")
            return

        pedidos_pendientes = []
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    if not pedido.get('en_cocina', False):
                        pedidos_pendientes.append((cliente['nombre'], pedido))

        if not pedidos_pendientes:
            print("\n⚠️ No hay pedidos pendientes para cancelar.")
            return

        print("\n=== Pedidos Pendientes ===")
        for idx, (cliente_nombre, pedido) in enumerate(pedidos_pendientes, 1):
            print(f"\n{idx}. {cliente_nombre}:")
            print(f"   - {pedido.get('cantidad', 1)}x {pedido.get('nombre', 'Desconocido')}")
            if pedido.get('notas'):
                print("   📝 Notas:")
                for nota in pedido['notas']:
                    print(f"     • {nota}")

        print("\n0. Volver")
        opcion = input("\nSeleccione el pedido a cancelar (0 para volver): ")

        if opcion == "0":
            return

        try:
            idx = int(opcion) - 1
            if 0 <= idx < len(pedidos_pendientes):
                cliente_nombre, pedido = pedidos_pendientes[idx]
                print(f"\n⚠️ ¿Está seguro que desea cancelar el pedido de {cliente_nombre}?")
                print("1. Sí, cancelar")
                print("2. No, volver")
                confirmacion = input("\nSeleccione una opción: ")
                if confirmacion == "1":
                    # Encontrar y eliminar el pedido
                    for i in range(1, mesa.get('capacidad', 0) + 1):
                        cliente_key = f"cliente_{i}"
                        cliente = mesa.get(cliente_key)
                        if cliente and cliente.get('nombre') == cliente_nombre:
                            cliente['pedidos'].remove(pedido)
                            self._guardar_cambios()
                            print("\n✅ Pedido cancelado exitosamente")
                            return
                else:
                    print("\n❌ Cancelación abortada")
            else:
                print("\n⚠️ Opción inválida")
        except ValueError:
            print("\n⚠️ Por favor ingrese un número válido")