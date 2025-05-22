from datetime import datetime
import os
import json
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

class VisualizadorPedidosMozo(BaseVisualizador):
    """Clase para manejar toda la visualización de pedidos para el mozo"""

    def __init__(self, sistema_mesas):
        """Inicializa la clase con el sistema de mesas."""
        super().__init__(sistema_mesas)
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
                    estado = "💬 Pendiente" if not solicitud.get('resuelto', False) else "✅ Realizado"
                    hora_solicitud = f" [Enviado: {solicitud.get('hora', 'No registrada')}]"
                    print(f"  📢 {solicitud.get('mensaje', '')}{hora_solicitud} [{estado}]")
        else:
            print("  (No hay solicitudes pendientes)")

        input("\nPresione Enter para volver al mapa de mesas...")

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

class SistemaPedidosMozos(BaseVisualizador):
    """Sistema de gestión de pedidos para los mozos del restaurante."""

    def __init__(self, sistema_mesas):
        """Inicializa el sistema con dependencias necesarias."""
        super().__init__(sistema_mesas)
        self.notificaciones = ManejadorNotificaciones(sistema_mesas)
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
        self.pagos_pendientes = []
        self.historial_tickets = []
        self._cargar_historial()

    def _cargar_historial(self):
        """Carga el historial de tickets desde el archivo."""
        try:
            if os.path.exists('data/historial_pagos/historial.json'):
                with open('data/historial_pagos/historial.json', 'r') as f:
                    self.historial_tickets = json.load(f)
        except Exception as e:
            print(f"Error al cargar historial de tickets: {str(e)}")
            self.historial_tickets = []

    def _guardar_historial(self):
        """Guarda el historial de tickets en el archivo."""
        try:
            os.makedirs('data/historial_pagos', exist_ok=True)
            with open('data/historial_pagos/historial.json', 'w') as f:
                json.dump(self.historial_tickets, f, indent=4)
        except Exception as e:
            print(f"Error al guardar historial de tickets: {str(e)}")

    def guardar_ticket(self, ticket):
        """Guarda un ticket en formato texto en el directorio de tickets."""
        try:
            # Crear directorio si no existe
            os.makedirs('data/tickets', exist_ok=True)
            
            # Generar nombre de archivo único usando timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            mesa_id = ticket['mesa_id']
            filename = f"ticket_{mesa_id}_{timestamp}.txt"
            
            # Crear el contenido del ticket
            contenido = [
                "=" * 40,
                "           TICKET DE PAGO",
                "=" * 40,
                f"\nMesa: {ticket['mesa_nombre']}",
                f"Fecha: {datetime.strptime(ticket['fecha'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')}",
                "-" * 40,
                "\nClientes:"
            ]
            
            # Agregar clientes
            clientes = set()
            for pedido in ticket['pedidos']:
                clientes.add(pedido['cliente'])
            for cliente in sorted(clientes):
                contenido.append(f"- {cliente}")
            
            # Agregar detalle de pedidos
            contenido.extend([
                "\nDETALLE DE PEDIDOS:",
                "-" * 40
            ])
            
            # Agrupar pedidos por cliente
            pedidos_por_cliente = {}
            for pedido in ticket['pedidos']:
                cliente = pedido['cliente']
                if cliente not in pedidos_por_cliente:
                    pedidos_por_cliente[cliente] = []
                pedidos_por_cliente[cliente].append(pedido)
            
            # Agregar pedidos al ticket
            for cliente, pedidos in pedidos_por_cliente.items():
                for pedido in pedidos:
                    if pedido['cantidad'] > 1:
                        contenido.extend([
                            f"{pedido['cantidad']}x {pedido['nombre']}",
                            f"   Precio unitario: ${pedido['precio']}",
                            f"   Subtotal: ${pedido['subtotal']}\n"
                        ])
                    else:
                        contenido.append(f"{pedido['cantidad']}x {pedido['nombre']} - ${pedido['precio']}\n")
            
            # Agregar total y método de pago
            contenido.extend([
                "-" * 40,
                f"TOTAL A PAGAR: ${ticket['total']}",
                f"Método de pago: {ticket['metodo_pago'].capitalize()}",
                "=" * 40,
                "¡Gracias por su visita!",
                "=" * 40
            ])
            
            # Guardar el ticket
            with open(f'data/tickets/{filename}', 'w', encoding='utf-8') as f:
                f.write('\n'.join(contenido))
            
            # También agregar al historial
            self.historial_tickets.append(ticket)
            self._guardar_historial()
            
            return True
        except Exception as e:
            print(f"Error al guardar ticket: {str(e)}")
            return False

    def confirmar_pago(self, mesa_id, cliente, tipo_pago, metodo_pago, total):
        """Confirma un pago y guarda el ticket."""
        try:
            # Buscar el pago pendiente
            pago_confirmado = None
            for pago in self.pagos_pendientes:
                if pago['mesa_id'] == mesa_id and pago['cliente'] == cliente:
                    pago_confirmado = pago
                    break

            if not pago_confirmado:
                return False, "No se encontró el pago pendiente"

            # Obtener datos de la mesa
            mesa_data = self.sistema_mesas.obtener_mesa(mesa_id)
            if not mesa_data:
                return False, "Mesa no encontrada"

            mesa = mesa_data[0]

            # Crear el ticket
            ticket = {
                'mesa_id': mesa_id,
                'mesa_nombre': mesa['nombre'],
                'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'tipo_pago': tipo_pago,
                'metodo_pago': metodo_pago,
                'total': total,
                'cliente': cliente,
                'pedidos': []
            }

            # Agregar los pedidos al ticket
            for i in range(1, mesa.get('capacidad', 0) + 1):
                cliente_key = f"cliente_{i}"
                cliente_data = mesa.get(cliente_key)
                if cliente_data and cliente_data.get('nombre'):
                    # Si es pago individual, solo incluir pedidos del cliente específico
                    if tipo_pago == 'individual' and cliente_data['nombre'] != cliente:
                        continue
                        
                    for pedido in cliente_data.get('pedidos', []):
                        if pedido.get('entregado'):
                            ticket['pedidos'].append({
                                'cliente': cliente_data['nombre'],
                                'nombre': pedido['nombre'],
                                'cantidad': pedido['cantidad'],
                                'precio': pedido['precio'],
                                'subtotal': pedido['precio'] * pedido['cantidad']
                            })

            # Guardar el ticket
            if not self.guardar_ticket(ticket):
                return False, "Error al guardar el ticket"

            # Eliminar el pago de la lista de pendientes
            self.pagos_pendientes = [
                p for p in self.pagos_pendientes 
                if not (p['mesa_id'] == mesa_id and p['cliente'] == cliente)
            ]

            # Limpiar la mesa según el tipo de pago
            if tipo_pago == 'individual':
                # Limpiar solo el cliente específico
                for i in range(1, mesa.get('capacidad', 0) + 1):
                    cliente_key = f"cliente_{i}"
                    cliente_data = mesa.get(cliente_key)
                    if cliente_data and cliente_data.get('nombre') == cliente:
                        # Limpiar pedidos del cliente
                        mesa[cliente_key] = {
                            'nombre': '',
                            'pedidos': [],
                            'contador_pedidos': 0
                        }
                        break
            else:
                # Limpiar toda la mesa
                mesa['estado'] = 'libre'
                mesa['comentarios_camarero'] = []
                mesa['notificaciones'] = []
                
                # Limpiar todos los clientes
                for i in range(1, mesa.get('capacidad', 0) + 1):
                    cliente_key = f"cliente_{i}"
                    mesa[cliente_key] = {
                        'nombre': '',
                        'pedidos': [],
                        'contador_pedidos': 0
                    }

            # Asegurar que todos los clientes tengan el contador_pedidos
            for i in range(1, mesa.get('capacidad', 0) + 1):
                cliente_key = f"cliente_{i}"
                if 'contador_pedidos' not in mesa[cliente_key]:
                    mesa[cliente_key]['contador_pedidos'] = 0

            # Guardar los cambios en las mesas
            self.sistema_mesas.guardar_mesas()

            return True, "Pago confirmado exitosamente"

        except Exception as e:
            print(f"Error al confirmar pago: {str(e)}")
            return False, str(e)

    def mostrar_pedidos_pendientes(self):
        """Muestra los pedidos pendientes de entrega."""
        pedidos_pendientes = []
        
        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            if mesa['estado'] == 'ocupada':
                pedidos = self.procesar_pedidos_mesa(mesa_id)
                pedidos_pendientes.extend([p for p in pedidos if p.get('estado_cocina') == self.estados_pedido['listo']])
        
        return pedidos_pendientes

    def marcar_pedido_entregado(self, mesa_id, pedido_id):
        """Marca un pedido como entregado."""
        try:
            mesa_data = self._validar_mesa(mesa_id)
            if not mesa_data:
                print(f"⚠️ Error: Mesa {mesa_id} no encontrada")
                return False

            mesa = mesa_data[0]
            pedido_encontrado = False
            
            for i in range(1, mesa.get('capacidad', 0) + 1):
                cliente_key = f"cliente_{i}"
                cliente = mesa.get(cliente_key)
                if cliente and cliente.get('nombre'):
                    for pedido in cliente.get('pedidos', []):
                        if pedido.get('id') == pedido_id:
                            if pedido.get('entregado', False):
                                print(f"⚠️ Error: El pedido {pedido_id} ya está marcado como entregado")
                                return False
                            pedido['entregado'] = True
                            pedido['hora_entrega'] = datetime.now().strftime("%H:%M hs")
                            pedido_encontrado = True
                            break
                    if pedido_encontrado:
                        break
            
            if not pedido_encontrado:
                print(f"⚠️ Error: Pedido {pedido_id} no encontrado en la mesa {mesa_id}")
                return False
                
            try:
                self.sistema_mesas.guardar_mesas()
                return True
            except Exception as e:
                print(f"⚠️ Error al guardar mesas: {e}")
                return False
                
        except Exception as e:
            print(f"⚠️ Error inesperado al marcar pedido como entregado: {e}")
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

    def mostrar_mapa_mesas(self):
        """Muestra el mapa de mesas con clientes, pedidos y comentarios."""
        self.mostrar_mapa_mesas()

    def gestionar_comentarios(self):
        """Permite al mozo ver y marcar comentarios como realizados."""
        while True:
            comentarios_pendientes = self._obtener_comentarios_pendientes()
            if not comentarios_pendientes:
                print("\nℹ️ No hay comentarios pendientes.")
                input("Presione Enter para volver al menú...")
                return

            print("\n--- COMENTARIOS PENDIENTES ---")
            for i, comentario_info in enumerate(comentarios_pendientes, 1):
                estado = "💬 Pendiente"
                hora_envio = f" [Enviado: {comentario_info.get('hora', 'No registrada')}]"
                print(f"{i}. {comentario_info['mesa_nombre']}, 👤 Cliente: {comentario_info['cliente']}, 📝 Comentario: {comentario_info['texto']}{hora_envio} [{estado}]")
            print("\n0. Volver al menú principal")

            opcion = input("Seleccione un comentario para marcar como realizado ✅ (número) o 0 para volver: ")
            if opcion == '0':
                return
            try:
                indice = int(opcion) - 1
                if 0 <= indice < len(comentarios_pendientes):
                    comentario = comentarios_pendientes[indice]
                    print("\n¿Está seguro que desea marcar este comentario como realizado?")
                    print("1. Sí, marcar como realizado")
                    print("2. No, cancelar")
                    confirmacion = input("\nSeleccione una opción: ")
                    if confirmacion == "1":
                        if self._marcar_comentario_realizado(comentario['mesa_id'], comentario['cliente'], comentario['texto']):
                            print("✅ Comentario marcado como realizado.")
                        else:
                            print("⚠️ Error al marcar el comentario como realizado.")
                    elif confirmacion == "2":
                        print("❌ Operación cancelada.")
                    else:
                        print("⚠️ Opción inválida.")
                else:
                    print("Número de comentario inválido.")
            except ValueError:
                print("Por favor, ingrese un número válido.")

    def _obtener_comentarios_pendientes(self):
        """Obtiene todos los comentarios pendientes de todas las mesas."""
        comentarios_pendientes = []
        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            if 'comentarios_camarero' in mesa:
                for comentario in mesa['comentarios_camarero']:
                    if not comentario.get('resuelto', False):
                        comentarios_pendientes.append({
                            'mesa_id': mesa_id,
                            'mesa_nombre': mesa['nombre'],
                            'cliente': comentario['cliente'],
                            'texto': comentario['mensaje'],
                            'hora': comentario.get('hora', 'No registrada')
                        })
        return comentarios_pendientes

    def _marcar_comentario_realizado(self, mesa_id, cliente_nombre, comentario_texto):
        """Marca un comentario específico como realizado."""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return False

        mesa = mesa_data[0]
        if 'comentarios_camarero' in mesa:
            for comentario in mesa['comentarios_camarero']:
                if comentario['cliente'] == cliente_nombre and comentario['mensaje'] == comentario_texto and not comentario.get('resuelto', False):
                    comentario['resuelto'] = True
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
                print("\nℹ️ No hay pedidos listos para entregar.")
                input("Presione Enter para volver al menú...")
                return

            print("\n--- PEDIDOS LISTOS PARA ENTREGAR ---")
            for i, pedido_info in enumerate(pedidos_listos, 1):
                print(f"{i}. {pedido_info['mesa_nombre']}, 👤: {pedido_info['cliente']}, Pedido: {pedido_info['nombre']}")
            print("\n0. Volver al menú principal")

            opcion = input("📋 Seleccione un pedido para marcar como entregado (número) o 0 para volver: ")
            if opcion == '0':
                return
            try:
                indice = int(opcion) - 1
                if 0 <= indice < len(pedidos_listos):
                    pedido = pedidos_listos[indice]
                    print(f"\n⚠️ ¿Está seguro que desea marcar como entregado el pedido '{pedido['nombre']}'?")
                    print("1. Sí, marcar como entregado")
                    print("2. No, volver")
                    confirmacion = input("\nSeleccione una opción: ")
                    if confirmacion == "1":
                        if self.marcar_pedido_entregado(pedido['mesa_id'], pedido['id']):
                            print(f"\n✅ Pedido '{pedido['nombre']}' marcado como entregado.")
                        else:
                            print("Error al marcar el pedido como entregado.")
                    else:
                        print("\n❌ Operación cancelada")
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

    def reiniciar_mesa(self, mesa_id):
        """Reinicia una mesa específica, registrando el evento en el historial."""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return False

        mesa = mesa_data[0]
        
        # Registrar en el historial
        historial_dir = "data/historial_pagos"
        if not os.path.exists(historial_dir):
            os.makedirs(historial_dir)

        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        archivo_historial = os.path.join(historial_dir, f"pagos_{fecha_actual}.json")
        
        registro = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mesa": mesa['nombre'],
            "total": 0,
            "tipo": "reinicio",
            "detalle": "Mesa reiniciada por el camarero"
        }

        try:
            if os.path.exists(archivo_historial):
                with open(archivo_historial, 'r', encoding='utf-8') as f:
                    historial = json.load(f)
            else:
                historial = []

            historial.append(registro)

            with open(archivo_historial, 'w', encoding='utf-8') as f:
                json.dump(historial, f, indent=4, ensure_ascii=False)

            # Limpiar la mesa
            for i in range(1, mesa.get('capacidad', 0) + 1):
                cliente_key = f"cliente_{i}"
                if cliente_key in mesa:
                    mesa[cliente_key] = {'nombre': '', 'pedidos': []}
            
            # Cambiar el estado de la mesa a 'libre'
            mesa['estado'] = 'libre'
            
            self.sistema_mesas.guardar_mesas()
            print(f"\n✅ Mesa {mesa['nombre']} reiniciada exitosamente")
            return True
        except Exception as e:
            print(f"\n⚠️ Error al reiniciar la mesa: {e}")
            return False

    def mostrar_menu(self):
        """Muestra el menú principal del sistema de mozos."""
        while True:
            print("\n--- SISTEMA DE MOZOS ---")
            print("1. Mostrar mapa de mesas")
            print("2. Gestionar comentarios pendientes")
            print("3. Gestionar entregas de pedidos")
            print("4. Reiniciar mesa")
            print("0. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                self.mostrar_mapa_mesas()
                input("Presione Enter para volver al menú...")
            elif opcion == '2':
                self.gestionar_comentarios()
            elif opcion == '3':
                self.gestionar_entregas()
            elif opcion == '4':
                self.mostrar_mapa_mesas()
                mesa_id = input("\nIngrese el ID de la mesa a reiniciar (o 0 para volver): ")
                if mesa_id != '0':
                    self.reiniciar_mesa(mesa_id)
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