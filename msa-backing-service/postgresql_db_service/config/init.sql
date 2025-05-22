CREATE SCHEMA IF NOT EXISTS product_service_schema AUTHORIZATION admin_user;
CREATE SCHEMA IF NOT EXISTS order_service_schema AUTHORIZATION admin_user;
CREATE SCHEMA IF NOT EXISTS user_service_schema AUTHORIZATION admin_user;
GRANT ALL ON SCHEMA product_service_schema TO admin_user;
GRANT ALL ON SCHEMA order_service_schema TO admin_user;
GRANT ALL ON SCHEMA user_service_schema TO admin_user;
SET search_path TO product_service_schema;
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
INSERT INTO items (name, description, price, is_active) VALUES
('프리미엄 노트북', '전문가용 고성능 노트북', 1500000.00, TRUE),
('무선 마우스', '인체공학적 디자인의 무선 마우스', 35000.00, TRUE),
('RGB 기계식 키보드', '다채로운 RGB 백라이트 기계식 키보드', 120000.00, FALSE)
ON CONFLICT (id) DO NOTHING;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE product_service_schema.items TO admin_user;
GRANT USAGE, SELECT ON SEQUENCE product_service_schema.items_id_seq TO admin_user;
\echo 'PostgreSQL 초기화 스크립트 실행 완료.'