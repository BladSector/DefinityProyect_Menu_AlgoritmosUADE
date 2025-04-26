from sistema_mesas import SistemaMesas
from sistema_pedidos_clientes import SistemaPedidosClientes
from sistema_pedidos_cocina import SistemaPedidosCocina
from sistema_pedidos_mozos import SistemaPedidosMozos

# URL de mesa 1. Copiar y pegar en URL de QR (cambiar el número de mesa para las distinas mesas):
# https://turestaurante.com/menu/mesa-1

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
                sistema_pedidos_clientes.hacer_pedido(mesa_id, cliente_key)
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
                            if not pedido.get('entregado', False):
                                todos_entregados = False
                                break
                    if not todos_entregados:
                        break

                if todos_entregados:
                    if sistema_pedidos_clientes.pagar_cuenta(mesa_id):
                        return
                else:
                    print("\n⚠️ No se puede pagar aún. Todos los pedidos deben estar marcados como 'entregado' en mesa.")
                    #sistema_pedidos_clientes.mostrar_resumen_grupal(mesa_id) # Opcional: mostrar qué falta
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
    """
    Interfaz principal para el sistema de cocina
    
    Args:
        sistema_pedidos_cocina (SistemaPedidosCocina): Instancia del sistema de pedidos
        
    Ejemplo:
        >>> sistema = SistemaPedidosCocina(sistema_mesas)
        >>> interfaz_cocina(sistema)
    """

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
                sistema_pedidos_cocina.mostrar_pedidos_activos()
            else:
                print("\n⚠️ Opción no válida. Por favor seleccione 0, 1 o 2")
                
        except KeyboardInterrupt:
            print("\n\nOperación cancelada por el usuario")
            return
        except Exception as e:
            print(f"\n⚠️ Error inesperado: {str(e)}")
            # Opcional: Registrar el error en un log
            continue

def interfaz_mozos(sistema_pedidos_mozos):
    while True:
        try:
            print("\n=== INTERFAZ MOZOS ===")
            print("--- OPCIONES ---")
            print("1. Mapa del Restaurante")
            print("2. Marcar pedido como entregado")
            print("3. Comentarios de Mesas")
            print("0. Volver")

            opcion = input("Seleccione una opción: ")

            if opcion == "0":
                return
            elif opcion == "1":
                sistema_pedidos_mozos.mostrar_mapa_mesas()
            elif opcion == "2":
                sistema_pedidos_mozos.gestionar_entregas() # Llamar a la función correcta
            elif opcion == "3":
                sistema_pedidos_mozos.gestionar_comentarios() # Había un error tipográfico aquí, lo corregí a gestionar_comentarios
            else:
                print("Opción no válida")
        except ValueError:
            print("")
            

if __name__ == "__main__":
    main()