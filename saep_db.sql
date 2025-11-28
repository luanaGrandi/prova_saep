-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS saep_db;
USE saep_db;

CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL
);


CREATE TABLE IF NOT EXISTS produto (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL,
    quantidade_estoque INT DEFAULT 0,
    estoque_min INT DEFAULT 0
);


CREATE TABLE IF NOT EXISTS movimentacao (
    id_movimentacao INT AUTO_INCREMENT PRIMARY KEY,
    tipo_movimentacao ENUM('entrada','saida') NOT NULL,
    quantidade INT NOT NULL,
    data_movimentacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT NOT NULL,
    id_produto INT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_produto) REFERENCES produto(id_produto)
);



-- Inserir usuários
INSERT INTO usuario (nome, email, senha) VALUES
('João Silva', 'joao@email.com', 'senha123'),
('Maria Oliveira', 'maria@email.com', 'senha123');

-- Inserir produtos
INSERT INTO produto (nome, descricao, preco, quantidade_estoque, estoque_min) VALUES
('Notebook Dell', 'Notebook Dell i5 8GB RAM 256GB SSD', 3500.00, 10, 2),
('Smartphone Samsung', 'Samsung Galaxy S21 128GB', 2800.00, 15, 5);

-- Inserir movimentações
INSERT INTO movimentacao (tipo_movimentacao, quantidade, id_usuario, id_produto) VALUES
('entrada', 5, 1, 1),
('saida', 2, 2, 2),
('entrada', 3, 1, 2);


SELECT * FROM usuario;
SELECT * FROM produto;
SELECT * FROM movimentacao;
