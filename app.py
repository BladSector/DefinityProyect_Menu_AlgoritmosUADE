import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template, session
from funciones.sistema_mesas import SistemaMesas
from funciones.sistema_pedidos_clientes import SistemaPedidosClientes
from funciones.sistema_pedidos_cocina import SistemaPedidosCocina
from funciones.sistema_pedidos_mozos import SistemaPedidosMozos
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.secret_key = 'definity_proyect_secret_key'  # Clave secreta para la sesión (Seguridad)

# ------------------------------Inicializar sistemas------------------------------
sistema_mesas = SistemaMesas()
sistema_pedidos_clientes = SistemaPedidosClientes(sistema_mesas)
sistema_pedidos_mozos = SistemaPedidosMozos(sistema_mesas)
sistema_pedidos_cocina = SistemaPedidosCocina(sistema_mesas)

# ------------------------------Rutas para vistas------------------------------
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

# ------------------------------Obtener mesas general (Clientes)------------------------------
@app.route('/api/mesas', methods=['GET'])
def obtener_mesas():
    """Obtiene todas las mesas disponibles."""
    try:
        mesas = sistema_mesas.obtener_mesas()
        return jsonify({"success": True, "data": mesas})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
# ------------------------------Obtener mesa específica (Clientes)------------------------------
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
            
# ------------------------------Acceder a una mesa (Clientes)------------------------------
@app.route('/api/mesas/acceder', methods=['POST'])
def acceder_mesa():
    """Accede a una mesa usando la URL del QR y el nombre del cliente."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos def acceder_mesa"}), 400
            
        qr_url = data.get('qr_url')
        nombre = data.get('nombre')
        
        if not qr_url or not nombre:
            return jsonify({"success": False, "error": "Se requiere URL del QR y nombre del cliente. Intentar de nuevo"}), 400
        
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

# ------------------------------Obtiene el menú completo (Clientes)------------------------------
@app.route('/api/menu', methods=['GET'])
def obtener_menu():
    """Obtiene el menú completo."""
    try:
        menu = sistema_mesas.mostrar_menu_completo()
        return jsonify({"success": True, "data": menu})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ------------------------------Obtiene las categorías disponibles del menú (Clientes)------------------------------
@app.route('/api/menu/categorias', methods=['GET'])
def obtener_categorias():
    """Obtiene las categorías disponibles del menú."""
    try:
        categorias = sistema_mesas.filtrar_por_categoria()
        return jsonify({"success": True, "data": categorias})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
def _normalizar_categoria(categoria):
    """Normaliza el nombre de la categoría para comparación."""
    categoria_normalizada = categoria.lower().replace('/', ' ').strip()
    print(f"Normalizando categoría: '{categoria}' -> '{categoria_normalizada}'")
    return categoria_normalizada
    
# ------------------------------Obtiene los platos de una categoría específica (Clientes)------------------------------
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

# ------------------------------Obtiene las dietas disponibles del menú (Clientes)------------------------------
@app.route('/api/menu/dietas', methods=['GET'])
def obtener_dietas():
    """Obtiene las dietas disponibles del menú."""
    try:
        dietas = sistema_mesas.obtener_dietas_disponibles()
        return jsonify({"success": True, "data": dietas})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ------------------------------Obtiene los platos de una dieta específica (Clientes)------------------------------
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

# ------------------------------Hacer pedido (Clientes)------------------------------
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
    
# ------------------------------Obtiene los pedidos pendientes de una mesa para cancelar (Clientes)------------------------------
@app.route('/api/mesas/<mesa_id>/pedidos-pendientes')
def obtener_pedidos_pendientes(mesa_id):
    """Obtiene los pedidos pendientes de una mesa."""
    try:
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({
                'success': False,
                'error': 'Mesa no encontrada'
            }), 404

        mesa = mesa_data[0]
        pedidos_pendientes = []

        # Procesar pedidos de cada cliente
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    if not pedido.get('en_cocina', False) and not pedido.get('entregado', False):
                        pedidos_pendientes.append({
                            'id': pedido['id'],
                            'cliente': cliente['nombre'],
                            'nombre': pedido['nombre'],
                            'cantidad': pedido['cantidad'],
                            'precio': pedido['precio'],
                            'hora': pedido.get('hora', '')
                        })

        return jsonify({
            'success': True,
            'pedidos': pedidos_pendientes
        })

    except Exception as e:
        print(f"Error en obtener_pedidos_pendientes: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
# ------------------------------Cancelar un pedido (Clientes)------------------------------
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
    
# ------------------------------Obtiene el resumen de pedidos de una mesa (Clientes)------------------------------
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

# ------------------------------Envía los pedidos pendientes de una mesa a cocina (Clientes)------------------------------
@app.route('/api/mesas/<mesa_id>/enviar-cocina', methods=['POST'])
def enviar_pedidos_cocina(mesa_id):
    """Envía los pedidos pendientes de una mesa a cocina."""
    try:
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({
                'success': False,
                'error': 'Mesa no encontrada'
            }), 404

        mesa = mesa_data[0]
        pedidos_enviados = []
        timestamp = datetime.now().strftime("%H:%M hs")

        # Procesar pedidos de cada cliente
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    if not pedido.get('en_cocina', False) and not pedido.get('entregado', False):
                        pedido['en_cocina'] = True
                        pedido['hora_envio'] = timestamp
                        pedido['estado_cocina'] = '🟡 Pendiente en cocina'
                        pedidos_enviados.append({
                            'id': pedido['id'],
                            'cliente': cliente['nombre'],
                            'nombre': pedido['nombre'],
                            'cantidad': pedido['cantidad']
                        })

        if not pedidos_enviados:
            return jsonify({
                'success': False,
                'error': 'No hay pedidos pendientes para enviar a cocina'
            }), 400

        # Guardar los cambios
        sistema_mesas.guardar_mesas()

        return jsonify({
            'success': True,
            'message': 'Pedidos enviados a cocina exitosamente',
            'data': {
                'pedidos': pedidos_enviados,
                'hora_envio': timestamp
            }
        })

    except Exception as e:
        print(f"Error en enviar_pedidos_cocina: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
# ------------------------------Agregar comentario a una mesa (Clientes)------------------------------
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
    
# ------------------------------Llamar al camarero (Clientes)------------------------------
@app.route('/api/mesas/<mesa_id>/llamar-camarero', methods=['POST'])
def llamar_camarero(mesa_id):
    """Agrega una solicitud al camarero para una mesa específica."""
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

        mesa = mesa_data[0]
        cliente = mesa.get(cliente_key)
        if not cliente or not cliente.get('nombre'):
            return jsonify({
                'success': False,
                'error': 'Cliente no encontrado en la mesa'
            }), 404

        # Crear la solicitud al camarero
        solicitud = {
            'cliente': cliente['nombre'],
            'mensaje': mensaje,
            'hora': datetime.now().strftime("%H:%M hs"),
            'resuelto': False
        }

        # Agregar la solicitud a la lista de comentarios del camarero
        if 'comentarios_camarero' not in mesa:
            mesa['comentarios_camarero'] = []
        mesa['comentarios_camarero'].append(solicitud)

        # Guardar los cambios
        sistema_mesas.guardar_mesas()

        return jsonify({
            'success': True,
            'message': 'Solicitud enviada al camarero',
            'data': solicitud
        })

    except Exception as e:
        print(f"Error en llamar_camarero: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



# ------------------------------Obtiene el mapa de mesas (Mozos)------------------------------
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

# ------------------------------Obtiene los detalles de una mesa específica (Mozos)------------------------------
@app.route('/api/mozos/mesas/<mesa_id>')
def obtener_detalles_mesa(mesa_id):
    """Obtiene los detalles de una mesa específica para la vista de mozos."""
    try:
        mesa_data = sistema_pedidos_mozos.sistema_mesas.mesas.get(mesa_id)
        if not mesa_data:
            return jsonify({"success": False, "error": "Mesa no encontrada"}), 404

        mesa = mesa_data[0]
        detalles = {
            "id": mesa_id,
            "nombre": mesa['nombre'],
            "estado": mesa['estado'],
            "capacidad": mesa.get('capacidad', 0),
            "pedidos_en_cocina": [],
            "pedidos_entregados": [],
            "comentarios_camarero": []
        }

        # Procesar pedidos y comentarios
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    pedido_info = {
                        "id": pedido.get('id'),
                        "cliente": cliente['nombre'],
                        "nombre": pedido.get('nombre'),
                        "cantidad": pedido.get('cantidad', 1),
                        "estado_cocina": pedido.get('estado_cocina'),
                        "hora_envio": pedido.get('hora_envio'),
                        "notas": pedido.get('notas', []),
                        "entregado": pedido.get('entregado', False)
                    }
                    
                    if pedido.get('en_cocina', False) and not pedido.get('entregado', False):
                        detalles['pedidos_en_cocina'].append(pedido_info)
                    elif pedido.get('entregado', False) or pedido.get('estado_cocina') == '✅ LISTO PARA ENTREGAR':
                        detalles['pedidos_entregados'].append(pedido_info)

        # Procesar comentarios del camarero
        if 'comentarios_camarero' in mesa:
            detalles['comentarios_camarero'] = mesa['comentarios_camarero']

        return jsonify({"success": True, "data": detalles})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ------------------------------Obtiene los pedidos listos para entregar (Mozos)------------------------------
@app.route('/api/mozos/pedidos-listos')
def obtener_pedidos_listos():
    """Obtiene los pedidos listos para entregar."""
    try:
        pedidos = sistema_pedidos_mozos._obtener_pedidos_listos_para_entregar()
        return jsonify({"success": True, "pedidos": pedidos})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ------------------------------Obtiene los comentarios pendientes (Mozos)------------------------------
@app.route('/api/mozos/comentarios-pendientes')
def obtener_comentarios_pendientes():
    """Obtiene los comentarios pendientes."""
    try:
        comentarios = sistema_pedidos_mozos._obtener_comentarios_pendientes()
        return jsonify({"success": True, "comentarios": comentarios})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ------------------------------Marca un comentario como realizado (Mozos)------------------------------
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

# ------------------------------Marca un pedido como entregado (Mozos)------------------------------
@app.route('/api/mozos/pedidos/<pedido_id>/entregar', methods=['PUT'])
def marcar_pedido_entregado(pedido_id):
    """Marca un pedido como entregado."""
    try:
        data = request.get_json()
        mesa_id = data.get('mesa_id')
        cliente = data.get('cliente')
        
        if not mesa_id or not cliente:
            return jsonify({
                'success': False,
                'error': 'Se requiere mesa_id y cliente'
            }), 400

        success = sistema_pedidos_mozos.marcar_pedido_entregado(mesa_id, pedido_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Pedido marcado como entregado'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo marcar el pedido como entregado'
            }), 400

    except Exception as e:
        print(f"Error en marcar_pedido_entregado: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ------------------------------Obtiene las mesas ocupadas para reiniciar (Mozos)------------------------------
@app.route('/api/mozos/mesas-ocupadas')
def obtener_mesas_ocupadas():
    """Obtiene las mesas ocupadas para reiniciar."""
    try:
        mesas = [(mid, m[0]) for mid, m in sistema_pedidos_mozos.sistema_mesas.mesas.items() if m[0]['estado'] == 'ocupada']
        return jsonify({"success": True, "mesas": [{"id": mid, "nombre": m['nombre'], "estado": m['estado']} for mid, m in mesas]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ------------------------------Reiniciar una mesa (Mozos)------------------------------
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

# ------------------------------Obtiene el mapa de mesas (Cocina)------------------------------
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

# ------------------------------Obtiene los detalles de una mesa específica (Cocina)------------------------------
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

# ------------------------------Actualiza el estado de un pedido (Cocina)------------------------------
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

# ------------------------------Obtiene los pedidos activos en la cocina (Cocina)------------------------------
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

# ------------------------------Obtiene los detalles de un pedido específico (Cocina)------------------------------
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





# ------------------------------Obtiene la cuenta de la mesa para pagar (Clientes)------------------------------
@app.route('/api/clientes/cuenta', methods=['GET'])
def obtener_cuenta():
    """
    Obtiene el detalle de la cuenta para un cliente específico o para toda la mesa.
    
    Proceso:
    1. Verifica si hay una mesa seleccionada en la sesión
    2. Obtiene los datos de la mesa
    3. Calcula los totales:
       - Total individual: solo los pedidos del cliente actual
       - Total grupal: todos los pedidos de todos los clientes
       - Pedidos por cliente: desglose de lo que debe cada cliente
    4. Detecta si hay un solo cliente para ajustar las opciones de pago
    
    Returns:
        JSON con:
        - total_individual: monto a pagar por el cliente actual
        - total_grupal: monto total de toda la mesa
        - pedidos_por_cliente: diccionario con el total por cada cliente
        - opciones_pago: configuración de las opciones de pago disponibles
    """
    try:
        # Obtener la mesa actual del cliente
        mesa_id = session.get('mesa_id')
        if not mesa_id:
            return jsonify({'success': False, 'error': 'No hay mesa seleccionada'})

        # Obtener los datos de la mesa
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({'success': False, 'error': 'Mesa no encontrada'})

        mesa = mesa_data[0]  # Accedemos al primer elemento del array
        cliente_key = session.get('cliente_key')

        # Calcular totales
        total_individual = 0
        total_grupal = 0
        pedidos_por_cliente = {}
        clientes_activos = 0

        # Iterar sobre los clientes de la mesa
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key_actual = f"cliente_{i}"
            cliente = mesa.get(cliente_key_actual)
            if cliente and cliente.get('nombre'):
                clientes_activos += 1
                total_cliente = 0
                # Solo sumar pedidos que ya fueron entregados
                for pedido in cliente.get('pedidos', []):
                    if pedido.get('entregado'):
                        total_cliente += pedido['precio'] * pedido['cantidad']
                pedidos_por_cliente[cliente['nombre']] = total_cliente
                total_grupal += total_cliente

                # Si es el cliente actual, actualizar el total individual
                if cliente_key_actual == cliente_key:
                    total_individual = total_cliente

        # Configurar opciones de pago según el número de clientes
        opciones_pago = {
            'tipo_pago': {
                'individual': True,
                'grupal': clientes_activos > 1
            },
            'metodo_pago': {
                'efectivo': True,
                'tarjeta': True
            }
        }

        return jsonify({
            'success': True,
            'total_individual': total_individual,
            'total_grupal': total_grupal,
            'pedidos_por_cliente': pedidos_por_cliente,
            'opciones_pago': opciones_pago,
            'clientes_activos': clientes_activos
        })

    except Exception as e:
        print(f"Error en obtener_cuenta: {str(e)}")  # Agregamos log para debug
        return jsonify({'success': False, 'error': str(e)})

# ------------------------------Procesa el pago (Clientes)------------------------------
@app.route('/api/clientes/pagar', methods=['POST'])
def procesar_pago():
    """
    Procesa el pago de una mesa, ya sea individual o grupal.
    
    Proceso:
    1. Verifica los datos de la mesa y el cliente
    2. Valida que todos los pedidos estén entregados
    3. Verifica que no haya un pago pendiente previo
    4. Crea un ticket con:
       - Información de la mesa
       - Fecha y hora
       - Tipo de pago (individual/grupal)
       - Método de pago (efectivo/tarjeta)
       - Total a pagar
       - Detalle de pedidos
    5. Guarda el ticket en el historial
    6. Notifica a los mozos sobre el pago pendiente
    
    Returns:
        JSON con:
        - success: true/false
        - message: mensaje informativo para el cliente
    """
    try:
        data = request.get_json()
        mesa_id = session.get('mesa_id')
        if not mesa_id:
            return jsonify({'success': False, 'error': 'No hay mesa seleccionada'})

        # Obtener los datos de la mesa
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({'success': False, 'error': 'Mesa no encontrada'})

        mesa = mesa_data[0]  # Accedemos al primer elemento del array

        # Verificar si ya existe un pago pendiente para esta mesa
        if hasattr(sistema_pedidos_mozos, 'pagos_pendientes'):
            for pago in sistema_pedidos_mozos.pagos_pendientes:
                if pago['mesa_id'] == mesa_id:
                    return jsonify({
                        'success': False,
                        'error': 'Ya existe una solicitud de pago pendiente para esta mesa. Por favor, espere al mozo.'
                    }), 400

        # Verificar que todos los pedidos estén entregados
        pedidos_pendientes = []
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    if not pedido.get('entregado', False):
                        pedidos_pendientes.append({
                            'cliente': cliente['nombre'],
                            'pedido': pedido['nombre']
                        })

        if pedidos_pendientes:
            return jsonify({
                'success': False,
                'error': 'No se puede procesar el pago porque hay pedidos pendientes de entrega',
                'pedidos_pendientes': pedidos_pendientes
            }), 400

        # Crear el ticket con la información básica
        ticket = {
            'mesa_id': mesa_id,
            'mesa_nombre': mesa['nombre'],
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tipo_pago': data['tipo_pago'],
            'metodo_pago': data['metodo_pago'],
            'total': data['total'],
            'pedidos': []
        }

        # Agregar los pedidos al ticket
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    if pedido.get('entregado'):
                        ticket['pedidos'].append({
                            'cliente': cliente['nombre'],
                            'nombre': pedido['nombre'],
                            'cantidad': pedido['cantidad'],
                            'precio': pedido['precio'],
                            'subtotal': pedido['precio'] * pedido['cantidad']
                        })

        # Guardar el ticket en el historial
        if not hasattr(sistema_pedidos_mozos, 'historial_tickets'):
            sistema_pedidos_mozos.historial_tickets = []
        sistema_pedidos_mozos.historial_tickets.append(ticket)

        # Notificar a los mozos
        if not hasattr(sistema_pedidos_mozos, 'pagos_pendientes'):
            sistema_pedidos_mozos.pagos_pendientes = []
        
        # Obtener el nombre del cliente para el pago individual
        cliente_nombre = None
        if data['tipo_pago'] == 'individual':
            cliente_key = session.get('cliente_key')
            cliente = mesa.get(cliente_key)
            if cliente:
                cliente_nombre = cliente.get('nombre')
        
        # Agregar el pago a la lista de pendientes
        sistema_pedidos_mozos.pagos_pendientes.append({
            'mesa_id': mesa_id,
            'mesa_nombre': mesa['nombre'],
            'cliente': cliente_nombre if data['tipo_pago'] == 'individual' else 'Grupal',
            'tipo_pago': data['tipo_pago'],
            'metodo_pago': data['metodo_pago'],
            'total': data['total'],
            'hora_solicitud': datetime.now().strftime('%H:%M:%S')
        })

        return jsonify({
            'success': True,
            'message': 'Su pago será realizado, espere al mozo'
        })

    except Exception as e:
        print(f"Error en procesar_pago: {str(e)}")  # Agregamos log para debug
        return jsonify({'success': False, 'error': str(e)})
    
# ------------------------------Procesar pago (Clientes)------------------------------
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
    

# ------------------------------Obtiene los pagos pendientes (Mozos)------------------------------
@app.route('/api/mozos/pagos-pendientes', methods=['GET'])
def obtener_pagos_pendientes():
    """
    Obtiene la lista de pagos pendientes para que los mozos los procesen.
    
    Proceso:
    1. Verifica si existe la lista de pagos pendientes
    2. Retorna todos los pagos que están esperando ser confirmados
    
    Returns:
        JSON con:
        - success: true/false
        - pagos: lista de pagos pendientes con:
          * mesa_id
          * mesa_nombre
          * cliente
          * tipo_pago
          * metodo_pago
          * total
          * hora_solicitud
    """
    try:
        if not hasattr(sistema_pedidos_mozos, 'pagos_pendientes'):
            sistema_pedidos_mozos.pagos_pendientes = []
        
        return jsonify({
            'success': True,
            'pagos': sistema_pedidos_mozos.pagos_pendientes
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ------------------------------Confirma el pago (Mozos)------------------------------
@app.route('/api/mozos/pagos/<mesa_id>/confirmar', methods=['POST'])
def confirmar_pago(mesa_id):
    """
    Confirma que un pago ha sido recibido por los mozos.
    
    Proceso:
    1. Obtiene los datos del pago del request
    2. Llama al sistema de mozos para confirmar el pago
    3. El sistema:
       - Crea y guarda el ticket
       - Marca los pedidos como pagados
       - Elimina el pago de la lista de pendientes
    
    Returns:
        JSON con:
        - success: true/false
        - message: mensaje de éxito o error
    """
    try:
        data = request.get_json()
        cliente = data.get('cliente')
        tipo_pago = data.get('tipo_pago')
        metodo_pago = data.get('metodo_pago')
        total = data.get('total')
        
        if not all([cliente, tipo_pago, metodo_pago, total]):
            return jsonify({
                'success': False,
                'error': 'Faltan datos requeridos para confirmar el pago'
            }), 400

        # Confirmar el pago usando el sistema de mozos
        success, message = sistema_pedidos_mozos.confirmar_pago(
            mesa_id, cliente, tipo_pago, metodo_pago, total
        )

        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        print(f"Error en confirmar_pago: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



if __name__ == '__main__':
    app.run(debug=True)


"""
# Por primera vez que se accede a la mesa se ocupa la mesa
@app.route('/api/mesas/<mesa_id>/ocupar', methods=['POST'])
def ocupar_mesa(mesa_id):
    try:
        data = request.get_json()
        clientes = data.get('clientes', [])
        if not clientes:
            return jsonify({"success": False, "error": "Se requiere al menos un cliente"}), 400
        
        # Verificar si la mesa existe
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({"success": False, "error": "Mesa no encontrada"}), 404
            
        # Verificar si la mesa está ocupada
        mesa = mesa_data[0]
        if mesa['estado'] != 'libre':
            return jsonify({
                "success": False, 
                "error": "Mesa ocupada. Por favor, ingrese en una mesa libre"
            }), 400
        
        resultado = sistema_mesas.ocupar_mesa(mesa_id, clientes)
        if resultado:
            return jsonify({"success": True, "message": "Mesa ocupada exitosamente"})
        return jsonify({"success": False, "error": "No se pudo ocupar la mesa"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
"""
"""
# AGREGAR CLIENTE A LA MESA
@app.route('/api/mesas/<mesa_id>/agregar-cliente', methods=['POST'])
def agregar_cliente_mesa(mesa_id):
    try:
        data = request.get_json()
        nombre_cliente = data.get('nombre')
        if not nombre_cliente:
            return jsonify({"success": False, "error": "Se requiere el nombre del cliente"}), 400
        
        # Verificar si la mesa existe
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({"success": False, "error": "Mesa no encontrada"}), 404
            
        mesa = mesa_data[0]
        
        # Verificar si la mesa está ocupada
        if mesa['estado'] != 'ocupada':
            return jsonify({
                "success": False, 
                "error": "La mesa debe estar ocupada para agregar más clientes"
            }), 400
            
        # Verificar si hay espacio disponible
        clientes_actuales = sum(1 for i in range(1, mesa.get('capacidad', 0) + 1) 
                              if mesa.get(f"cliente_{i}", {}).get('nombre'))
        if clientes_actuales >= mesa.get('capacidad', 0):
            return jsonify({
                "success": False,
                "error": "No hay espacio disponible en la mesa"
            }), 400
        
        resultado = sistema_mesas.agregar_cliente_mesa(mesa_id, nombre_cliente)
        if resultado:
            return jsonify({"success": True, "message": "Cliente agregado exitosamente"})
        return jsonify({"success": False, "error": "No se pudo agregar el cliente"}), 400
    except Exception as e:
        print(f"Error al agregar cliente: {str(e)}")  # Para logging
        return jsonify({
            "success": False, 
            "error": "Ocurrió un error inesperado al agregar el cliente. Por favor, intente nuevamente."
        }), 500

# Obtiene los pedidos de una mesa específica.
@app.route('/api/mesas/<mesa_id>/pedidos', methods=['GET'])
def obtener_pedidos_mesa(mesa_id):
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
"""