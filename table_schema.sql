CREATE TABLE mZprize (
  prize_id     TINYINT PRIMARY KEY,
  nominal      INT NOT NULL,       
  keterangan   VARCHAR(50) NOT NULL,  
  qty_total    INT NOT NULL,          
  qty_per_box  INT NOT NULL         
);

CREATE TABLE m_operator (
  operator_id  INT IDENTITY PRIMARY KEY,
  nama         VARCHAR(100) NOT NULL
);

CREATE TABLE prod_batch (
  batch_id     INT IDENTITY PRIMARY KEY,
  no_batch     TINYINT NOT NULL UNIQUE,   
  operator_id  INT NOT NULL REFERENCES mst_operator,
  lokasi       VARCHAR(100) NOT NULL,
  produced_at  DATETIME NOT NULL,
  output_box   TINYINT NOT NULL           
);

CREATE TABLE box (
  box_id       INT IDENTITY PRIMARY KEY,
  batch_id     INT NOT NULL REFERENCES prod_batch,
  no_box       TINYINT NOT NULL UNIQUE, 
  jumlah_kupon SMALLINT NOT NULL DEFAULT 1000
);

CREATE TABLE coupon (
  no_kupon     CHAR(5) PRIMARY KEY
               CHECK (no_kupon BETWEEN '00001' AND '10000'),
  prize_id     TINYINT NOT NULL REFERENCES mst_prize,
  box_id       INT NOT NULL REFERENCES box
);
CREATE INDEX ix_coupon_box ON coupon(box_id, prize_id);

INSERT INTO m_operator (nama) VALUES ('Amir'), ('Nando');