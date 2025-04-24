from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from funciones.acceso_mesas import SistemaMesas
from funciones.sistema_pedidos_clientes import SistemaPedidosClientes
from funciones.sistema_pedidos_cocina import SistemaPedidosCocina
from funciones.sistema_pedidos_mozos import SistemaPedidosMozos
from datetime import datetime
import json
import os

