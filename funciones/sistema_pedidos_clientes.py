import json
from datetime import datetime

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
                        print(f"  - {pedido['cantidad']}x {pedido['nombre']} 🟢 En cocina (desde {hora_envio})")
                        
                        # Mostrar notas (sistema nuevo y antiguo)
                        if 'notas' in pedido and pedido['notas']:
                            print("    📝 Notas:")
                            for nota in pedido['notas']:
                                print(f"      • {nota['texto']} ({nota['hora']})")
                        elif 'nota' in pedido and pedido['nota']:
                            print(f"    📝 Nota: {pedido['nota']} (sistema anterior)")
        
        if not hay_en_cocina:
            print("  (No hay pedidos en cocina aún)")
        
        # Mostrar comentarios al camarero
        print("\n--- SOLICITUDES AL CAMARERO ---")
        if mesa.get('comentarios_camarero'):
            for comentario in mesa['comentarios_camarero']:
                estado = "✅ Resuelto" if comentario['resuelto'] else "🟡 Pendiente"
                print(f"\n👤 {comentario['cliente']} - {comentario['hora']} {estado}:")
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
                        pedido['hora_envio'] = datetime.now().strftime("%H:%M:%S")
        
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
                        'hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                                'hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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