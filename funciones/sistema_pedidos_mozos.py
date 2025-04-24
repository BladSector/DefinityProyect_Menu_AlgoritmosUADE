import json
from datetime import datetime

class SistemaPedidosMozos:
    def __init__(self, sistema_mesas):
        self.sistema_mesas = sistema_mesas
    
    def marcar_entregado(self):
        """Muestra pedidos listos para entregar y permite marcarlos como entregados"""
        while True:
            print("\n--- PEDIDOS LISTOS PARA ENTREGAR ---")
            pedidos_listos = []
            
            # Buscar todos los pedidos listos (no entregados)
            for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
                mesa = mesa_data[0]
                for i in range(1, mesa['capacidad'] + 1):
                    cliente_key = f"cliente_{i}"
                    if mesa[cliente_key]['nombre']:
                        for pedido in mesa[cliente_key]['pedidos']:
                            if not pedido.get('entregado', False):
                                pedidos_listos.append({
                                    'mesa_id': mesa_id,
                                    'mesa_nombre': mesa['nombre'],
                                    'cliente': mesa[cliente_key]['nombre'],
                                    'pedido': pedido
                                })
            
            if not pedidos_listos:
                print("No hay pedidos pendientes de entrega")
                input("\nPresione Enter para volver...")
                return
            
            # Mostrar pedidos listos con numeración
            for i, item in enumerate(pedidos_listos, 1):
                nota = f" (Nota: {item['pedido']['nota']})" if 'nota' in item['pedido'] else ""
                print(f"{i}. ({item['mesa_nombre']}) - {item['cliente']}")
                print(f"   - {item['pedido']['cantidad']}x {item['pedido']['nombre']}{nota}")
            
            print("\n0. Volver al menú anterior")
            
            try:
                opcion = int(input("\nSeleccione el pedido a marcar como entregado: "))
                if opcion == 0:
                    return
                if opcion < 1 or opcion > len(pedidos_listos):
                    print("Opción inválida")
                    continue
                    
                # Marcar como entregado
                pedido_seleccionado = pedidos_listos[opcion-1]['pedido']
                pedido_seleccionado['entregado'] = True
                pedido_seleccionado['hora_entrega'] = datetime.now().strftime("%H:%M hs")
                self.sistema_mesas.guardar_mesas()
                
                print(f"\n✅ Pedido marcado como entregado:")
                print(f"Mesa {pedidos_listos[opcion-1]['mesa_id']} - {pedidos_listos[opcion-1]['cliente']}")
                print(f"{pedido_seleccionado['cantidad']}x {pedido_seleccionado['nombre']}")
                
            except ValueError:
                print("Por favor ingrese un número válido")
    
    def mostrar_comentarios_mesas(self):
        """Muestra todas las mesas con comentarios y sus pedidos"""
        print("\n--- MESAS CON COMENTARIOS ---")
        mesas_con_comentarios = False
        
        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            comentarios = mesa.get('comentarios_camarero', [])
            
            if comentarios:
                mesas_con_comentarios = True
                print(f"\n--{mesa['nombre']}--")
                print(f"Estado: {mesa['estado'].upper()}")
                
                # Mostrar comentarios
                print("\n📝 Comentarios:")
                for i, comentario in enumerate(comentarios, 1):
                    estado = "✅ Resuelto" if comentario['resuelto'] else "⚠️ Pendiente"
                    print(f"{i}.  [{estado}] {comentario['cliente']}: {comentario['mensaje']}")
                    print(f"   Hora: {comentario['hora']}")
                
                # Mostrar pedidos activos
                print("\n🍽️ Pedidos en mesa:")
                for i in range(1, mesa['capacidad'] + 1):
                    cliente_key = f"cliente_{i}"
                    if mesa[cliente_key]['nombre']:
                        print(f"\n{mesa[cliente_key]['nombre']}:")
                        for pedido in mesa[cliente_key]['pedidos']:
                            nota = f" (Nota: {pedido['nota']})" if 'nota' in pedido else ""
                            print(f"  - {pedido['cantidad']}x {pedido['nombre']}{nota}")
        
        if not mesas_con_comentarios:
            print("No hay mesas con comentarios pendientes")
    
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
                
                # Mostrar comentarios si existen
                if mesa.get('comentarios_camarero'):
                    print("\n📢 Comentarios:")
                    for comentario in mesa['comentarios_camarero']:
                        estado = "✅" if comentario['resuelto'] else "⚠️"
                        print(f"  {estado} {comentario['cliente']}: {comentario['mensaje']}")
