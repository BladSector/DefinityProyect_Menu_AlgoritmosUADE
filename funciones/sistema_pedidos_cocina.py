import json
from datetime import datetime

class SistemaPedidosCocina:
    def mostrar_mapa_mesas(self):
        """Muestra un mapa completo de todas las mesas con su estado"""
        print("\n--- MAPA DEL RESTAURANTE ---")
        
        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            estado = "🟢 Libre" if mesa['estado'] == 'libre' else "🟠 Ocupada"
            
            print(f"\n{mesa['nombre']} [{estado}]")
            
            if mesa['estado'] == 'ocupada':
                # Mostrar clientes y pedidos
                for i in range(1, mesa['capacidad'] + 1):
                    cliente_key = f"cliente_{i}"
                    if mesa[cliente_key]['nombre']:
                        print(f"\n👤 {mesa[cliente_key]['nombre']}:")
                        for pedido in mesa[cliente_key]['pedidos']:
                            nota = f" (Nota: {pedido['nota']})" if 'nota' in pedido else ""
                            entregado = " (✅ Entregado)" if pedido.get('entregado') else ""
                            print(f"  - {pedido['cantidad']}x {pedido['nombre']}{nota}{entregado}")
        input("\nPresione Enter para continuar...")
        
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
    
    def procesar_pedidos_mesa(self, mesa_id):
        """Organiza los pedidos por lógica culinaria (excluyendo bebidas)"""
        mesa = self.sistema_mesas.mesas[mesa_id][0]
        pedidos_agrupados = {
            'entradas': [],
            'principales': [],
            'postres': []
        }
        
        # Agrupar pedidos por etapa
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre']:
                for pedido in mesa[cliente_key]['pedidos']:
                    # Solo procesar pedidos enviados a cocina pero no entregados
                    if not pedido.get('en_cocina', False) or pedido.get('entregado', False):
                        continue
                    
                    # Buscar el plato en el menú (versión corregida)
                    plato = None
                    for etapa in self.sistema_mesas.menu['platos'].values():
                        for categoria in etapa.values():
                            for item in categoria:
                                if item['id'] == pedido['id']:
                                    plato = item
                                    break
                            if plato: break
                        if plato: break
                    
                    if not plato:
                        continue
                    
                    # Determinar etapa del plato (versión mejorada)
                    etapa_plato = plato.get('etapa', '').lower()
                    if any(b in etapa_plato for b in ['bebida', 'bebidas', 'drink']):
                        continue
                    
                    # Clasificación mejorada de etapas
                    if any(e in etapa_plato for e in ['entrada', 'starter', 'appetizer']):
                        grupo = 'entradas'
                    elif any(m in etapa_plato for m in ['principal', 'main', 'plato principal']):
                        grupo = 'principales'
                    elif any(p in etapa_plato for p in ['postre', 'dessert', 'dulce']):
                        grupo = 'postres'
                    else:
                        continue  # Si no coincide con ninguna etapa conocida
                    
                    # Crear copia del pedido con información adicional
                    pedido_procesado = {
                        'id': pedido['id'],
                        'nombre': pedido['nombre'],
                        'cantidad': pedido['cantidad'],
                        'cliente': mesa[cliente_key]['nombre'],
                        'mesa_id': mesa_id,
                        'mesa_nombre': mesa['nombre'],
                        'hora_envio': pedido.get('hora_envio', 'reciente'),
                        'notas': pedido.get('notas', []),
                        'estado_cocina': pedido.get('estado_cocina', self.estados_pedido['normal'])
                    }
                    pedidos_agrupados[grupo].append(pedido_procesado)
        
        # Ordenar por prioridad (urgentes primero)
        pedidos_ordenados = []
        for etapa in ['entradas', 'principales', 'postres']:
            if pedidos_agrupados[etapa]:
                pedidos_etapa = sorted(
                    pedidos_agrupados[etapa],
                    key=lambda x: (
                        0 if x['estado_cocina'] == self.estados_pedido['preparar'] else
                        1 if x['estado_cocina'] == self.estados_pedido['normal'] else 2
                    )
                )
                pedidos_ordenados.extend(pedidos_etapa)
        
        return pedidos_ordenados

    def mostrar_pedidos_activos(self):
        """Muestra todos los pedidos activos en cocina"""
        print("\n=== PEDIDOS ACTIVOS EN COCINA ===")
        
        todos_pedidos = []
        for mesa_id in self.sistema_mesas.mesas:
            pedidos_mesa = self.procesar_pedidos_mesa(mesa_id)
            if pedidos_mesa:
                print(f"\nMesa {mesa_id}: {self.sistema_mesas.mesas[mesa_id][0]['nombre']}")
                for i, pedido in enumerate(pedidos_mesa, 1):
                    estado = pedido.get('estado_cocina', '🟡 PENDIENTE')
                    print(f"{i}. {estado} - {pedido['cliente']}")
                    print(f"   {pedido['cantidad']}x {pedido['nombre']}")
                    print(f"   Enviado a cocina: {pedido['hora_envio']}")
                    
                    # Mostrar notas si existen
                    if pedido.get('notas'):
                        print("   📝 Notas:")
                        for nota in pedido['notas']:
                            print(f"      - {nota['texto']} ({nota['hora']})")
                    
                    todos_pedidos.append(pedido)
        
        if not todos_pedidos:
            print("\nNo hay pedidos activos en cocina")
            input("\nPresione Enter para continuar...")
            return
        
        # Opción para gestionar pedidos
        try:
            print("\nSeleccione:")
            print("1. Gestionar un pedido")
            print("0. Volver")
            
            opcion = int(input("\nOpción: "))
            if opcion == 1:
                mesa_id = input("Ingrese ID de mesa: ")
                num_pedido = int(input("Número de pedido: ")) - 1
                
                # Buscar el pedido seleccionado
                pedido_seleccionado = None
                for pedido in todos_pedidos:
                    if pedido['mesa_id'] == mesa_id and todos_pedidos.index(pedido) == num_pedido:
                        pedido_seleccionado = pedido
                        break
                
                if pedido_seleccionado:
                    self.gestionar_pedido(mesa_id, pedido_seleccionado)
        except (ValueError, IndexError):
            print("Opción inválida")

    def gestionar_pedido(self, mesa_id, pedido):
        """Menú de gestión para un pedido específico"""
        while True:
            print(f"\n--- GESTIÓN DE PEDIDO ---")
            print(f"Mesa: {pedido['mesa_nombre']}")
            print(f"Cliente: {pedido['cliente']}")
            print(f"Pedido: {pedido['cantidad']}x {pedido['nombre']}")
            print(f"Estado actual: {pedido.get('estado_cocina', 'Pendiente')}")
            
            print("\nOpciones:")
            print("1. Marcar como en preparación")
            print("2. Marcar como listo para entregar")
            print("3. Agregar nota")
            print("0. Volver")
            
            try:
                opcion = int(input("\nSelección: "))
                
                if opcion == 0:
                    break
                elif opcion == 1:
                    self.marcar_en_preparacion(mesa_id, pedido)
                elif opcion == 2:
                    self.marcar_listo_entrega(mesa_id, pedido)
                elif opcion == 3:
                    nota = input("Ingrese nota: ")
                    if nota:
                        if 'notas' not in pedido:
                            pedido['notas'] = []
                        pedido['notas'].append({
                            'texto': nota,
                            'hora': datetime.now().strftime("%H:%M hs")
                        })
                        self.sistema_mesas.guardar_mesas()
                        print("✅ Nota agregada")
            except ValueError:
                print("Opción inválida")

    def determinar_estado_pedido(self, pedido):
        """Determina el estado de prioridad del pedido"""
        # Buscar el plato en la estructura del menú
        plato = None
        for etapa in self.sistema_mesas.menu['platos'].values():
            for categoria in etapa.values():
                for item in categoria:
                    if item['id'] == pedido['id']:
                        plato = item
                        break
                if plato:
                    break
            if plato:
                break
        
        if not plato:
            print(f"Advertencia: No se encontró el plato con ID {pedido['id']}")
            return self.estados_pedido['normal']
        
        try:
            if pedido.get('estado_cocina'):
                return pedido['estado_cocina']
            if 'urgente' in pedido.get('nota', '').lower():
                return self.estados_pedido['preparar']
            if 'niño' in pedido.get('nota', '').lower():
                return self.estados_pedido['preparar']
            if any(d in ['vegano', 'sin gluten'] for d in plato.get('dietas', [])):
                return self.estados_pedido['preparar']
            
            return self.estados_pedido['normal']
        except KeyError as e:
            print(f"Advertencia: Falta campo requerido: {e}")
            return self.estados_pedido['normal']
    
    def mostrar_pedidos_activos(self):
        """Muestra todos los pedidos activos con opciones de gestión"""
        while True:
            print("\n--- PEDIDOS ACTIVOS EN COCINA ---")
            mesas_activas = {}
            
            # Recolectar mesas con pedidos activos (excluyendo bebidas)
            for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
                mesa = mesa_data[0]
                if mesa['estado'] == 'ocupada':
                    pedidos = self.procesar_pedidos_mesa(mesa_id)
                    if pedidos:
                        mesas_activas[mesa_id] = {
                            'nombre': mesa['nombre'],
                            'pedidos': pedidos,
                            'comentarios': mesa.get('comentarios_camarero', [])
                        }

            if not mesas_activas:
                print("No hay pedidos activos en cocina")
                input("\nPresione Enter para volver...")
                return

            # Mostrar lista numerada de mesas
            print("\nMesas con pedidos activos:")
            for i, mesa_id in enumerate(mesas_activas.keys(), 1):
                print(f"{i}. {mesas_activas[mesa_id]['nombre']}")

            print("\n0. Volver al menú principal")
            
            try:
                opcion_mesa = int(input("\nSeleccione una mesa (número): "))
                if opcion_mesa == 0:
                    return
                    
                mesa_id = list(mesas_activas.keys())[opcion_mesa-1]
                mesa_info = mesas_activas[mesa_id]
                
                # Mostrar detalles de la mesa seleccionada
                while True:
                    print(f"\n---{mesa_info['nombre']}---")
                    print("-" * 40)
                    
                    # Mostrar pedidos numerados
                    print("\n🍽️ Pedidos:")
                    for i, pedido in enumerate(mesa_info['pedidos'], 1):
                        estado = pedido.get('estado_cocina', self.determinar_estado_pedido(pedido))
                        nota = f" (Nota: {pedido['nota']})" if 'nota' in pedido else ""
                        print(f"{i}. {estado} - {pedido['cliente']}")
                        print(f"   {pedido['cantidad']}x {pedido['nombre']}{nota}")
                        print(f"   Hora: {pedido['hora']}")
                    
                    # Opciones para el pedido
                    print("\nOpciones:")
                    print("1. Seleccionar pedido para gestión")
                    print("0. Volver a lista de mesas")
                    
                    opcion_accion = input("\nSeleccione una opción: ")
                    
                    if opcion_accion == "0":
                        break
                        
                    elif opcion_accion == "1":
                        try:
                            num_pedido = int(input("Número de pedido a gestionar: ")) - 1
                            if num_pedido < 0 or num_pedido >= len(mesa_info['pedidos']):
                                print("Número de pedido inválido")
                                continue
                                
                            pedido = mesa_info['pedidos'][num_pedido]
                            
                            # Menú de gestión del pedido
                            print(f"\nGestión del pedido: {pedido['nombre']}")
                            print(f"Cliente: {pedido['cliente']}")
                            print(f"Estado actual: {pedido.get('estado_cocina', 'Pendiente')}")
                            
                            print("\n1. Marcar como en preparación")
                            print("2. Marcar como listo para entregar")
                            print("3. Notificar retraso")
                            print("0. Volver")
                            
                            opcion_gestion = input("\nSeleccione acción: ")
                            
                            if opcion_gestion == "1":
                                self.marcar_en_preparacion(mesa_id, pedido)
                            elif opcion_gestion == "2":
                                self.marcar_listo_entrega(mesa_id, pedido)
                            elif opcion_gestion == "3":
                                self.notificar_retraso_interactivo(mesa_id, pedido)
                                
                        except ValueError:
                            print("Por favor ingrese un número válido")
                            
            except (ValueError, IndexError):
                print("Selección inválida")

    def marcar_en_preparacion(self, mesa_id, pedido):
        """Marca un pedido como en preparación y notifica"""
        mesa = self.sistema_mesas.mesas[mesa_id][0]
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre'] == pedido['cliente']:
                for p in mesa[cliente_key]['pedidos']:
                    if p['id'] == pedido['id']:
                        p['estado_cocina'] = self.estados_pedido['en_preparacion']
                        p['hora_preparacion'] = datetime.now().strftime("%H:%M hs")
                        
                        # Notificar
                        mensaje = f"Pedido en preparación: {pedido['nombre']} para {pedido['cliente']}"
                        self.registrar_notificacion(mesa_id, mensaje)
                        
                        self.sistema_mesas.guardar_mesas()
                        print("\n👨‍🍳 Pedido marcado como en preparación")
                        print("Notificación enviada a mozos y clientes")
                        return

    def marcar_listo_entrega(self, mesa_id, pedido):
        """Marca un pedido como listo para entregar y notifica"""
        mesa = self.sistema_mesas.mesas[mesa_id][0]
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre'] == pedido['cliente']:
                for p in mesa[cliente_key]['pedidos']:
                    if p['id'] == pedido['id']:
                        p['estado_cocina'] = self.estados_pedido['listo']
                        p['hora_listo'] = datetime.now().strftime("%H:%M hs")
                        
                        # Notificar
                        mensaje = f"Pedido listo para entregar: {pedido['nombre']} para {pedido['cliente']}"
                        self.registrar_notificacion(mesa_id, mensaje)
                        
                        self.sistema_mesas.guardar_mesas()
                        print("\n✅ Pedido marcado como listo para entregar")
                        print("Notificación enviada a mozos")
                        return

    def notificar_retraso_interactivo(self, mesa_id, pedido):
        """Notifica retraso con opciones predefinidas"""
        print("\nSeleccione tiempo de retraso:")
        print("1. 10 minutos")
        print("2. 20 minutos")
        print("3. 30 minutos")
        print("0. Cancelar")
        
        try:
            opcion = int(input("\nOpción: "))
            minutos = {1: 10, 2: 20, 3: 30}.get(opcion)
            
            if minutos:
                # Actualizar estado del pedido
                mesa = self.sistema_mesas.mesas[mesa_id][0]
                for i in range(1, mesa['capacidad'] + 1):
                    cliente_key = f"cliente_{i}"
                    if mesa[cliente_key]['nombre'] == pedido['cliente']:
                        for p in mesa[cliente_key]['pedidos']:
                            if p['id'] == pedido['id']:
                                p['retraso_minutos'] = minutos
                                
                                # Notificar
                                mensaje = f"Retraso en pedido: {pedido['nombre']} tiene {minutos} min de retraso"
                                self.registrar_notificacion(mesa_id, mensaje)
                                
                                self.sistema_mesas.guardar_mesas()
                                print(f"\n⚠️ Notificación de retraso de {minutos} min enviada")
                                return
        except ValueError:
            print("Opción inválida")

    def registrar_notificacion(self, mesa_id, mensaje):
        """Registra notificación para clientes y mozos"""
        mesa = self.sistema_mesas.mesas[mesa_id][0]
        
        if 'notificaciones' not in mesa:
            mesa['notificaciones'] = []
        
        mesa['notificaciones'].append({
            "mensaje": mensaje,
            "hora": datetime.now().strftime("%H:%M hs"),
            "tipo": "cocina"
        })

    def mostrar_pedidos_urgentes(self):
        """Muestra solo los pedidos marcados como urgentes"""
        print("\n--- PEDIDOS URGENTES ---")
        pedidos_urgentes = []
        
        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            if mesa['estado'] == 'ocupada':
                for i in range(1, mesa['capacidad'] + 1):
                    cliente_key = f"cliente_{i}"
                    if mesa[cliente_key]['nombre']:
                        for pedido in mesa[cliente_key]['pedidos']:
                            # Excluir bebidas
                            plato = next((p for p in self.sistema_mesas.menu['platos'] 
                                        if p['id'] == pedido['id'] and 
                                        p['etapa'].lower() not in ['bebida', 'bebidas']), None)
                            if not plato:
                                continue
                                
                            if ('urgente' in pedido.get('nota', '').lower() or 
                                any(d in ['vegano', 'sin gluten'] for d in plato.get('dietas', []))):
                                pedidos_urgentes.append({
                                    'mesa_id': mesa_id,
                                    'mesa_nombre': mesa['nombre'],
                                    'cliente': mesa[cliente_key]['nombre'],
                                    'pedido': pedido,
                                    'plato': plato
                                })
        
        if not pedidos_urgentes:
            print("No hay pedidos urgentes en este momento")
            input("\nPresione Enter para continuar...")
            return
        
        for i, item in enumerate(pedidos_urgentes, 1):
            nota = f" (Nota: {item['pedido']['nota']})" if 'nota' in item['pedido'] else ""
            print(f"\n{i}. Mesa {item['mesa_id']} - {item['mesa_nombre']}")
            print(f"   Cliente: {item['cliente']}")
            print(f"   🚨 {item['pedido']['cantidad']}x {item['pedido']['nombre']}{nota}")
            print(f"   Tipo: {item['plato']['etapa'].capitalize()}")
            if any(d in ['vegano', 'sin gluten'] for d in item['plato'].get('dietas', [])):
                print(f"   Dietas especiales: {', '.join(item['plato']['dietas'])}")
        
        input("\nPresione Enter para continuar...")