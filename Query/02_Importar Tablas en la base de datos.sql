
USE mineria_operaciones;

CREATE TABLE dim_procesos (
    id_proceso VARCHAR(50) PRIMARY KEY,
    proceso VARCHAR(100),
    tipo_proceso VARCHAR(50)
);

CREATE TABLE preparacion_minerales (
    id INT PRIMARY KEY,
    fecha DATE,
    id_proceso VARCHAR(50),
    id_encargado VARCHAR(50),
    toneladas_procesadas DECIMAL(10,2),
    porcentaje_recuperacion DECIMAL(5,2),
    tiempo_operacion_horas DECIMAL(10,2),
    consumo_energia_kwh DECIMAL(10,2),
    costo_tonelada_usd DECIMAL(10,2),
    FOREIGN KEY (id_proceso) REFERENCES dim_procesos(id_proceso)
);

CREATE TABLE extraccion_metales (
    id INT PRIMARY KEY,
    fecha DATE,
    id_proceso VARCHAR(50),
    id_encargado VARCHAR(50),
    toneladas_procesadas DECIMAL(10,2),
    porcentaje_extraccion DECIMAL(5,2),
    temperatura_procesos_celcius DECIMAL(10,2),
    consumo_reactivos_kg DECIMAL(10,2),
    costo_operacion_usd DECIMAL(10,2),
    FOREIGN KEY (id_proceso) REFERENCES dim_procesos(id_proceso)
);

CREATE TABLE refinacion_metales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE,
    proceso VARCHAR(100),
    toneladas_procesadas DECIMAL(10,2),
    pureza_inicial_pct DECIMAL(5,2),
    pureza_final_pct DECIMAL(5,2),
    tiempo_refinacion_hrs DECIMAL(10,2),
    consumo_electrico_kwh DECIMAL(10,2),
    costo_total_usd DECIMAL(10,2)
);

SHOW TABLES;