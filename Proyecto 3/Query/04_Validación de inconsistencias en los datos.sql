### control de calidad
# buscamos Ver si hay: porcentajes > 100  , valores negativos, datos raros  
USE mineria_operaciones;

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