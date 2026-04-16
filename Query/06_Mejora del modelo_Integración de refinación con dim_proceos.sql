-- Mejora del modelo: integración de refinación con dim_procesos
USE mineria_operaciones;

ALTER TABLE refinacion_metales
ADD COLUMN id_proceso VARCHAR(50);

INSERT INTO dim_procesos (id_proceso, proceso, tipo_proceso)
VALUES 
('REF001', 'Electrorefinación', 'Refinación'),
('REF002', 'Refinación química', 'Refinación'),
('REF003', 'Fundición adicional', 'Refinación');

SET SQL_SAFE_UPDATES = 0;

UPDATE refinacion_metales r
JOIN dim_procesos d 
  ON TRIM(LOWER(r.proceso)) = TRIM(LOWER(d.proceso))
SET r.id_proceso = d.id_proceso;

SET SQL_SAFE_UPDATES = 1;

ALTER TABLE refinacion_metales
ADD CONSTRAINT fk_refinacion_proceso
FOREIGN KEY (id_proceso) REFERENCES dim_procesos(id_proceso);

#--------------vALIDACIÓN 
USE mineria_operaciones;

SELECT proceso, id_proceso
FROM refinacion_metales;
## VALIDACIÓN DE RELACIONES ENTRE TABLAS 
USE mineria_operaciones;

SHOW CREATE TABLE preparacion_minerales;
SHOW CREATE TABLE extraccion_metales;
SHOW CREATE TABLE refinacion_metales;

##VALIDACIÓN DE FUNCIONALIDAD DE RELACIONES 

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

