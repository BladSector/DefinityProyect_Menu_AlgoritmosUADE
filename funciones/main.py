import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .sistema_mesas import SistemaMesas
from .sistema_pedidos_clientes import SistemaPedidosClientes
from .sistema_pedidos_cocina import SistemaPedidosCocina
from .sistema_pedidos_mozos import SistemaPedidosMozos

# URL de mesa 1. Copiar y pegar en URL de QR (cambiar el número de mesa para las distinas mesas):
# https://turestaurante.com/menu/mesa-1
# " python -m funciones.main "desde el bash para ejecutar main.py


def main():
    sistema = SistemaMesas()
    sistema_pedidos_clientes = SistemaPedidosClientes(sistema)
    sistema_pedidos_cocina = SistemaPedidosCocina(sistema)
    sistema_pedidos_mozos = SistemaPedidosMozos(sistema)
    while True:
        try:
            print("\n=== SISTEMA RESTAURANTE ===")
            print("Seleccione su rol:")
            print("1. Cliente")
            print("2. Empleado")
            print("0. Salir")
            
            rol = input("Opción: ")
            
            if rol == "1":
                interfaz_cliente(sistema, sistema_pedidos_clientes)
            elif rol == "2":
                interfaz_empleado(sistema_pedidos_cocina, sistema_pedidos_mozos)
            elif rol == "0":
                break
            else:
                print("Opción inválida \n")
        except ValueError:
            print()
        
def interfaz_cliente(sistema, sistema_pedidos_clientes):
    print("\n=== ACCESO CLIENTE ===")
    qr_url = input("Ingrese URL del QR escaneado: ")

    mesa_id, mesa = sistema.obtener_mesa_por_url(qr_url)
    if not mesa:
        print("Mesa no encontrada")
        return

    print(f"\nBienvenido a {mesa['nombre']} (Capacidad: {mesa['capacidad']})")

    # Bucle para validar que el nombre no esté vacío
    while True:
        nombre_cliente = input("Ingrese su nombre: ").strip()
        if not nombre_cliente:
            print("\n⚠️ Error: No puede dejar el nombre vacío. Por favor ingrese su nombre.")
        else:
            break

    cliente_key = sistema.registrar_cliente(mesa_id, nombre_cliente)

    if not cliente_key:
        print("Mesa llena o nombre ya registrado")
        return

    sistema_pedidos_clientes.cliente_actual = cliente_key # Establecer cliente actual

    while True:
        try:
            print(f"\n--- MENÚ CLIENTE: {nombre_cliente} ---")
            print("1. Ver menú y hacer pedido")
            print("2. Ver resumen grupal")
            print("3. Confirmar y enviar pedido a cocina")
            print("4. Agregar nota a pedido")
            print("5. Llamar al camarero")
            print("6. Pagar cuenta")
            print("0. Volver")

            opcion = input("Seleccione una opción: ")

            if opcion == "0":
                return
            elif opcion == "1":
                # Verificar si hay pedidos antes de mostrar la opción
                mesa_data = sistema.mesas[mesa_id][0]
                tiene_pedidos = any(len(mesa_data[f"cliente_{i}"]['pedidos']) > 0
                                    for i in range(1, mesa_data['capacidad'] + 1))
                
                if tiene_pedidos:
                    sistema_pedidos_clientes.hacer_pedido(mesa_id, cliente_key)
                else:
                    print("\n⚠️ No hay pedidos para realizar")
            elif opcion == "2":
                sistema_pedidos_clientes.mostrar_resumen_grupal(mesa_id)
            elif opcion == "3":
                # Verificar si hay pedidos antes de mostrar la opción
                mesa_data = sistema.mesas[mesa_id][0]
                tiene_pedidos = any(len(mesa_data[f"cliente_{i}"]['pedidos']) > 0
                                    for i in range(1, mesa_data['capacidad'] + 1))

                if tiene_pedidos:
                    sistema_pedidos_clientes.confirmar_envio_cocina(mesa_id)
                else:
                    print("\n⚠️ No hay pedidos para enviar a cocina")
            elif opcion == "4":
                sistema_pedidos_clientes.agregar_nota_pedido(mesa_id, cliente_key)
            elif opcion == "5":
                sistema_pedidos_clientes.llamar_camarero(mesa_id, cliente_key)
            elif opcion == "6":
                mesa_data = sistema.mesas[mesa_id][0]
                todos_entregados = True
                for i in range(1, mesa_data['capacidad'] + 1):
                    cliente = mesa_data.get(f"cliente_{i}")
                    if cliente and cliente.get('pedidos'):
                        for pedido in cliente['pedidos']:
                            # Ignorar pedidos cancelados
                            if pedido.get('estado_cocina') != '🔴 CANCELADO' and not pedido.get('entregado', False):
                                todos_entregados = False
                                break
                    if not todos_entregados:
                        break

                if todos_entregados:
                    # Encontrar el cliente activo
                    cliente_key = None
                    for i in range(1, mesa_data['capacidad'] + 1):
                        if mesa_data.get(f"cliente_{i}", {}).get('nombre') == nombre_cliente:
                            cliente_key = f"cliente_{i}"
                            break
                    
                    if cliente_key:
                        if sistema_pedidos_clientes.pagar_cuenta(mesa_id, cliente_key):
                            return
                    else:
                        print("\n⚠️ Error: No se encontró el cliente en la mesa.")
                else:
                    print("\n⚠️ No se puede pagar aún. Todos los pedidos deben estar marcados como 'entregado' en mesa.")
            else:
                print("Opción no válida")
        except ValueError:
            print("Entrada inválida")

def interfaz_empleado(sistema_pedidos_cocina, sistema_pedidos_mozos):
    while True:
        try:
            print("\n=== ACCESO EMPLEADO ===")
            print("Seleccione departamento:")
            print("1. Cocina")
            print("2. Mozos/Camareros")
            print("0. Volver")
            
            depto = input("Opción: ")
            
            if depto == "1":
                interfaz_cocina(sistema_pedidos_cocina)
            elif depto == "2":
                interfaz_mozos(sistema_pedidos_mozos)
            elif depto == "0":
                return
            else:
                print("Opción inválida \n")
        except ValueError:
            print("")

def interfaz_cocina(sistema_pedidos_cocina):
    while True:
        try:
            print("\n=== INTERFAZ COCINA ===")
            print("--- OPCIONES ---")
            print("1. Mapa del Restaurante")
            print("2. Gestionar pedidos activos")
            print("0. Volver al menú principal")
            
            opcion = input("\nSeleccione una opción: ").strip()
            
            if opcion == "0":
                print("\nVolviendo al menú principal...")
                return
            elif opcion == "1":
                sistema_pedidos_cocina.mostrar_mapa_mesas()
            elif opcion == "2":
                pedidos_activos = sistema_pedidos_cocina.mostrar_pedidos_activos()
                if not pedidos_activos:
                    print("\nNo hay pedidos activos para gestionar.")
                    continue

                print("\n=== GESTIONAR PEDIDOS ===")
                for i, pedido in enumerate(pedidos_activos, 1):
                    print(f"\n{i}. Mesa {pedido['mesa_id']} - Cliente: {pedido['cliente']}")
                    print(f"   - {pedido['cantidad']}x {pedido['nombre']} [{pedido['estado_cocina']}]")
                    if pedido.get('notas'):
                        print("     📝 Notas:")
                        for nota in pedido['notas']:
                            print(f"       • {nota['texto']}")

                print("\n0. Volver al menú anterior")
                try:
                    seleccion = int(input("\nSeleccione un pedido para gestionar (número): "))
                    if seleccion == 0:
                        continue
                    
                    if 1 <= seleccion <= len(pedidos_activos):
                        pedido = pedidos_activos[seleccion - 1]
                        print(f"\n=== GESTIONANDO PEDIDO ===")
                        print(f"Mesa: {pedido['mesa_id']}")
                        print(f"Cliente: {pedido['cliente']}")
                        print(f"Pedido: {pedido['cantidad']}x {pedido['nombre']}")
                        print(f"Estado actual: {pedido['estado_cocina']}")

                        if pedido['estado_cocina'] == sistema_pedidos_cocina.estados_pedido['pendiente']:
                            print("\n1. Marcar como EN PREPARACIÓN")
                            print("2. Cancelar pedido")
                            print("0. Volver")
                            
                            opcion = input("\nSeleccione una opción: ")
                            if opcion == "1":
                                if sistema_pedidos_cocina.actualizar_estado_pedido(pedido['mesa_id'], pedido['id'], 'en_preparacion'):
                                    print("\n✅ Pedido marcado como EN PREPARACIÓN")
                            elif opcion == "2":
                                print("\n⚠️ ¿Está seguro que desea cancelar este pedido?")
                                print("1. Sí, cancelar")
                                print("2. No, volver")
                                confirmacion = input("\nSeleccione una opción: ")
                                if confirmacion == "1":
                                    if sistema_pedidos_cocina.actualizar_estado_pedido(pedido['mesa_id'], pedido['id'], 'cancelado'):
                                        print("\n✅ Pedido cancelado")
                                else:
                                    print("\n❌ Cancelación abortada")
                            elif opcion == "0":
                                continue
                            else:
                                print("Opción inválida")
                        elif pedido['estado_cocina'] == sistema_pedidos_cocina.estados_pedido['en_preparacion']:
                            print("\n1. Marcar como LISTO PARA ENTREGAR")
                            print("2. Cancelar pedido")
                            print("0. Volver")
                            
                            opcion = input("\nSeleccione una opción: ")
                            if opcion == "1":
                                if sistema_pedidos_cocina.actualizar_estado_pedido(pedido['mesa_id'], pedido['id'], 'listo'):
                                    print("\n✅ Pedido marcado como LISTO PARA ENTREGAR")
                            elif opcion == "2":
                                print("\n⚠️ ¿Está seguro que desea cancelar este pedido?")
                                print("1. Sí, cancelar")
                                print("2. No, volver")
                                confirmacion = input("\nSeleccione una opción: ")
                                if confirmacion == "1":
                                    if sistema_pedidos_cocina.actualizar_estado_pedido(pedido['mesa_id'], pedido['id'], 'cancelado'):
                                        print("\n✅ Pedido cancelado")
                                else:
                                    print("\n❌ Cancelación abortada")
                            elif opcion == "0":
                                continue
                            else:
                                print("Opción inválida")
                        else:
                            print("\n⚠️ Este pedido no puede ser modificado.")
                    else:
                        print("Número de pedido inválido")
                except ValueError:
                    print("Por favor ingrese un número válido")
            else:
                print("\n⚠️ Opción no válida. Por favor seleccione 0, 1 o 2")
                
        except KeyboardInterrupt:
            print("\n\nOperación cancelada por el usuario")
            return
        except Exception as e:
            print(f"\n⚠️ Error inesperado: {str(e)}")
            continue

def interfaz_mozos(sistema_pedidos_mozos):
    while True:
        try:
            print("\n=== INTERFAZ MOZOS ===")
            print("--- OPCIONES ---")
            print("1. Mapa del Restaurante")
            print("2. Marcar pedido como entregado")
            print("3. Comentarios de Mesas")
            print("4. Reiniciar mesa")
            print("0. Volver")

            opcion = input("Seleccione una opción: ")

            if opcion == "0":
                return
            elif opcion == "1":
                sistema_pedidos_mozos.mostrar_mapa_mesas()
            elif opcion == "2":
                sistema_pedidos_mozos.gestionar_entregas()
            elif opcion == "3":
                sistema_pedidos_mozos.gestionar_comentarios()
            elif opcion == "4":
                # Mostrar solo mesas ocupadas
                mesas_ocupadas = [(mid, m[0]) for mid, m in sistema_pedidos_mozos.sistema_mesas.mesas.items() if m[0]['estado'] == 'ocupada']
                if not mesas_ocupadas:
                    print("\nNo hay mesas ocupadas para reiniciar.")
                    continue
                print("\n=== REINICIAR MESA ===")
                for idx, (mid, mesa) in enumerate(mesas_ocupadas, 1):
                    print(f"{idx}. {mesa['nombre']}")
                print("0. Volver al menú principal")
                seleccion = input("\nSeleccione la mesa a reiniciar (número): ")
                if seleccion == "0":
                    continue
                try:
                    seleccion = int(seleccion)
                    if 1 <= seleccion <= len(mesas_ocupadas):
                        mid, mesa = mesas_ocupadas[seleccion-1]
                        print(f"\n⚠️ ¿Está seguro que desea reiniciar la {mesa['nombre']}?")
                        print("1. Sí, reiniciar mesa")
                        print("2. No, volver")
                        confirm = input("\nSeleccione una opción: ")
                        if confirm == "1":
                            sistema_pedidos_mozos.reiniciar_mesa(mid)
                        else:
                            print("\nOperación cancelada.")
                    else:
                        print("Opción inválida.")
                except ValueError:
                    print("Por favor ingrese un número válido.")
            else:
                print("Opción no válida")
        except ValueError:
            print("")
            

if __name__ == "__main__":
    main()