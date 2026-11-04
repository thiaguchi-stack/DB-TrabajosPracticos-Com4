-- ============================================================================
-- Food Store - seed minimo para reproducir las pruebas del TP2
-- Base de trabajo: foodstore_tp2 (copia creada desde foodstore)
-- Ejecutar DESPUES de TP1/sql/schema.sql sobre una base vacia.
--
-- Mantiene el estado base que esperan los escenarios de concurrencia:
--   categoria 1 = Pizzas (1 producto), categoria 2 = Bebidas
--   producto 1 = Muzzarella, stock 20
--   producto 2 = Coca 1.5L, precio 800.00, stock 50
--   cliente 1 = Ana Gomez (activa)
--   pedido 1 con dos lineas (Muzzarella y Coca)
--   sync_deadlock lista para coordinar el escenario 4 (aviso = FALSE)
-- ============================================================================

BEGIN;

-- Deja la copia en el estado base exacto (IDs 1..n) y permite reejecutar el seed.
TRUNCATE linea_pedido, pedido, producto, cliente, categoria RESTART IDENTITY CASCADE;

INSERT INTO categoria (nombre) VALUES
  ('Pizzas'),
  ('Bebidas');

INSERT INTO producto (categoria_id, nombre, descripcion, precio, stock, activo) VALUES
  (1, 'Muzzarella', 'Pizza clasica de muzzarella', 1050.00, 20, TRUE),
  (2, 'Coca 1.5L',  'Gaseosa de 1.5 litros',       800.00, 50, TRUE);

INSERT INTO cliente (nombre, apellido, email, telefono, activo) VALUES
  ('Ana', 'Gomez', 'ana@mail.com', '1155550001', TRUE);

INSERT INTO pedido (cliente_id, fecha, forma_pago) VALUES
  (1, now(), 'EFECTIVO');

INSERT INTO linea_pedido (pedido_id, producto_id, cantidad, precio_unitario) VALUES
  (1, 1, 2, 1000.00),
  (1, 2, 1,  800.00);

-- Tabla auxiliar del escenario 4: A espera a que B avise que bloqueo producto 2.
CREATE TABLE IF NOT EXISTS sync_deadlock (
  id integer PRIMARY KEY,
  aviso boolean NOT NULL DEFAULT FALSE
);
INSERT INTO sync_deadlock (id, aviso) VALUES (1, FALSE)
ON CONFLICT (id) DO UPDATE SET aviso = EXCLUDED.aviso;

COMMIT;

SELECT 'seed minimo cargado' AS estado;
SELECT p.id AS producto, p.nombre, p.precio, p.stock, p.activo
FROM producto p
ORDER BY p.id;
