# TP N.º 2 — Laboratorio de concurrencia e IA (Food Store)

**Asignatura:** Base de Datos II · Unidad 1: integridad, transacciones y concurrencia
**Proyecto integrador:** Food Store (esquema del TP1)
**Motor:** PostgreSQL 17+ · **Cliente:** psql / DBeaver (dos sesiones concurrentes)
**Base de trabajo:** `foodstore_tp2` (copia; nunca la base real)
**Integrantes:** Guillot Tiago, Monardez Maximo, Ruiz Matias, Mendez Joaquin, Oviedo Thiago y Chacon Facundo

Regla de fondo del TP: **se delega la escritura, nunca la decisión**. Todo script se lee, se prueba sobre una copia dentro de una transacción y se defiende antes de darlo por bueno.

## Estructura

```
TP2/
├── README.md
├── TP2_Entrega_Completa.pdf                 Entrega compilada (Partes 0-3)
├── protocolo_seguridad.md                   ENTREGABLE Parte 0
├── DUIA_parte1.md                           Declaración de Uso de IA - integridad
├── DUIA_parte2.md                           Declaración de Uso de IA - concurrencia
├── DUIA_parte3.md                           Declaración de Uso de IA - lectura crítica
├── specs/
│   └── spec_restricciones.md                Spec escrita antes del script (Parte 1)
├── sql/
│   ├── 00_seed_minimo.sql                   Datos base reejecutables + sync_deadlock
│   ├── restricciones_integridad.sql         ENTREGABLE: 3 funciones + 3 triggers
│   └── pruebas_restricciones.sql            Pruebas válidas/inválidas en una transacción
├── concurrencia/
│   ├── escenario1_no_repetible/             READ COMMITTED vs REPEATABLE READ
│   ├── escenario2_fantasma/                 Lectura fantasma
│   ├── escenario3_bloqueo/                  Espera por bloqueo FOR UPDATE
│   └── escenario4_interbloqueo/             Deadlock real (40P01)
└── informe/
    ├── informe_concurrencia.md              Informe técnico de los 4 escenarios
    ├── ejercicio_lectura_critica.md         Análisis y corrección de los 2 scripts peligrosos
    ├── Informe_TP2_Actividades.md           Informe por actividad
    ├── Informe_TP2_Actividades.pdf          Informe por actividad (generado)
    └── generar_informe_actividades.py       Generador del PDF
```

## Entregables y consigna

| Parte | Consigna | Entregable |
|---|---|---|
| 0 | Protocolo de seguridad adaptado al entorno | `protocolo_seguridad.md` |
| 1 | Reglas de negocio garantizadas en el motor (triggers) + DUIA | `specs/spec_restricciones.md`, `sql/restricciones_integridad.sql`, `sql/pruebas_restricciones.sql`, `DUIA_parte1.md` |
| 2 | Mínimo tres escenarios de concurrencia verificados en el motor + informe + DUIA | `concurrencia/`, `informe/informe_concurrencia.md`, `DUIA_parte2.md` |
| 3 | Lectura crítica de dos scripts peligrosos (UPDATE sin WHERE y NOT IN con NULL) + DUIA | `informe/ejercicio_lectura_critica.md`, `DUIA_parte3.md` |

## Reproducción

Requisitos: `psql` en el PATH, PostgreSQL 17+ y `PGPASSWORD` definida.

```powershell
$env:PGPASSWORD = "tu_password"

# 1) Crear la copia de trabajo (elegir UNA opcion)
# Opcion A: desde cero con el esquema del TP1
createdb -U postgres -h localhost foodstore_tp2
psql -U postgres -h localhost -d foodstore_tp2 -f ../TP1/sql/schema.sql

# Opcion B: copiando una base foodstore ya existente
# createdb -U postgres -h localhost -T foodstore foodstore_tp2

# 2) Datos base. Es reejecutable: trunca, reinicia IDs y deja sync_deadlock lista.
psql -U postgres -h localhost -d foodstore_tp2 -f sql/00_seed_minimo.sql

# 3) Restricciones y pruebas (el script aplica el DDL y hace ROLLBACK al final)
Push-Location sql
psql -U postgres -h localhost -d foodstore_tp2 -f pruebas_restricciones.sql
Pop-Location

# 4) Escenarios de concurrencia
.\concurrencia\escenario1_no_repetible\run1.ps1
.\concurrencia\escenario1_no_repetible\run1_rr.ps1
.\concurrencia\escenario2_fantasma\run2.ps1 -sA sA_rc.sql
.\concurrencia\escenario2_fantasma\run2.ps1 -sA sA_rr.sql
.\concurrencia\escenario3_bloqueo\run3.ps1
.\concurrencia\escenario4_interbloqueo\run4.ps1
```

Cada orquestador acepta `-Db`, `-DbUser` y `-DbHost`; por defecto usa `foodstore_tp2`, `postgres` y `localhost`. Las contraseñas no se escriben en los scripts: se leen de `PGPASSWORD`. Antes de lanzar las sesiones, cada orquestador restaura su condición inicial: precio 800 en el escenario 1, sin `Fugazzeta` en el 2 y `sync_deadlock.aviso = FALSE` en el 4. Así los escenarios se pueden repetir sin limpiar la base a mano.

## Restricciones garantizadas en el motor

| Trigger | Regla | Tabla |
|---|---|---|
| `trg_chk_activo_cliente_pedido` | Un cliente inactivo no genera pedidos nuevos | `pedido` |
| `trg_chk_activo_producto_linea` | Un producto inactivo no se vende en líneas nuevas | `linea_pedido` |
| `trg_chk_stock_linea` | La cantidad vendida no supera el stock disponible | `linea_pedido` |

## Escenarios de concurrencia

| Escenario | Fenómeno | Nivel donde aparece | Solución verificada |
|---|---|---|---|
| 1 | Lectura no repetible | `READ COMMITTED` | `REPEATABLE READ` (snapshot único) |
| 2 | Lectura fantasma | `READ COMMITTED` | `REPEATABLE READ` |
| 3 | Espera por bloqueo (`FOR UPDATE`) | cualquier nivel | `COMMIT` de la sesión bloqueante |
| 4 | Interbloqueo (SQLSTATE 40P01) | orden cruzado de bloqueos | orden consistente + transacciones cortas |

La evidencia real del motor está en `concurrencia/*/salida_*.txt`; el análisis completo, en `informe/informe_concurrencia.md`.

## Verificación

- Los tres triggers se probaron con casos válidos e inválidos dentro de `BEGIN ... ROLLBACK`.
- Los cuatro escenarios se ejecutaron con dos sesiones `psql` concurrentes y sus salidas quedaron versionadas.
- Cada script generado por IA fue leído línea por línea antes de aplicarse (ver las tres DUIA).
