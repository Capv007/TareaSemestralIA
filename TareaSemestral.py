#Jaime Palavecino, Cristian Pinilla

import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import networkx as nx
from itertools import permutations

# Leer el archivo CSV
df = pd.read_csv('LATITUD - LONGITUD CHILE.CSV')

# Convertir las columnas de latitud y longitud a tipos numéricos
df['Latitud (Decimal)'] = pd.to_numeric(df['Latitud (Decimal)'], errors='coerce')
df['Longitud (decimal)'] = pd.to_numeric(df['Longitud (decimal)'], errors='coerce')

# Eliminar filas con datos faltantes
df = df.dropna(subset=['Latitud (Decimal)', 'Longitud (decimal)']).reset_index(drop=True)

# Función para calcular la distancia Haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radio de la Tierra en kilómetros
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distancia = R * c
    return distancia

# Crear un grafo
G = nx.Graph()

# Agregar nodos
for index, row in df.iterrows():
    G.add_node(row['Comuna'], pos=(row['Longitud (decimal)'], row['Latitud (Decimal)']))

# Agregar aristas solo entre ciudades que están a 250 km o menos de distancia
for i in range(len(df)):
    ciudad1 = df.loc[i, 'Comuna']
    lat1 = df.loc[i, 'Latitud (Decimal)']
    lon1 = df.loc[i, 'Longitud (decimal)']
    for j in range(i+1, len(df)):
        ciudad2 = df.loc[j, 'Comuna']
        lat2 = df.loc[j, 'Latitud (Decimal)']
        lon2 = df.loc[j, 'Longitud (decimal)']
        distancia = haversine(lat1, lon1, lat2, lon2)
        if distancia <= 250:
            G.add_edge(ciudad1, ciudad2, weight=distancia)

# Establecer la ciudad de origen como Santiago
origen = 'Santiago'

# Pedir al usuario las ciudades de destino
destinos_input = input("Ingrese las ciudades de destino separadas por comas: ")
destinos = [destino.strip() for destino in destinos_input.split(',')]

# Añadir el origen a la lista de destinos
destinos = [origen] + destinos

# Encontrar el camino más corto que pase por todas las ciudades sin importar el orden
min_distancia_total = float('inf')
mejor_camino_completo = []

for perm in permutations(destinos[1:]):
    camino_completo = [origen]
    distancia_total = 0
    camino_valido = True

    for i in range(len(perm)):
        origen_parcial = camino_completo[-1]
        destino_parcial = perm[i]
        try:
            camino_parcial = nx.dijkstra_path(G, source=origen_parcial, target=destino_parcial, weight='weight')
            distancia_parcial = nx.dijkstra_path_length(G, source=origen_parcial, target=destino_parcial, weight='weight')

            # Evitar duplicar la ciudad de conexión
            if camino_completo:
                camino_parcial = camino_parcial[1:]

            camino_completo.extend(camino_parcial)
            distancia_total += distancia_parcial
        except nx.NetworkXNoPath:
            camino_valido = False
            break

    if camino_valido and distancia_total < min_distancia_total:
        min_distancia_total = distancia_total
        mejor_camino_completo = camino_completo

if mejor_camino_completo:
    print(f"El camino más corto que pasa por todas las ciudades es:")
    print(" -> ".join(mejor_camino_completo))
    print(f"Distancia total: {min_distancia_total:.2f} km")
else:
    print("No se encontró un camino que cumpla con las restricciones establecidas.")
