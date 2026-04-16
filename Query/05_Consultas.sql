### CONSULTAS

# Consulta 1: total de toneladas por proceso
USE mineria_operaciones;

SELECT d.proceso,
       SUM(p.toneladas_procesadas) AS total_toneladas
FROM preparacion_minerales p
JOIN dim_procesos d ON p.id_proceso = d.id_proceso
GROUP BY d.proceso
ORDER BY total_toneladas DESC;

# Consulta 2: costo promedio por proceso
SELECT d.proceso,
       AVG(p.costo_tonelada_usd) AS costo_promedio
FROM preparacion_minerales p
JOIN dim_procesos d ON p.id_proceso = d.id_proceso
GROUP BY d.proceso
ORDER BY costo_promedio DESC;

# Consulta 3: tiempo promedio de operación
SELECT d.proceso,
       AVG(p.tiempo_operacion_horas) AS tiempo_promedio
FROM preparacion_minerales p
JOIN dim_procesos d ON p.id_proceso = d.id_proceso
GROUP BY d.proceso
ORDER BY tiempo_promedio DESC;

# Consulta 4: recuperación vs energía
SELECT fecha,
       id_proceso,
       porcentaje_recuperacion,
       consumo_energia_kwh
FROM preparacion_minerales
ORDER BY porcentaje_recuperacion DESC;

# Consulta 5: extracción vs temperatura
SELECT fecha,
       id_proceso,
       porcentaje_extraccion,
       temperatura_procesos_celcius
FROM extraccion_metales
ORDER BY porcentaje_extraccion DESC;

# Consulta 6: mejora de pureza en refinación
SELECT proceso,
       pureza_inicial_pct,
       pureza_final_pct,
       (pureza_final_pct - pureza_inicial_pct) AS mejora_pureza
FROM refinacion_metales
ORDER BY mejora_pureza DESC;

# Consulta 7: subconsulta - registros por encima del promedio
SELECT *
FROM preparacion_minerales
WHERE toneladas_procesadas > (
    SELECT AVG(toneladas_procesadas)
    FROM preparacion_minerales
);

# Consulta 8: join de reporte operativo
SELECT d.proceso,
       d.tipo_proceso,
       p.fecha,
       p.toneladas_procesadas,
       p.costo_tonelada_usd
FROM preparacion_minerales p
JOIN dim_procesos d ON p.id_proceso = d.id_proceso
ORDER BY p.fecha;

# Consulta 9: máximos, mínimos y promedio por proceso
SELECT d.proceso,
       MAX(p.toneladas_procesadas) AS max_toneladas,
       MIN(p.toneladas_procesadas) AS min_toneladas,
       AVG(p.toneladas_procesadas) AS prom_toneladas
FROM preparacion_minerales p
JOIN dim_procesos d ON p.id_proceso = d.id_proceso
GROUP BY d.proceso;

# Consulta 10: control de calidad de datos
SELECT *
FROM preparacion_minerales
WHERE porcentaje_recuperacion > 100
   OR porcentaje_recuperacion < 0
   OR tiempo_operacion_horas < 0;

SELECT *
FROM extraccion_metales
WHERE porcentaje_extraccion > 100
   OR porcentaje_extraccion < 0
   OR temperatura_procesos_celcius < 0;
   
   # Consulta 11: consumo energético por tonelada
SELECT d.proceso,
       SUM(p.consumo_energia_kwh) / SUM(p.toneladas_procesadas) AS kwh_por_tonelada
FROM preparacion_minerales p
JOIN dim_procesos d ON p.id_proceso = d.id_proceso
GROUP BY d.proceso
ORDER BY kwh_por_tonelada DESC;




   
   