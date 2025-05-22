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

## Estructura de Directorios

```
data/
├── historial_pagos/     # Historial de pagos realizados
│   └── historial.json   # Registro de todos los pagos
├── tickets/            # Tickets generados por cada pago
└── mesas.json         # Estado actual de las mesas
```

## Flujo de Datos

### 1. Gestión de Mesas

#### Estados de Mesa
- **libre**: Mesa disponible para nuevos clientes
- **ocupada**: Mesa con clientes activos
- **reservada**: Mesa con reserva confirmada

#### Estructura de Mesa
```json
{
  "nombre": "Mesa 1",
  "qr_url": "https://turestaurante.com/menu/mesa-1",
  "capacidad": 2,
  "estado": "libre",
  "comentarios_camarero": [],
  "notificaciones": [],
  "cliente_1": {
    "nombre": "",
    "pedidos": [],
    "contador_pedidos": 0
  },
  "cliente_2": {
    "nombre": "",
    "pedidos": [],
    "contador_pedidos": 0
  }
}
```

### 2. Gestión de Pedidos

#### Estados de Pedido
- **preparar**: 🟢 PREPARAR AHORA
- **normal**: 🟡 NORMAL
- **cancelado**: 🔴 CANCELADO
- **agregado**: 🔵 AGREGADO
- **en_preparacion**: 👨‍🍳 EN PREPARACIÓN
- **listo**: ✅ LISTO PARA ENTREGAR
- **entregado**: 🍽️ ENTREGADO

#### Estructura de Pedido
```json
{
  "id": "unique_id",
  "nombre": "Nombre del Plato",
  "cantidad": 1,
  "precio": 1000,
  "notas": [
    {
      "texto": "Sin sal",
      "hora": "12:00"
    }
  ],
  "estado_cocina": "en_preparacion",
  "entregado": false,
  "es_bebida": false
}
```

### 3. Sistema de Pagos

#### Tipos de Pago
- **individual**: Pago por cliente específico
- **grupal**: Pago para toda la mesa

#### Métodos de Pago
- **efectivo**: Pago en efectivo
- **tarjeta**: Pago con tarjeta

#### Flujo de Pago
1. Cliente solicita pago
2. Sistema verifica pedidos entregados
3. Sistema genera ticket
4. Mozo confirma pago
5. Sistema limpia mesa según tipo de pago

### 4. Sistema de Notificaciones

#### Tipos de Notificación
- **general**: Notificaciones generales de la mesa
- **pedido**: Notificaciones relacionadas con pedidos
- **pago**: Notificaciones relacionadas con pagos

#### Estructura de Notificación
```json
{
  "mensaje": "Texto de la notificación",
  "hora": "HH:MM hs",
  "tipo": "general"
}
```

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
- **Respuesta**: Mensaje indicando que el pago será procesado por el mozo

#### Confirmar pago (Mozo)
- **POST** `/api/mozos/pagos/<mesa_id>/confirmar`
- **Body**:
```json
{
    "cliente": "Juan Pérez",
    "tipo_pago": "individual",
    "metodo_pago": "efectivo",
    "total": 1500
}
```
- **Acciones**:
  - Genera ticket en formato texto
  - Guarda historial del pago
  - Limpia la mesa según tipo de pago
  - Marca pedidos como pagados

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

## Formato de Tickets

Los tickets se generan en formato texto (.txt) con la siguiente estructura:
```
========================================
           TICKET DE PAGO
========================================

Mesa: [Número de Mesa]
Fecha: [DD/MM/YYYY HH:MM]
----------------------------------------

Clientes:
- [Nombre Cliente 1]
- [Nombre Cliente 2]

DETALLE DE PEDIDOS:
----------------------------------------
[Cantidad]x [Nombre Producto]
   Precio unitario: $[Precio]
   Subtotal: $[Subtotal]

----------------------------------------
TOTAL A PAGAR: $[Total]
Método de pago: [Efectivo/Tarjeta]
========================================
¡Gracias por su visita!
========================================
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