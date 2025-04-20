import json
from datetime import datetime

class SistemaPedidosClientes:
    def __init__(self, sistema_mesas):
        self.sistema_mesas = sistema_mesas
    
    def mostrar_resumen_grupal(self, mesa_id):
        """Muestra el resumen grupal de pedidos antes de confirmar"""
        mesa = self.sistema_mesas.mesas[mesa_id][0]
        clientes_confirmados = 0
        total_clientes = 0
        
        print("\n--- RESUMEN GRUPAL ---")
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre']:
                total_clientes += 1
                print(f"\n{mesa[cliente_key]['nombre']}:")
                if mesa[cliente_key]['pedidos']:
                    clientes_confirmados += 1
                    for pedido in mesa[cliente_key]['pedidos']:
                        print(f"  - {pedido['cantidad']}x {pedido['nombre']}")
                else:
                    print("  (Sin pedidos aún)")
        
        if clientes_confirmados < total_clientes:
            print(f"\n⚠️ Faltan {total_clientes - clientes_confirmados} confirmaciones")
        else:
            print("\n✅ Todos los clientes han confirmado sus pedidos")
    
    def confirmar_envio_cocina(self, mesa_id):
        """Confirma el envío del pedido a cocina si hay pedidos"""
        mesa = self.sistema_mesas.mesas[mesa_id][0]
        tiene_pedidos = False
        
        # Verificar si hay al menos un pedido en la mesa
        for i in range(1, mesa['capacidad'] + 1):
            cliente_key = f"cliente_{i}"
            if mesa[cliente_key]['nombre'] and mesa[cliente_key]['pedidos']:
                tiene_pedidos = True
                break
        
        if not tiene_pedidos:
            print("\n⚠️ No hay pedidos para enviar a cocina")
            return
        
        # Si hay pedidos, proceder con el envío
        self.sistema_mesas.guardar_mesas()
        print("\n🚀 Pedido enviado a cocina con éxito")
        
    def agregar_nota_pedido(self, mesa_id, cliente_key):
        """Agrega una nota especial a un pedido seleccionado"""
        mesa = self.sistema_mesas.mesas[mesa_id][0]
        cliente = mesa[cliente_key]
    
        if not cliente['pedidos']:
            print("\n⚠️ No tienes pedidos registrados")
            return
    
        print("\n--- TUS PEDIDOS ---")
        for i, pedido in enumerate(cliente['pedidos'], 1):
            print(f"{i}. {pedido['nombre']} - {pedido['cantidad']}x (${pedido['precio'] * pedido['cantidad']})")
            if 'nota' in pedido:
                print(f"   Nota actual: {pedido['nota']}")
    
        try:
            opcion = int(input("\nSeleccione el número de pedido a modificar (0 para cancelar): "))
            if opcion == 0:
                return
            if opcion < 1 or opcion > len(cliente['pedidos']):
                print("Número de pedido inválido")
                return
            
            nota = input("Ingrese la nueva nota (deje vacío para eliminar): ").strip()
            pedido_seleccionado = cliente['pedidos'][opcion-1]
        
            if nota:
                pedido_seleccionado['nota'] = nota
                print("\n📝 Nota agregada al pedido")
            else:
                if 'nota' in pedido_seleccionado:
                    del pedido_seleccionado['nota']
                    print("\n🗑️ Nota eliminada del pedido")
                else:
                    print("\nℹ️ El pedido no tenía notas")
                
            self.sistema_mesas.guardar_mesas()
        
        except ValueError:
            print("Por favor ingrese un número válido")