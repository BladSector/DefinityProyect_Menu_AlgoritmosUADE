# API del Sistema de Restaurante

Esta API proporciona endpoints para gestionar un sistema de restaurante, incluyendo mesas, pedidos, menú y pagos.

## Requisitos

- Python 3.8+
- Flask
- Flask-CORS
- python-dotenv

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python app.py
```

El servidor se ejecutará en `http://127.0.0.1:5000`

## Endpoints

### Mesas

#### Obtener todas las mesas
- **GET** `/api/mesas`
- **Respuesta**: Lista de todas las mesas disponibles

#### Obtener una mesa específica
- **GET** `/api/mesas/<mesa_id>`
- **Respuesta**: Información de la mesa especificada

#### Ocupar una mesa
- **POST** `/api/mesas/<mesa_id>/ocupar`
- **Body**:
```json
{
    "clientes": [
        {
            "nombre": "Juan Pérez"
        },
        {
            "nombre": "María García"
        }
    ]
}
```

#### Agregar cliente a una mesa
- **POST** `/api/mesas/<mesa_id>/agregar-cliente`
- **Body**:
```json
{
    "nombre": "Carlos Rodríguez"
}
```

### Pedidos

#### Obtener pedidos de una mesa
- **GET** `/api/mesas/<mesa_id>/pedidos`
- **Respuesta**: Lista de pedidos de la mesa

#### Realizar un pedido
- **POST** `/api/mesas/<mesa_id>/clientes/<cliente_key>/pedidos`
- **Body**:
```json
{
    "plato_id": "1"
}
```

### Menú

#### Obtener menú completo
- **GET** `/api/menu`
- **Respuesta**: Lista completa del menú

#### Obtener categorías
- **GET** `/api/menu/categorias`
- **Respuesta**: Lista de categorías disponibles

#### Obtener dietas
- **GET** `/api/menu/dietas`
- **Respuesta**: Lista de dietas disponibles

### Pagos

#### Procesar pago
- **POST** `/api/mesas/<mesa_id>/clientes/<cliente_key>/pagar`
- **Body**:
```json
{
    "tipo_pago": "individual",
    "metodo_pago": "efectivo"
}
```

### Cocina

#### Obtener pedidos activos
- **GET** `/api/cocina/pedidos`
- **Respuesta**: Lista de pedidos activos en cocina

#### Actualizar estado de pedido
- **PUT** `/api/cocina/pedidos/<pedido_id>/estado`
- **Body**:
```json
{
    "estado": "en_preparacion"
}
```

### Mozos

#### Obtener mapa de mesas
- **GET** `/api/mozos/mesas`
- **Respuesta**: Mapa de mesas para mozos

#### Marcar pedido como entregado
- **PUT** `/api/mozos/pedidos/<pedido_id>/entregar`

#### Obtener comentarios de mesa
- **GET** `/api/mozos/mesas/<mesa_id>/comentarios`
- **Respuesta**: Lista de comentarios de la mesa

#### Agregar comentario a mesa
- **POST** `/api/mozos/mesas/<mesa_id>/comentarios`
- **Body**:
```json
{
    "mensaje": "Necesito más pan",
    "cliente": "Juan Pérez"
}
```

## Respuestas

Todas las respuestas siguen el formato:
```json
{
    "success": true/false,
    "data": {...} // o "message": "..." en caso de éxito
    "error": "..." // en caso de error
}
```

## Códigos de Estado

- 200: Éxito
- 400: Error en la solicitud
- 404: Recurso no encontrado
- 500: Error interno del servidor 