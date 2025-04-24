import json
from datetime import datetime
import os

HISTORIAL_DIR = "historial_pagos"

class SistemaPedidosClientes:
    def __init__(self, sistema_mesas):
        self.sistema_mesas = sistema_mesas
    
    def mostrar_resumen_grupal(self, mesa_id):
        """Muestra el resumen grupal de pedidos con notas múltiples y comentarios al camarero"""
        mesa = self.sistema_mesas.mesas[mesa_id][0]
        
        print("\n=== RESUMEN GRUPAL ===")
        
        # Mostrar pedidos pendientes de enviar
        print("\n--- PEDIDOS POR ENVIAR A COCINA ---")
        hay_pendientes = False
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre'] and mesa[cliente_key]['pedidos']:
                for pedido in mesa[cliente_key]['pedidos']:
                    if not pedido.get('en_cocina', False):
                        hay_pendientes = True
                        print(f"\n👤 {mesa[cliente_key]['nombre']}:")
                        print(f"  - {pedido['cantidad']}x {pedido['nombre']} 🟡 Pendiente")
                        
                        # Mostrar notas (sistema nuevo y antiguo)
                        if 'notas' in pedido and pedido['notas']:
                            print("    📝 Notas:")
                            for nota in pedido['notas']:
                                print(f"      • {nota['texto']} ({nota['hora']})")
                        elif 'nota' in pedido and pedido['nota']:
                            print(f"    📝 Nota: {pedido['nota']} (sistema anterior)")
        
        if not hay_pendientes:
            print("  (No hay pedidos pendientes de enviar)")
        
        # Mostrar pedidos en cocina
        print("\n--- PEDIDOS EN COCINA ---")
        hay_en_cocina = False
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre'] and mesa[cliente_key]['pedidos']:
                for pedido in mesa[cliente_key]['pedidos']:
                    if pedido.get('en_cocina', False):
                        hay_en_cocina = True
                        print(f"\n👤 {mesa[cliente_key]['nombre']}:")
                        hora_envio = pedido.get('hora_envio', 'reciente')
                        print(f"  - {pedido['cantidad']}x {pedido['nombre']} 🟢 En cocina ({hora_envio})")
                        
                        # Mostrar notas (sistema nuevo y antiguo)
                        if 'notas' in pedido and pedido['notas']:
                            print("    📝 Notas:")
                            for nota in pedido['notas']:
                                print(f"      - {nota['texto']} ({nota['hora']})")
                        elif 'nota' in pedido and pedido['nota']:
                            print(f"    📝 Nota: {pedido['nota']} (sistema anterior)")
        
        if not hay_en_cocina:
            print("  (No hay pedidos en cocina aún)")
        
        # Mostrar comentarios al camarero
        print("\n--- SOLICITUDES AL CAMARERO ---")
        if mesa.get('comentarios_camarero'):
            for comentario in mesa['comentarios_camarero']:
                estado = "✅ Resuelto" if comentario['resuelto'] else "🟡 Pendiente"
                print(f"\n{estado} 👤: {comentario['cliente']} - ({comentario['hora']}):")
                print(f"  - {comentario['mensaje']}")
        else:
            print("  (No hay solicitudes al camarero)")
        
        # Mostrar total acumulado
        total = 0
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre']:
                total_cliente = sum(p['precio'] * p['cantidad'] for p in mesa[cliente_key]['pedidos'])
                total += total_cliente
        
        print(f"\n💵 TOTAL ACUMULADO: ${total}")
        
    def confirmar_envio_cocina(self, mesa_id):
        """Confirma el envío del pedido a cocina si hay pedidos nuevos"""
        mesa = self.sistema_mesas.mesas[mesa_id][0]
        tiene_pedidos_nuevos = False
        
        # Verificar si hay pedidos nuevos no enviados
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre']:
                for pedido in mesa[cliente_key]['pedidos']:
                    if not pedido.get('en_cocina', False):
                        tiene_pedidos_nuevos = True
                        pedido['en_cocina'] = True  # Marcar como enviado a cocina
                        pedido['hora_envio'] = datetime.now().strftime("%H:%M hs")
        
        if not tiene_pedidos_nuevos:
            print("\n⚠️ No hay nuevos pedidos para enviar a cocina")
            return
        
        self.sistema_mesas.guardar_mesas()
        print("\n🚀 Pedido enviado a cocina con éxito")
        
    def agregar_nota_pedido(self, mesa_id, cliente_key):
        """Agrega o acumula notas a un pedido seleccionado"""
        mesa = self.sistema_mesas.mesas[mesa_id][0]
        cliente = mesa[cliente_key]

        if not cliente['pedidos']:
            print("\n⚠️ No tienes pedidos registrados")
            return

        while True:
            print("\n=== AGREGAR NOTA A PEDIDO ===")
            print("\n--- TUS PEDIDOS ---")
            for i, pedido in enumerate(cliente['pedidos'], 1):
                print(f"{i}. {pedido['nombre']} - {pedido['cantidad']}x (${pedido['precio'] * pedido['cantidad']})")
                if 'notas' in pedido and pedido['notas']:
                    print("   Historial de notas:")
                    for idx, nota in enumerate(pedido['notas'], 1):
                        print(f"     {idx}. {nota['texto']} ({nota['hora']})")
                elif 'nota' in pedido:  # Compatibilidad con version anterior
                    print(f"   Nota actual: {pedido['nota']} (antigua)")
            
            print("\n0. Volver al menú anterior")
            
            try:
                opcion = input("\nSeleccione el número de pedido: ").strip()
                
                if opcion == "0":
                    print("\nVolviendo al menú anterior...")
                    return
                
                opcion = int(opcion)
                if opcion < 1 or opcion > len(cliente['pedidos']):
                    print("\n⚠️ Error: Número de pedido inválido")
                    continue
                
                pedido = cliente['pedidos'][opcion-1]
                
                # Migrar nota antigua al nuevo sistema si existe
                if 'nota' in pedido and pedido['nota']:
                    if 'notas' not in pedido:
                        pedido['notas'] = []
                    pedido['notas'].append({
                        'texto': pedido['nota'],
                        'hora': datetime.now().strftime("%H:%M hs")
                    })
                    del pedido['nota']
                    self.sistema_mesas.guardar_mesas()
                
                while True:
                    print("\n--- ADMINISTRAR NOTAS ---")
                    print(f"Pedido: {pedido['nombre']}")
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
                            self.sistema_mesas.guardar_mesas()
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
                                eliminada = pedido['notas'].pop(num_nota-1)
                                self.sistema_mesas.guardar_mesas()
                                print(f"\n🗑️ Nota eliminada: '{eliminada['texto']}'")
                            else:
                                print("\n⚠️ Número de nota inválido")
                        except ValueError:
                            print("\n⚠️ Ingrese un número válido")
                    else:
                        print("\n⚠️ Opción no válida")
            
            except ValueError:
                print("\n⚠️ Error: Ingrese un número válido")

    def hacer_pedido(self, mesa_id, cliente_key):
        """Gestiona el proceso de pedido con el menú completo integrado"""
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
                    plato = self.sistema_mesas.mostrar_menu_completo()
                elif opcion_menu == 2:
                    plato = self.sistema_mesas.filtrar_por_categoria()
                elif opcion_menu == 3:
                    plato = self.sistema_mesas.filtrar_por_dieta()
                else:
                    print("Opción inválida")
                    continue
                    
                if not plato:  # Si el usuario eligió volver
                    continue
                    
                # Procesar la selección del plato
                try:
                    cantidad = int(input(f"\nCantidad de '{plato['nombre']}': "))
                    if cantidad <= 0:
                        print("La cantidad debe ser mayor a 0")
                        continue
                        
                    # Agregar pedido
                    nuevo_pedido = {
                        'id': plato['id'],
                        'nombre': plato['nombre'],
                        'cantidad': cantidad,
                        'precio': plato['precio'],
                        'hora': datetime.now().strftime("%H:%M hs"),
                        'en_cocina': False  # Por defecto no enviado a cocina
                    }
                    
                    # Agregar a la mesa
                    mesa = self.sistema_mesas.mesas[mesa_id][0]
                    mesa[cliente_key]['pedidos'].append(nuevo_pedido)
                    self.sistema_mesas.guardar_mesas()
                    
                    print(f"\n✅ {cantidad} x {plato['nombre']} agregado(s) a tu pedido")
                    print("Recuerda enviar los pedidos a cocina cuando termines")
                    
                except ValueError:
                    print("Por favor ingrese un número válido para la cantidad")
                    
            except ValueError:
                print("Por favor ingrese una opción numérica válida")
    
    def llamar_camarero(self, mesa_id, cliente_key):
        """Registra solicitud de camarero con validación y opción para volver"""
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
            
            # Obtener nombre del cliente desde sistema_mesas
            mesa = self.sistema_mesas.mesas[mesa_id][0]
            nombre_cliente = mesa[cliente_key]['nombre']
            
            # Crear comentario
            comentario = {
                "mensaje": mensaje,
                "hora": datetime.now().strftime("%H:%M hs"),
                "resuelto": False,
                "cliente": nombre_cliente
            }
            
            # Agregar comentario a la mesa
            if 'comentarios_camarero' not in mesa:
                mesa['comentarios_camarero'] = []
            mesa['comentarios_camarero'].append(comentario)
            
            # Guardar cambios
            self.sistema_mesas.guardar_mesas()
            print("\n✅ Solicitud enviada al camarero")
            return True
    
    def pagar_cuenta(self, mesa_id):
        """Procesa el pago y guarda historial en data/"""
        mesa = self.sistema_mesas.mesas[mesa_id][0]
        
        # 1. Verificar si hay pedidos para cobrar
        if not any(mesa[f"cliente_{i}"]['pedidos'] for i in range(1, mesa['capacidad'] + 1)):
            print("\n⚠️ No hay ningún plato registrado para cobrar")
            return False
        
        # 2. Verificar que todos los pedidos fueron enviados a cocina
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            for pedido in mesa[cliente_key]['pedidos']:
                if not pedido.get('en_cocina', False):
                    print("\n⚠️ No se puede pagar: hay pedidos pendientes de enviar a cocina")
                    print("   Por favor use la opción 3 para enviar pedidos a cocina")
                    return False
        
        # 3. Crear registro de historial
        registro = {
            "mesa": mesa['nombre'],
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "clientes": [],
            "total": 0
        }
        
        # Calcular total y preparar historial
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa[cliente_key]
            
            if cliente['nombre']:
                total_cliente = sum(p['precio'] * p['cantidad'] for p in cliente['pedidos'])
                registro["clientes"].append({
                    "nombre": cliente['nombre'],
                    "pedidos": cliente['pedidos'],
                    "total": total_cliente
                })
                registro["total"] += total_cliente
        
        # 4. Guardar en data/historial_pagos/
        historial_dir = os.path.join("data", "historial_pagos")
        os.makedirs(historial_dir, exist_ok=True)  # Crea la carpeta si no existe
        
        fecha_archivo = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_historial = os.path.join(historial_dir, f"mesa_{mesa_id}_{fecha_archivo}.json")
        
        with open(archivo_historial, 'w', encoding='utf-8') as f:
            json.dump(registro, f, indent=2, ensure_ascii=False)
        
        # 5. Reiniciar mesa
        self.sistema_mesas.limpiar_mesa(mesa_id)
        
        print(f"\n✅ Cuenta pagada - Total: ${registro['total']}")
        print(f"📁 Historial guardado en: {archivo_historial}")
        return True