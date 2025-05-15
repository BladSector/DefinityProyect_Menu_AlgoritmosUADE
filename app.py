import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template
from funciones.sistema_mesas import SistemaMesas
from funciones.sistema_pedidos_clientes import SistemaPedidosClientes
from funciones.sistema_pedidos_cocina import SistemaPedidosCocina
from funciones.sistema_pedidos_mozos import SistemaPedidosMozos
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Inicializar sistemas
sistema_mesas = SistemaMesas()
sistema_pedidos_clientes = SistemaPedidosClientes(sistema_mesas)
sistema_pedidos_mozos = SistemaPedidosMozos(sistema_mesas)
sistema_pedidos_cocina = SistemaPedidosCocina(sistema_mesas)

# Rutas para vistas
@app.route('/')
def index():
    return render_template('clientes.html', mesas=sistema_mesas.obtener_mesas(), menu=sistema_mesas.mostrar_menu_completo())

@app.route('/clientes')
def vista_clientes():
    return render_template('clientes.html', mesas=sistema_mesas.obtener_mesas(), menu=sistema_mesas.mostrar_menu_completo())

@app.route('/cocina')
def vista_cocina():
    return render_template('cocina.html', pedidos=sistema_pedidos_cocina.mostrar_pedidos_activos())

@app.route('/mozos')
def vista_mozos():
    return render_template('mozos.html', mesas=sistema_mesas.obtener_mesas())

# Endpoints de Mesas
@app.route('/api/mesas', methods=['GET'])
def obtener_mesas():
    """Obtiene todas las mesas disponibles."""
    try:
        mesas = sistema_mesas.obtener_mesas()
        return jsonify({"success": True, "data": mesas})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mesas/acceder', methods=['POST'])
def acceder_mesa():
    """Accede a una mesa usando la URL del QR y el nombre del cliente."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400
            
        qr_url = data.get('qr_url')
        nombre = data.get('nombre')
        
        if not qr_url or not nombre:
            return jsonify({"success": False, "error": "Se requiere URL del QR y nombre del cliente"}), 400
        
        # Extraer el ID de la mesa de la URL del QR
        try:
            # Manejar diferentes formatos de URL
            if 'mesa-' in qr_url:
                mesa_id = qr_url.split('mesa-')[-1].split('?')[0]
            else:
                mesa_id = qr_url.split('/')[-1].split('?')[0]
            
            # Verificar que el ID de la mesa es válido
            if not mesa_id or not mesa_id.isdigit():
                return jsonify({"success": False, "error": "ID de mesa inválido"}), 400
                
            # Convertir el ID a entero para validación
            mesa_id = int(mesa_id)
                
        except Exception as e:
            print(f"Error al procesar URL: {str(e)}")
            return jsonify({"success": False, "error": "Error al procesar la URL del QR"}), 400
        
        # Verificar que la mesa existe
        try:
            mesa_data = sistema_mesas.obtener_mesa(str(mesa_id))
            if not mesa_data:
                return jsonify({"success": False, "error": "Mesa no encontrada"}), 404
            
            mesa = mesa_data[0]
            
            # Si la mesa está libre, registrar al cliente
            if mesa['estado'] == 'libre':
                cliente_key = sistema_mesas.registrar_cliente(str(mesa_id), nombre)
                if not cliente_key:
                    return jsonify({"success": False, "error": "No se pudo registrar al cliente en la mesa"}), 400
                return jsonify({
                    "success": True,
                    "mesa_id": str(mesa_id),
                    "cliente_key": cliente_key,
                    "message": "Cliente registrado exitosamente en la mesa"
                })
            
            # Si la mesa está ocupada, buscar al cliente o agregarlo si hay espacio
            cliente_key = None
            
            # Primero buscar si el cliente ya existe
            for i in range(1, mesa.get('capacidad', 0) + 1):
                key = f"cliente_{i}"
                if key in mesa and mesa[key].get('nombre') == nombre:
                    cliente_key = key
                    break
            
            # Si el cliente no existe, buscar un espacio libre
            if not cliente_key:
                for i in range(1, mesa.get('capacidad', 0) + 1):
                    key = f"cliente_{i}"
                    if not mesa[key].get('nombre'):
                        mesa[key]['nombre'] = nombre
                        mesa[key]['pedidos'] = []
                        cliente_key = key
                        sistema_mesas.guardar_mesas()
                        break
            
            if not cliente_key:
                return jsonify({"success": False, "error": "La mesa está llena"}), 400
            
            return jsonify({
                "success": True,
                "mesa_id": str(mesa_id),
                "cliente_key": cliente_key,
                "message": "Acceso exitoso a la mesa"
            })
            
        except Exception as e:
            print(f"Error al acceder a la mesa: {str(e)}")
            return jsonify({"success": False, "error": "Error al acceder a la mesa"}), 500
        
    except Exception as e:
        print(f"Error general en acceder_mesa: {str(e)}")
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500

@app.route('/api/mesas/<mesa_id>', methods=['GET'])
def obtener_mesa(mesa_id):
    """Obtiene una mesa específica."""
    try:
        mesa = sistema_mesas.obtener_mesa(mesa_id)
        if mesa:
            return jsonify({"success": True, "data": mesa})
        return jsonify({"success": False, "error": "Mesa no encontrada"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mesas/<mesa_id>/ocupar', methods=['POST'])
def ocupar_mesa(mesa_id):
    """Ocupa una mesa con los clientes especificados."""
    try:
        data = request.get_json()
        clientes = data.get('clientes', [])
        if not clientes:
            return jsonify({"success": False, "error": "Se requiere al menos un cliente"}), 400
        
        resultado = sistema_mesas.ocupar_mesa(mesa_id, clientes)
        if resultado:
            return jsonify({"success": True, "message": "Mesa ocupada exitosamente"})
        return jsonify({"success": False, "error": "No se pudo ocupar la mesa"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mesas/<mesa_id>/agregar-cliente', methods=['POST'])
def agregar_cliente_mesa(mesa_id):
    """Agrega un nuevo cliente a una mesa existente."""
    try:
        data = request.get_json()
        nombre_cliente = data.get('nombre')
        if not nombre_cliente:
            return jsonify({"success": False, "error": "Se requiere el nombre del cliente"}), 400
        
        resultado = sistema_mesas.agregar_cliente_mesa(mesa_id, nombre_cliente)
        if resultado:
            return jsonify({"success": True, "message": "Cliente agregado exitosamente"})
        return jsonify({"success": False, "error": "No se pudo agregar el cliente"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Endpoints de Pedidos
@app.route('/api/mesas/<mesa_id>/pedidos', methods=['GET'])
def obtener_pedidos_mesa(mesa_id):
    """Obtiene los pedidos de una mesa específica."""
    try:
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({"success": False, "error": "Mesa no encontrada"}), 404
        
        mesa = mesa_data[0]  # Accedemos al primer elemento del array
        pedidos = []
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                pedidos.append({
                    "cliente": cliente['nombre'],
                    "pedidos": cliente.get('pedidos', [])
                })
        
        return jsonify({"success": True, "data": pedidos})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mesas/<mesa_id>/clientes/<cliente_key>/pedidos', methods=['POST'])
def hacer_pedido(mesa_id, cliente_key):
    """Realiza un nuevo pedido para un cliente específico."""
    try:
        data = request.get_json()
        plato_id = data.get('plato_id')
        
        if not plato_id:
            return jsonify({"success": False, "error": "Se requiere el ID del plato"}), 400
        
        # Obtener la mesa
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({"success": False, "error": "Mesa no encontrada"}), 404

        mesa = mesa_data[0]  # Accedemos al primer elemento del array

        # Verificar que el cliente existe en la mesa
        cliente = mesa.get(cliente_key)
        if not cliente or not cliente.get('nombre'):
            return jsonify({"success": False, "error": "Cliente no encontrado en la mesa"}), 404

        # Obtener el menú completo para encontrar el plato
        menu_completo = sistema_mesas.mostrar_menu_completo()
        plato_encontrado = None
        for item in menu_completo:
            if str(item['index']) == str(plato_id):
                plato_encontrado = item['plato']
                break

        if not plato_encontrado:
            return jsonify({"success": False, "error": "Plato no encontrado en el menú"}), 404

        # Crear el nuevo pedido
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        if 'contador_pedidos' not in cliente:
            cliente['contador_pedidos'] = 0
        cliente['contador_pedidos'] += 1
        pedido_id = f"{timestamp}_{cliente['contador_pedidos']}"

        nuevo_pedido = {
            'id': pedido_id,
            'plato_id': plato_encontrado['id'],
            'nombre': plato_encontrado['nombre'],
            'cantidad': 1,
            'precio': plato_encontrado['precio'],
            'hora': datetime.now().strftime("%H:%M hs"),
            'en_cocina': False,
            'estado_cocina': '🟡 Pendiente'
        }

        # Agregar el pedido al cliente
        if 'pedidos' not in cliente:
            cliente['pedidos'] = []
        cliente['pedidos'].append(nuevo_pedido)

        # Guardar los cambios
        sistema_mesas.guardar_mesas()

        return jsonify({
            "success": True,
            "message": "Pedido realizado exitosamente",
            "data": nuevo_pedido
        })

    except Exception as e:
        print(f"Error en hacer_pedido: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Endpoints de Menú
@app.route('/api/menu', methods=['GET'])
def obtener_menu():
    """Obtiene el menú completo."""
    try:
        menu = sistema_mesas.mostrar_menu_completo()
        return jsonify({"success": True, "data": menu})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/menu/categorias', methods=['GET'])
def obtener_categorias():
    """Obtiene las categorías disponibles del menú."""
    try:
        categorias = sistema_mesas.filtrar_por_categoria()
        return jsonify({"success": True, "data": categorias})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/menu/dietas', methods=['GET'])
def obtener_dietas():
    """Obtiene las dietas disponibles del menú."""
    try:
        dietas = sistema_mesas.obtener_dietas_disponibles()
        return jsonify({"success": True, "data": dietas})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def _normalizar_categoria(categoria):
    """Normaliza el nombre de la categoría para comparación."""
    categoria_normalizada = categoria.lower().replace('/', ' ').strip()
    print(f"Normalizando categoría: '{categoria}' -> '{categoria_normalizada}'")
    return categoria_normalizada

@app.route('/api/menu/categorias/<categoria>', methods=['GET'])
def obtener_platos_categoria(categoria):
    """Obtiene los platos de una categoría específica."""
    try:
        menu = sistema_mesas.mostrar_menu_completo()
        platos_categoria = []
        categoria_normalizada = _normalizar_categoria(categoria)
        
        print(f"Buscando platos para categoría normalizada: '{categoria_normalizada}'")
        
        for item in menu:
            plato = item['plato']
            # Buscar en todas las etapas del menú
            for etapa in sistema_mesas.menu['platos'].values():
                for cat_nombre, platos in etapa.items():
                    cat_nombre_normalizado = _normalizar_categoria(cat_nombre)
                    print(f"Comparando con categoría del menú: '{cat_nombre}' -> '{cat_nombre_normalizado}'")
                    if cat_nombre_normalizado == categoria_normalizada:
                        for plato_cat in platos:
                            if plato_cat['nombre'] == plato['nombre']:
                                platos_categoria.append({
                                    'id': item['index'],
                                    'nombre': plato['nombre'],
                                    'descripcion': plato.get('descripcion', ''),
                                    'precio': plato['precio'],
                                    'ingredientes': plato.get('ingredientes', []),
                                    'dietas': plato.get('dietas', [])
                                })
                                break
        
        if not platos_categoria:
            print(f"No se encontraron platos para la categoría '{categoria_normalizada}'")
            return jsonify({
                'success': False,
                'error': f'No se encontraron platos en la categoría {categoria}'
            }), 404
            
        return jsonify({
            'success': True,
            'data': platos_categoria
        })
        
    except Exception as e:
        print(f"Error en obtener_platos_categoria: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/menu/dietas/<dieta>', methods=['GET'])
def obtener_platos_dieta(dieta):
    """Obtiene los platos de una dieta específica."""
    try:
        menu = sistema_mesas.mostrar_menu_completo()
        platos_dieta = []
        
        for item in menu:
            plato = item['plato']
            if dieta.lower() in [d.lower() for d in plato.get('dietas', [])]:
                platos_dieta.append({
                    'id': item['index'],
                    'nombre': plato['nombre'],
                    'descripcion': plato.get('descripcion', ''),
                    'precio': plato['precio'],
                    'ingredientes': plato.get('ingredientes', []),
                    'dietas': plato.get('dietas', [])
                })
        
        if not platos_dieta:
            return jsonify({
                'success': False,
                'error': f'No se encontraron platos para la dieta {dieta}'
            }), 404
            
        return jsonify({
            'success': True,
            'data': platos_dieta
        })
        
    except Exception as e:
        print(f"Error en obtener_platos_dieta: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Endpoints de Pagos
@app.route('/api/mesas/<mesa_id>/clientes/<cliente_key>/pagar', methods=['POST'])
def pagar_cuenta(mesa_id, cliente_key):
    """Procesa el pago de un cliente."""
    try:
        data = request.get_json()
        tipo_pago = data.get('tipo_pago')  # 'individual' o 'grupal'
        metodo_pago = data.get('metodo_pago')  # 'efectivo' o 'tarjeta'
        
        if not tipo_pago or not metodo_pago:
            return jsonify({"success": False, "error": "Se requiere tipo y método de pago"}), 400
        
        # Obtener la mesa
        mesa = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa:
            return jsonify({"success": False, "error": "Mesa no encontrada"}), 404

        # Verificar que el cliente existe
        cliente = mesa.get(cliente_key)
        if not cliente or not cliente.get('nombre'):
            return jsonify({"success": False, "error": "Cliente no encontrado en la mesa"}), 404

        # Procesar el pago
        resultado = sistema_pedidos_clientes.pagar_cuenta(mesa_id, cliente_key)
        if resultado:
            return jsonify({
                "success": True,
                "message": "Pago procesado exitosamente",
                "data": {
                    "tipo_pago": tipo_pago,
                    "metodo_pago": metodo_pago,
                    "mesa_id": mesa_id,
                    "cliente": cliente['nombre']
                }
            })
        return jsonify({"success": False, "error": "No se pudo procesar el pago"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Endpoints de Cocina
@app.route('/api/cocina/pedidos', methods=['GET'])
def obtener_pedidos_cocina():
    """Obtiene los pedidos activos en cocina."""
    try:
        pedidos = sistema_pedidos_cocina.mostrar_pedidos_activos()
        return jsonify({"success": True, "data": pedidos})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cocina/pedidos/<pedido_id>/estado', methods=['PUT'])
def actualizar_estado_pedido_cocina(pedido_id):
    """Actualiza el estado de un pedido."""
    try:
        data = request.get_json()
        nuevo_estado = data.get('estado')
        mesa_id = data.get('mesa_id')
        
        if not nuevo_estado or not mesa_id:
            return jsonify({
                'success': False,
                'error': 'Se requiere estado y mesa_id'
            }), 400
            
        success = sistema_pedidos_cocina.actualizar_estado_pedido(mesa_id, pedido_id, nuevo_estado)
        return jsonify({
            'success': success,
            'message': 'Estado del pedido actualizado'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Endpoints de Mozos
@app.route('/api/mozos/mesas', methods=['GET'])
def obtener_mesas_mozos():
    """Obtiene el mapa de mesas para los mozos."""
    try:
        mesas = sistema_pedidos_mozos.mostrar_mapa_mesas()
        return jsonify({"success": True, "data": mesas})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mozos/pedidos/<pedido_id>/entregar', methods=['PUT'])
def marcar_pedido_entregado(pedido_id):
    """Marca un pedido como entregado."""
    try:
        resultado = sistema_pedidos_mozos.marcar_pedido_entregado(pedido_id)
        if resultado:
            return jsonify({"success": True, "message": "Pedido marcado como entregado"})
        return jsonify({"success": False, "error": "No se pudo marcar el pedido como entregado"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mozos/mesas/<mesa_id>/comentarios', methods=['GET'])
def obtener_comentarios_mesa(mesa_id):
    """Obtiene los comentarios de una mesa."""
    try:
        comentarios = sistema_pedidos_mozos.gestionar_comentarios(mesa_id)
        return jsonify({"success": True, "data": comentarios})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mozos/mesas/<mesa_id>/comentarios', methods=['POST'])
def agregar_comentario_mesa(mesa_id):
    """Agrega un comentario a una mesa."""
    try:
        data = request.get_json()
        mensaje = data.get('mensaje')
        cliente = data.get('cliente')
        
        if not mensaje or not cliente:
            return jsonify({"success": False, "error": "Se requiere mensaje y cliente"}), 400
        
        resultado = sistema_pedidos_mozos.agregar_comentario(mesa_id, mensaje, cliente)
        if resultado:
            return jsonify({"success": True, "message": "Comentario agregado exitosamente"})
        return jsonify({"success": False, "error": "No se pudo agregar el comentario"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Rutas para la interfaz de mozos
@app.route('/api/mozos/mapa-mesas')
def obtener_mapa_mesas():
    """Obtiene el mapa de mesas para la vista de mozos."""
    try:
        mesas = sistema_mesas.obtener_mesas()
        return jsonify({
            "success": True,
            "data": [
                {
                    "id": mesa_id,
                    "nombre": mesa[0]['nombre'],
                    "estado": mesa[0]['estado']
                }
                for mesa_id, mesa in sistema_mesas.mesas.items()
            ]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mozos/mesas/<mesa_id>')
def obtener_detalles_mesa(mesa_id):
    """Obtiene los detalles de una mesa específica."""
    try:
        detalles = sistema_pedidos_mozos.visualizador._mostrar_detalles_mesa(mesa_id)
        return jsonify({"success": True, "mesa": detalles})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mozos/pedidos-listos')
def obtener_pedidos_listos():
    """Obtiene los pedidos listos para entregar."""
    try:
        pedidos = sistema_pedidos_mozos._obtener_pedidos_listos_para_entregar()
        return jsonify({"success": True, "pedidos": pedidos})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mozos/pedidos/<pedido_id>/entregar', methods=['POST'])
def marcar_pedido_entregado_mozos(pedido_id):
    """Marca un pedido como entregado."""
    try:
        data = request.get_json()
        mesa_id = data.get('mesa_id')
        cliente = data.get('cliente')
        success = sistema_pedidos_mozos._marcar_pedido_entregado(mesa_id, cliente, pedido_id)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mozos/comentarios-pendientes')
def obtener_comentarios_pendientes():
    """Obtiene los comentarios pendientes."""
    try:
        comentarios = sistema_pedidos_mozos._obtener_comentarios_pendientes()
        return jsonify({"success": True, "comentarios": comentarios})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mozos/comentarios/<mesa_id>/realizar', methods=['POST'])
def marcar_comentario_realizado(mesa_id):
    """Marca un comentario como realizado."""
    try:
        data = request.get_json()
        cliente = data.get('cliente')
        texto = data.get('texto')
        
        if not cliente or not texto:
            return jsonify({
                'success': False,
                'error': 'Se requiere cliente y texto del comentario'
            }), 400

        success = sistema_pedidos_mozos._marcar_comentario_realizado(mesa_id, cliente, texto)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Comentario marcado como realizado',
                'data': {
                    'cliente': cliente,
                    'texto': texto,
                    'hora': datetime.now().strftime("%H:%M hs")
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo marcar el comentario como realizado'
            }), 400

    except Exception as e:
        print(f"Error en marcar_comentario_realizado: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mozos/solicitudes/<mesa_id>/realizar', methods=['POST'])
def marcar_solicitud_realizada(mesa_id):
    """Marca una solicitud como realizada."""
    try:
        data = request.get_json()
        cliente = data.get('cliente')
        mensaje = data.get('mensaje')
        success = sistema_pedidos_mozos._marcar_solicitud_realizada(mesa_id, cliente, mensaje)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mozos/mesas-ocupadas')
def obtener_mesas_ocupadas():
    """Obtiene las mesas ocupadas para reiniciar."""
    try:
        mesas = [(mid, m[0]) for mid, m in sistema_pedidos_mozos.sistema_mesas.mesas.items() if m[0]['estado'] == 'ocupada']
        return jsonify({"success": True, "mesas": [{"id": mid, "nombre": m['nombre'], "estado": m['estado']} for mid, m in mesas]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mozos/mesas/<mesa_id>/reiniciar', methods=['POST'])
def reiniciar_mesa(mesa_id):
    """Reinicia una mesa específica."""
    try:
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({"success": False, "error": "Mesa no encontrada"}), 404

        mesa = mesa_data[0]
        
        # Limpiar todos los datos de la mesa
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            if cliente_key in mesa:
                mesa[cliente_key] = {
                    'nombre': '',
                    'pedidos': [],
                    'contador_pedidos': 0
                }
        
        # Limpiar comentarios al camarero
        if 'comentarios_camarero' in mesa:
            mesa['comentarios_camarero'] = []
            
        # Limpiar notificaciones
        if 'notificaciones' in mesa:
            mesa['notificaciones'] = []
            
        # Reiniciar estado de la mesa
        mesa['estado'] = 'libre'
        
        # Guardar los cambios
        sistema_mesas.guardar_mesas()
        
        return jsonify({
            "success": True,
            "message": "Mesa reiniciada exitosamente"
        })
    except Exception as e:
        print(f"Error en reiniciar_mesa: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Rutas para la interfaz de cocina
@app.route('/api/cocina/mapa-mesas')
def obtener_mapa_mesas_cocina():
    """Obtiene el mapa de mesas para la vista de cocina."""
    try:
        mesas = sistema_mesas.obtener_mesas()
        return jsonify({
            'success': True,
            'data': [
                {
                    "id": mesa_id,
                    "nombre": mesa[0]['nombre'],
                    "estado": mesa[0]['estado']
                }
                for mesa_id, mesa in sistema_mesas.mesas.items()
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cocina/mesas/<mesa_id>')
def obtener_detalles_mesa_cocina(mesa_id):
    """Obtiene los detalles de una mesa específica para la cocina."""
    try:
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({
                'success': False,
                'error': 'Mesa no encontrada'
            }), 404

        mesa = mesa_data[0]
        detalles = {
            'id': mesa_id,
            'nombre': mesa['nombre'],
            'estado': mesa['estado'],
            'capacidad': mesa.get('capacidad', 0),
            'pedidos_en_cocina': [],
            'pedidos_entregados': [],
            'clientes': []
        }

        # Procesar clientes y sus pedidos
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                cliente_info = {
                    'nombre': cliente['nombre'],
                    'pedidos_en_cocina': [],
                    'pedidos_entregados': []
                }
                
                for pedido in cliente.get('pedidos', []):
                    pedido_info = {
                        'id': pedido.get('id'),
                        'nombre': pedido.get('nombre', 'Desconocido'),
                        'cantidad': pedido.get('cantidad', 1),
                        'estado_cocina': pedido.get('estado_cocina', '🟡 Pendiente en cocina'),
                        'hora_envio': pedido.get('hora_envio', ''),
                        'notas': pedido.get('notas', []),
                        'retraso_minutos': pedido.get('retraso_minutos', 0),
                        'historial_estados': pedido.get('historial_estados', [])
                    }
                    
                    if pedido.get('en_cocina', False) and not pedido.get('entregado', False):
                        cliente_info['pedidos_en_cocina'].append(pedido_info)
                        detalles['pedidos_en_cocina'].append(pedido_info)
                    elif pedido.get('entregado', False):
                        cliente_info['pedidos_entregados'].append(pedido_info)
                        detalles['pedidos_entregados'].append(pedido_info)
                
                detalles['clientes'].append(cliente_info)

        # Agregar comentarios al camarero si existen
        if 'comentarios_camarero' in mesa:
            detalles['comentarios_camarero'] = [
                {
                    'cliente': comentario.get('cliente', 'Cliente'),
                    'mensaje': comentario.get('mensaje', ''),
                    'hora': comentario.get('hora', ''),
                    'resuelto': comentario.get('resuelto', False)
                }
                for comentario in mesa['comentarios_camarero']
            ]

        return jsonify({
            'success': True,
            'data': detalles
        })
    except Exception as e:
        print(f"Error en obtener_detalles_mesa_cocina: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cocina/pedidos-activos')
def obtener_pedidos_activos_cocina():
    """Obtiene los pedidos activos en la cocina."""
    try:
        pedidos = sistema_pedidos_cocina.mostrar_pedidos_activos()
        return jsonify({
            'success': True,
            'data': pedidos if pedidos else [],
            'message': 'No hay pedidos activos' if not pedidos else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cocina/pedidos/<pedido_id>')
def obtener_detalles_pedido_cocina(pedido_id):
    """Obtiene los detalles de un pedido específico."""
    try:
        # Buscar el pedido en todas las mesas
        for mesa_id, mesa_data in sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            for i in range(1, mesa.get('capacidad', 0) + 1):
                cliente_key = f"cliente_{i}"
                cliente = mesa.get(cliente_key)
                if cliente and cliente.get('nombre'):
                    for pedido in cliente.get('pedidos', []):
                        if pedido.get('id') == pedido_id:
                            detalles = {
                                'id': pedido.get('id'),
                                'mesa_id': mesa_id,
                                'cliente': cliente['nombre'],
                                'nombre': pedido.get('nombre', 'Desconocido'),
                                'cantidad': pedido.get('cantidad', 1),
                                'estado_cocina': pedido.get('estado_cocina', '🟡 Pendiente en cocina'),
                                'hora_envio': pedido.get('hora_envio', ''),
                                'notas': pedido.get('notas', []),
                                'retraso_minutos': pedido.get('retraso_minutos', 0),
                                'historial_estados': pedido.get('historial_estados', [])
                            }
                            return jsonify({
                                'success': True,
                                'data': detalles
                            })
        
        return jsonify({
            'success': False,
            'error': 'Pedido no encontrado'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mesas/<mesa_id>/resumen')
def obtener_resumen_mesa(mesa_id):
    """Obtiene el resumen de pedidos de una mesa."""
    try:
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({'error': 'Mesa no encontrada'}), 404

        mesa = mesa_data[0]  # Accedemos al primer elemento del array
        resumen = []
        total = 0
        solicitudes_camarero = []

        # Procesar pedidos y solicitudes por cliente
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                pedidos_cliente = []
                subtotal_cliente = 0
                
                # Procesar pedidos del cliente
                for pedido in cliente.get('pedidos', []):
                    if pedido.get('estado_cocina') not in ['🔴 CANCELADO']:
                        pedidos_cliente.append({
                            'id': pedido.get('id'),
                            'nombre': pedido.get('nombre', 'Desconocido'),
                            'cantidad': pedido.get('cantidad', 1),
                            'precio': pedido.get('precio', 0),
                            'notas': pedido.get('notas', []),
                            'estado_cocina': pedido.get('estado_cocina', '🟡 Pendiente'),
                            'en_cocina': pedido.get('en_cocina', False),
                            'hora_envio': pedido.get('hora_envio', ''),
                            'entregado': pedido.get('entregado', False)
                        })
                        subtotal_cliente += pedido.get('precio', 0) * pedido.get('cantidad', 1)
                
                if pedidos_cliente:
                    resumen.append({
                        'nombre': cliente['nombre'],
                        'pedidos': pedidos_cliente,
                        'subtotal': subtotal_cliente
                    })
                    total += subtotal_cliente

        # Procesar solicitudes al camarero
        if 'comentarios_camarero' in mesa:
            solicitudes_pendientes = [c for c in mesa['comentarios_camarero'] 
                                    if not c.get('resuelto', False)]
            if solicitudes_pendientes:
                solicitudes_camarero = [{
                    'cliente': s.get('cliente', 'Cliente'),
                    'mensaje': s.get('mensaje', ''),
                    'hora': s.get('hora', '')
                } for s in solicitudes_pendientes]

        return jsonify({
            'success': True,
            'resumen': resumen,
            'total': total,
            'solicitudes_camarero': solicitudes_camarero
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mesas/<mesa_id>/enviar-cocina', methods=['POST'])
def enviar_pedidos_cocina(mesa_id):
    """Envía los pedidos pendientes a cocina."""
    try:
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({'error': 'Mesa no encontrada'}), 404

        mesa = mesa_data[0]  # Accedemos al primer elemento del array
        pedidos_enviados = []
        tiene_pedidos_nuevos = False

        # Preservar los comentarios existentes
        comentarios_existentes = mesa.get('comentarios_camarero', [])

        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    if not pedido.get('en_cocina', False):
                        tiene_pedidos_nuevos = True
                        pedido['en_cocina'] = True
                        pedido['hora_envio'] = datetime.now().strftime("%H:%M hs")
                        pedido['estado_cocina'] = '🟡 Pendiente en cocina'
                        pedidos_enviados.append(f"{pedido.get('cantidad', 1)} x {pedido.get('nombre', 'Desconocido')} ({cliente['nombre']})")

        if not tiene_pedidos_nuevos:
            return jsonify({'error': 'No hay nuevos pedidos para enviar a cocina'}), 400

        # Restaurar los comentarios después de procesar los pedidos
        mesa['comentarios_camarero'] = comentarios_existentes

        # Guardar los cambios
        sistema_mesas.guardar_mesas()

        # Obtener el resumen actualizado
        resumen = []
        total = 0
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                pedidos_cliente = []
                subtotal_cliente = 0
                for pedido in cliente.get('pedidos', []):
                    if pedido.get('estado_cocina') not in ['🔴 CANCELADO']:
                        pedidos_cliente.append({
                            'id': pedido.get('id'),
                            'nombre': pedido.get('nombre', 'Desconocido'),
                            'cantidad': pedido.get('cantidad', 1),
                            'precio': pedido.get('precio', 0),
                            'notas': pedido.get('notas', []),
                            'estado_cocina': pedido.get('estado_cocina', '🟡 Pendiente en cocina'),
                            'en_cocina': pedido.get('en_cocina', False),
                            'hora_envio': pedido.get('hora_envio', '')
                        })
                        subtotal_cliente += pedido.get('precio', 0) * pedido.get('cantidad', 1)
                
                if pedidos_cliente:
                    resumen.append({
                        'nombre': cliente['nombre'],
                        'pedidos': pedidos_cliente,
                        'total': subtotal_cliente
                    })
                    total += subtotal_cliente

        return jsonify({
            'success': True,
            'mensaje': 'Pedidos enviados a cocina exitosamente',
            'pedidos': pedidos_enviados,
            'resumen': resumen,
            'total': total
        })

    except Exception as e:
        print(f"Error en enviar_pedidos_cocina: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mesas/<mesa_id>/pedidos-pendientes')
def obtener_pedidos_pendientes(mesa_id):
    """Obtiene los pedidos pendientes de una mesa."""
    try:
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({'error': 'Mesa no encontrada'}), 404

        mesa = mesa_data[0]  # Accedemos al primer elemento del array
        pedidos_pendientes = []
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    if not pedido.get('entregado', False):
                        pedidos_pendientes.append({
                            'id': pedido.get('id'),
                            'cliente': cliente['nombre'],
                            'nombre': pedido.get('nombre', 'Desconocido'),
                            'cantidad': pedido.get('cantidad', 1),
                            'notas': pedido.get('notas', []),
                            'estado': pedido.get('estado_cocina', '🟡 Pendiente')
                        })

        return jsonify({
            'success': True,
            'pedidos': pedidos_pendientes
        })

    except Exception as e:
        print(f"Error en obtener_pedidos_pendientes: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mesas/<mesa_id>/llamar-camarero', methods=['POST'])
def llamar_camarero(mesa_id):
    """Registra una solicitud de camarero para una mesa."""
    try:
        data = request.get_json()
        mensaje = data.get('mensaje')
        cliente_key = data.get('cliente_key')
        
        if not mensaje or not cliente_key:
            return jsonify({
                'success': False,
                'error': 'Se requiere mensaje y cliente_key'
            }), 400

        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({
                'success': False,
                'error': 'Mesa no encontrada'
            }), 404

        mesa = mesa_data[0]  # Accedemos al primer elemento del array
        cliente = mesa.get(cliente_key)
        if not cliente or not cliente.get('nombre'):
            return jsonify({
                'success': False,
                'error': 'Cliente no encontrado en la mesa'
            }), 404

        # Crear el comentario
        comentario = {
            'mensaje': mensaje,
            'hora': datetime.now().strftime("%H:%M hs"),
            'resuelto': False,
            'cliente': cliente['nombre']
        }

        # Agregar el comentario a la mesa
        if 'comentarios_camarero' not in mesa:
            mesa['comentarios_camarero'] = []
        mesa['comentarios_camarero'].append(comentario)

        # Guardar los cambios
        sistema_mesas.guardar_mesas()

        return jsonify({
            'success': True,
            'message': 'Solicitud enviada al camarero',
            'data': {
                'mensaje': mensaje,
                'hora': comentario['hora'],
                'cliente': cliente['nombre']
            }
        })

    except Exception as e:
        print(f"Error en llamar_camarero: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pedidos/<pedido_id>/cancelar', methods=['POST'])
def cancelar_pedido(pedido_id):
    """Cancela un pedido específico."""
    try:
        # Obtener todas las mesas
        mesas = sistema_mesas.mesas
        
        # Buscar el pedido en todas las mesas
        for mesa_id, mesa_data in mesas.items():
            mesa = mesa_data[0]  # Accedemos al primer elemento del array
            for i in range(1, mesa.get('capacidad', 0) + 1):
                cliente_key = f"cliente_{i}"
                cliente = mesa.get(cliente_key)
                if cliente and 'pedidos' in cliente:
                    for pedido in cliente['pedidos']:
                        if pedido['id'] == pedido_id:
                            # Verificar que el pedido no esté en cocina
                            if pedido.get('en_cocina', False):
                                return jsonify({
                                    "success": False,
                                    "error": "No se puede cancelar un pedido que ya está en cocina"
                                }), 400
                            
                            # Eliminar el pedido
                            cliente['pedidos'].remove(pedido)
                            sistema_mesas.guardar_mesas()
                            return jsonify({
                                "success": True,
                                "message": "Pedido cancelado exitosamente"
                            })
        
        return jsonify({
            "success": False,
            "error": "Pedido no encontrado"
        }), 404

    except Exception as e:
        print(f"Error en cancelar_pedido: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/pedidos/<pedido_id>/nota', methods=['POST'])
def agregar_nota_pedido(pedido_id):
    """Agrega una nota a un pedido específico."""
    try:
        data = request.get_json()
        nota_texto = data.get('nota')
        
        if not nota_texto:
            return jsonify({
                "success": False,
                "error": "Se requiere el texto de la nota"
            }), 400

        # Obtener todas las mesas
        mesas = sistema_mesas.mesas
        
        # Buscar el pedido en todas las mesas
        for mesa_id, mesa_data in mesas.items():
            mesa = mesa_data[0]  # Accedemos al primer elemento del array
            for i in range(1, mesa.get('capacidad', 0) + 1):
                cliente_key = f"cliente_{i}"
                cliente = mesa.get(cliente_key)
                if cliente and 'pedidos' in cliente:
                    for pedido in cliente['pedidos']:
                        if pedido['id'] == pedido_id:
                            # Crear la nota con timestamp
                            nota = {
                                'texto': nota_texto,
                                'hora': datetime.now().strftime("%H:%M hs")
                            }
                            
                            # Inicializar el array de notas si no existe
                            if 'notas' not in pedido:
                                pedido['notas'] = []
                            
                            # Agregar la nota
                            pedido['notas'].append(nota)
                            sistema_mesas.guardar_mesas()
                            
                            return jsonify({
                                "success": True,
                                "message": "Nota agregada exitosamente",
                                "data": nota
                            })
        
        return jsonify({
            "success": False,
            "error": "Pedido no encontrado"
        }), 404

    except Exception as e:
        print(f"Error en agregar_nota_pedido: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)

