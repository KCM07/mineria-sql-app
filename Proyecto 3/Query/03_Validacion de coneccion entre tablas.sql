-- ========================================
-- VERIFICAR RELACIONES / INTEGRIDAD REFERENCIAL
-- Si no devuelve filas, las relaciones están correctas
-- ========================================

USE mineria_operaciones;

SELECT p.*
FROM preparacion_minerales p
LEFT JOIN dim_procesos d ON p.id_proceso = d.id_proceso
WHERE d.id_proceso IS NULL;

SELECT e.*
FROM extraccion_metales e
LEFT JOIN dim_procesos d ON e.id_proceso = d.id_proceso
WHERE d.id_proceso IS NULL;

SELECT r.*
FROM refinacion_metales r
LEFT JOIN dim_procesos d ON r.id_proceso = d.id_proceso
WHERE d.id_proceso IS NULL;

##Eso significa: hay errores de relación todos los id_proceso en extraccion_metales existen en dim_procesos, 
## Tus tablas están bien conectadas
## Tu base de datos tiene integridad referencial correcta