DROP TABLE IF EXISTS  validacion;

CREATE TABLE validacion (
    [codigo] INTEGER PRIMARY KEY,
    [empresa] STRING  NOT NULL,
    [actividad] STRING NOT NULL,
    [nombre] STRING NOT NULL,
    [edad] INTEGER NOT NULL,
    [dni] INTEGER  NOT NULL,
    [fecha_permiso] INTEGER NOT NULL, 
    [riesgo] STRING NOT NULL
    
); 