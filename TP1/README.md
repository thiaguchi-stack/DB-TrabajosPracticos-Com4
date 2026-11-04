# TP N.º 1 — Del dominio al esquema (Food Store)

**Asignatura:** Base de Datos I · Tecnicatura Universitaria en Programación (UTN)
**Proyecto integrador:** Food Store
**Motor:** PostgreSQL 17+ · **Cliente:** DBeaver / psql
**Integrantes:** Guillot Tiago, Monardez Maximo, Ruiz Matias, Mendez Joaquin, Oviedo Thiago y Chacon Facundo

Modelo entidad-relación, derivación al modelo relacional, normalización hasta 3FN/BCNF y DDL del esquema inicial de Food Store.

## Estructura

```
TP1/
├── README.md
├── TP1_FoodStore_ModeloER_Normalizacion_DDL.pdf   Enunciado de cátedra
├── DUIA.md                                        Declaración de Uso de IA
├── diagrama/
│   ├── diagrama_er.dbml                           Diagrama Crow's Foot para dbdiagram.io
│   └── TP1_Diagrama_ER.pdf                        Diagrama exportado (generado)
├── informe/
│   ├── TP1_FoodStore_Desarrollo.md                Desarrollo completo de las Partes 1-3
│   ├── Informe_TP1_Actividades.md                 Informe por actividad
│   ├── Informe_TP1_Actividades.pdf                Informe por actividad (generado)
│   └── generar_informe_actividades.py             Generador del PDF
└── sql/
    └── schema.sql                                 ENTREGABLE: DDL ejecutable (Parte 4)
```

## Entregables y consigna

| Parte | Consigna | Entregable |
|---|---|---|
| 1 (25%) | Modelo entidad-relación | `diagrama/diagrama_er.dbml`, `diagrama/TP1_Diagrama_ER.pdf`, diccionario en `informe/TP1_FoodStore_Desarrollo.md` |
| 2 (20%) | Derivación al modelo relacional | `informe/TP1_FoodStore_Desarrollo.md` (tablas, PK, FK y justificación de la PK compuesta) |
| 3 (25%) | Normalización 1FN → 3FN/BCNF | `informe/TP1_FoodStore_Desarrollo.md` (siete pasos, dependencias funcionales y preguntas de integración) |
| 4 (25%) | DDL en PostgreSQL | `sql/schema.sql` |
| IA | DUIA y flujo de trabajo | `DUIA.md` |

## Reproducción

```powershell
# 1) Crear la base (o reutilizar una vacía)
createdb -U postgres -h localhost foodstore

# 2) Crear el esquema
psql -U postgres -h localhost -d foodstore -f sql/schema.sql

# 3) Verificar tablas, tipos y restricciones
psql -U postgres -h localhost -d foodstore -c "\dt"
psql -U postgres -h localhost -d foodstore -c "\d+ producto"
```

Para regenerar los PDF de este TP:

```powershell
python -m pip install reportlab
python informe/generar_informe_actividades.py
python diagrama/generar_diagrama_er.py
```

## Decisiones de diseño principales

- `linea_pedido` usa **clave primaria compuesta `(pedido_id, producto_id)`**: impone en el motor que un producto no se repita dentro de un pedido.
- El **precio unitario se congela en la línea** (R4): los cambios de precio del producto no alteran ventas ya facturadas.
- **Baja lógica** (`activo`) en `categoria`, `producto` y `cliente` para conservar el historial (R7).
- `subtotal` **no se almacena**: es derivado (`cantidad × precio_unitario`) y almacenarlo violaría 3FN.
- Las FK usan `ON DELETE RESTRICT` (o `CASCADE` solo de pedido a sus líneas) para proteger el historial.

## Verificación

- `schema.sql` se ejecutó completo sobre una base vacía en PostgreSQL 18.6 (compatible con 17) sin errores.
- Se comprobaron claves primarias, `UNIQUE`, `CHECK`, `DEFAULT`, tipos enumerados e índices.
- El detalle paso a paso y las respuestas a las preguntas guía están en `informe/TP1_FoodStore_Desarrollo.md`.
