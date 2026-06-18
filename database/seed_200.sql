-- =============================================
-- Saldo Verde — Seed 200 registros para testes
-- =============================================
-- Distribuição: 40 PESSOAS + 20 CLASSIFICACAO + 80 MOVIMENTOCONTAS + 60 PARCELACONTAS = 200
-- PESSOAS   ids 1-40  (1-20 FORNECEDOR, 21-30 CLIENTE, 31-40 FATURADO)
-- CLASSIF. ids 1-20  (1-14 DESPESA, 15-20 RECEITA)
-- MOVIMENT ids 1-80  (1-60 APAGAR, 61-80 ARECEBER)
-- PARCELAS ids 1-60  (movs 1-40 -> 1 parcela cada; movs 41-50 -> 2 parcelas cada)

BEGIN;

-- =============================================
-- PESSOAS (40 linhas)
-- =============================================
INSERT INTO PESSOAS (tipo, razao_social, cpf_cnpj, ativo) VALUES
-- FORNECEDOR (20)
('FORNECEDOR', 'Agro Insumos Norte Ltda',           '11.222.333/0001-01', TRUE),
('FORNECEDOR', 'Sementes do Cerrado SA',             '11.222.333/0001-02', TRUE),
('FORNECEDOR', 'Fertilizantes Brasil Comércio Ltda', '11.222.333/0001-03', TRUE),
('FORNECEDOR', 'Maquinários Agroverde ME',           '11.222.333/0001-04', TRUE),
('FORNECEDOR', 'Defensivos Agropecuários Ltda',      '11.222.333/0001-05', TRUE),
('FORNECEDOR', 'Combustíveis e Lubrificantes JK',    '11.222.333/0001-06', TRUE),
('FORNECEDOR', 'TerraFértil Distribuidora Ltda',     '11.222.333/0001-07', TRUE),
('FORNECEDOR', 'Agrovest Equipamentos SA',           '11.222.333/0001-08', TRUE),
('FORNECEDOR', 'Campo Verde Suprimentos Ltda',       '11.222.333/0001-09', TRUE),
('FORNECEDOR', 'Nutrição Animal Brasil ME',          '11.222.333/0001-10', TRUE),
('FORNECEDOR', 'Irrigação Moderna Ltda',             '22.333.444/0001-01', TRUE),
('FORNECEDOR', 'Sementes Híbridas do Sul SA',        '22.333.444/0001-02', TRUE),
('FORNECEDOR', 'Proteção Vegetal Cerrado Ltda',      '22.333.444/0001-03', TRUE),
('FORNECEDOR', 'Logística Rural Express ME',         '22.333.444/0001-04', TRUE),
('FORNECEDOR', 'Silos e Armazéns Goiás SA',          '22.333.444/0001-05', TRUE),
('FORNECEDOR', 'Energia Solar Agrícola Ltda',        '22.333.444/0001-06', TRUE),
('FORNECEDOR', 'BioDefensivos Naturais SA',          '22.333.444/0001-07', TRUE),
('FORNECEDOR', 'Plásticos Agrícolas Centro-Oeste',   '22.333.444/0001-08', TRUE),
('FORNECEDOR', 'Veterinária Campo Aberto Ltda',      '22.333.444/0001-09', TRUE),
('FORNECEDOR', 'Consultoria Agronômica Verde Ltda',  '22.333.444/0001-10', TRUE),
-- CLIENTE (10)
('CLIENTE', 'Cooperativa Agroverde Goiás',           '33.444.555/0001-01', TRUE),
('CLIENTE', 'Cerealista Central do Brasil Ltda',     '33.444.555/0001-02', TRUE),
('CLIENTE', 'Frigorífico Pantanal SA',               '33.444.555/0001-03', TRUE),
('CLIENTE', 'Grãos do Planalto Comércio ME',         '33.444.555/0001-04', TRUE),
('CLIENTE', 'Atacado Rural Cerrado Ltda',            '33.444.555/0001-05', TRUE),
('CLIENTE', 'Supermercados Naturais SA',             '33.444.555/0001-06', TRUE),
('CLIENTE', 'Exportadora Agro Brasil Ltda',          '33.444.555/0001-07', TRUE),
('CLIENTE', 'Indústria de Alimentos Verde SA',       '33.444.555/0001-08', TRUE),
('CLIENTE', 'Hortifruti Fresco Ltda',               '33.444.555/0001-09', TRUE),
('CLIENTE', 'Mercado Orgânico Central ME',           '33.444.555/0001-10', TRUE),
-- FATURADO (10)
('FATURADO', 'João da Silva',                        '111.222.333-01', TRUE),
('FATURADO', 'Maria Oliveira',                       '111.222.333-02', TRUE),
('FATURADO', 'Carlos Souza',                         '111.222.333-03', TRUE),
('FATURADO', 'Ana Pereira',                          '111.222.333-04', TRUE),
('FATURADO', 'Pedro Almeida',                        '111.222.333-05', TRUE),
('FATURADO', 'Fernanda Costa',                       '111.222.333-06', TRUE),
('FATURADO', 'Ricardo Martins',                      '111.222.333-07', TRUE),
('FATURADO', 'Patrícia Lima',                        '111.222.333-08', TRUE),
('FATURADO', 'Roberto Ferreira',                     '111.222.333-09', TRUE),
('FATURADO', 'Juliana Santos',                       '111.222.333-10', TRUE);

-- =============================================
-- CLASSIFICACAO (20 linhas)
-- =============================================
INSERT INTO CLASSIFICACAO (tipo, descricao, ativo) VALUES
-- DESPESA (14)
('DESPESA', 'Insumos Agrícolas',             TRUE),
('DESPESA', 'Combustível e Lubrificantes',   TRUE),
('DESPESA', 'Manutenção de Equipamentos',    TRUE),
('DESPESA', 'Serviços Terceirizados',        TRUE),
('DESPESA', 'Energia Elétrica',              TRUE),
('DESPESA', 'Transporte e Logística',        TRUE),
('DESPESA', 'Arrendamento de Terra',         TRUE),
('DESPESA', 'Mão de Obra Temporária',        TRUE),
('DESPESA', 'Defensivos Agrícolas',          TRUE),
('DESPESA', 'Sementes e Mudas',              TRUE),
('DESPESA', 'Irrigação',                     TRUE),
('DESPESA', 'Embalagens e Acondicionamento', TRUE),
('DESPESA', 'Seguro Rural',                  TRUE),
('DESPESA', 'Assistência Técnica Agronômica',TRUE),
-- RECEITA (6)
('RECEITA', 'Venda de Grãos',                TRUE),
('RECEITA', 'Venda de Hortaliças',           TRUE),
('RECEITA', 'Venda de Frutas',               TRUE),
('RECEITA', 'Venda de Gado',                 TRUE),
('RECEITA', 'Aluguel de Maquinário',         TRUE),
('RECEITA', 'Venda de Insumos',              TRUE);

-- =============================================
-- MOVIMENTOCONTAS (80 linhas)
-- id_fornecedor: 1-20 (FORNECEDOR)
-- id_faturado:  31-40 (FATURADO)
-- id_classificacao: 1-20
-- =============================================
INSERT INTO MOVIMENTOCONTAS (tipo, id_fornecedor, id_faturado, id_classificacao, valor_total, data_emissao, descricao_itens, numero_nota_fiscal, ativo) VALUES
-- APAGAR (60) -------------------------------------------------------------
('APAGAR',  1,  31,  1,   5800.00, '2024-01-10', 'Compra de Adubo NPK e Fertilizantes', 'NF-000001', TRUE),
('APAGAR',  2,  32,  2,   1250.50, '2024-01-15', 'Abastecimento Frota Óleo Diesel', 'NF-000002', TRUE),
('APAGAR',  3,  33,  3,   3400.00, '2024-01-22', 'Manutenção Preventiva Trator John Deere', 'NF-000003', TRUE),
('APAGAR',  4,  34,  4,   2100.75, '2024-02-03', 'Serviço de Apoio Técnico e Agronômico', 'NF-000004', TRUE),
('APAGAR',  5,  35,  5,    890.00, '2024-02-10', 'Fatura de Energia Elétrica Poço Artesiano', 'NF-000005', TRUE),
('APAGAR',  6,  36,  6,   6750.00, '2024-02-18', 'Frete e Transporte de Cargas e Insumos', 'NF-000006', TRUE),
('APAGAR',  7,  37,  7,  12000.00, '2024-02-25', 'Pagamento Arrendamento Parcial Gleba A', 'NF-000007', TRUE),
('APAGAR',  8,  38,  8,   4300.00, '2024-03-05', 'Diárias Mão de Obra Temporária Colheita', 'NF-000008', TRUE),
('APAGAR',  9,  39,  9,   7800.50, '2024-03-12', 'Compra de Defensivos Agrícolas e Herbicidas', 'NF-000009', TRUE),
('APAGAR', 10,  40, 10,   2200.00, '2024-03-20', 'Aquisição de Sementes Certificadas Milho', 'NF-000010', TRUE),
('APAGAR', 11,  31, 11,   9500.00, '2024-03-28', 'Manutenção Sistema de Irrigação por Pivô', 'NF-000011', TRUE),
('APAGAR', 12,  32, 12,   1800.25, '2024-04-05', 'Compra de Embalagens e Sacarias de Ráfia', 'NF-000012', TRUE),
('APAGAR', 13,  33, 13,   3200.00, '2024-04-12', 'Prêmio Seguro Rural Safra de Inverno', 'NF-000013', TRUE),
('APAGAR', 14,  34, 14,   5600.75, '2024-04-19', 'Consultoria Assistência Técnica Agronômica', 'NF-000014', TRUE),
('APAGAR', 15,  35,  1,   4100.00, '2024-04-26', 'Compra de Adubo Orgânico Fosfatado', 'NF-000015', TRUE),
('APAGAR', 16,  36,  2,   2750.50, '2024-05-03', 'Abastecimento Lubrificantes e Graxas', 'NF-000016', TRUE),
('APAGAR', 17,  37,  3,  11200.00, '2024-05-10', 'Revisão Motor Colheitadeira de Grãos', 'NF-000017', TRUE),
('APAGAR', 18,  38,  4,   6900.00, '2024-05-17', 'Serviço Terceirizado de Aluguel de Drone', 'NF-000018', TRUE),
('APAGAR', 19,  39,  5,   1350.00, '2024-05-24', 'Fatura de Energia Elétrica Galpão Central', 'NF-000019', TRUE),
('APAGAR', 20,  40,  6,   8400.00, '2024-05-31', 'Transporte Rodoviário Escoamento Safra', 'NF-000020', TRUE),
('APAGAR',  1,  31,  7,  15000.00, '2024-06-07', 'Arrendamento Trimestral Pastagem Setor Sul', 'NF-000021', TRUE),
('APAGAR',  2,  32,  8,   3600.00, '2024-06-14', 'Mão de Obra Diarista para Plantio Solo', 'NF-000022', TRUE),
('APAGAR',  3,  33,  9,   2900.25, '2024-06-21', 'Inseticidas e Fungicidas de Proteção', 'NF-000023', TRUE),
('APAGAR',  4,  34, 10,   7200.00, '2024-06-28', 'Sementes de Soja Transgênica Tratada', 'NF-000024', TRUE),
('APAGAR',  5,  35, 11,   4800.50, '2024-07-05', 'Peças e Reparos de Tubulação Irrigação', 'NF-000025', TRUE),
('APAGAR',  6,  36, 12,   1600.00, '2024-07-12', 'Caixas Plásticas e Paletes para Hortifruti', 'NF-000026', TRUE),
('APAGAR',  7,  37, 13,  10500.00, '2024-07-19', 'Seguro de Carga e Maquinário Agrícola', 'NF-000027', TRUE),
('APAGAR',  8,  38, 14,   3100.75, '2024-07-26', 'Laudo Técnico de Análise de Solo', 'NF-000028', TRUE),
('APAGAR',  9,  39,  1,   5400.00, '2024-08-02', 'Calcário Agrícola para Correção de Solo', 'NF-000029', TRUE),
('APAGAR', 10,  40,  2,   2000.00, '2024-08-09', 'Combustível para Gerador de Emergência', 'NF-000030', TRUE),
('APAGAR', 11,  31,  3,   8900.00, '2024-08-16', 'Recondicionamento de Implementos Agrícolas', 'NF-000031', TRUE),
('APAGAR', 12,  32,  4,   4500.25, '2024-08-23', 'Serviço de Topografia e Demarcação Area', 'NF-000032', TRUE),
('APAGAR', 13,  33,  5,   6300.00, '2024-08-30', 'Consumo Elétrico Bombas de Água', 'NF-000033', TRUE),
('APAGAR', 14,  34,  6,   1950.50, '2024-09-06', 'Logística de Distribuição e Entrega', 'NF-000034', TRUE),
('APAGAR', 15,  35,  7,  13500.00, '2024-09-13', 'Arrendamento Gleba B Contrato Anual', 'NF-000035', TRUE),
('APAGAR', 16,  36,  8,   7100.00, '2024-09-20', 'Contratação Chapas Carregamento Grãos', 'NF-000036', TRUE),
('APAGAR', 17,  37,  9,   2800.75, '2024-09-27', 'Defensivos Biológicos Contra Pragas', 'NF-000037', TRUE),
('APAGAR', 18,  38, 10,   5200.00, '2024-10-04', 'Mudas Certificadas de Frutíferas', 'NF-000038', TRUE),
('APAGAR', 19,  39, 11,   3700.00, '2024-10-11', 'Manutenção Aspersores de Campo', 'NF-000039', TRUE),
('APAGAR', 20,  40, 12,   9100.50, '2024-10-18', 'Embalagens Flexíveis para Silagem', 'NF-000040', TRUE),
('APAGAR',  1,  31, 13,   4200.00, '2024-10-25', 'Apólice de Seguro de Vida Trabalhadores', 'NF-000041', TRUE),
('APAGAR',  2,  32, 14,   6700.25, '2024-11-01', 'Planejamento de Rotação de Culturas', 'NF-000042', TRUE),
('APAGAR',  3,  33,  1,  11800.00, '2024-11-08', 'Fertilizantes Nitrogenados Concentrados', 'NF-000043', TRUE),
('APAGAR',  4,  34,  2,   2450.00, '2024-11-15', 'Combustível Caminhão de Distribuição', 'NF-000044', TRUE),
('APAGAR',  5,  35,  3,   8200.75, '2024-11-22', 'Troca de Pneus e Alinhamento Trator', 'NF-000045', TRUE),
('APAGAR',  6,  36,  4,   3900.00, '2024-11-29', 'Serviço de Limpeza e Roçagem Terceirizada', 'NF-000046', TRUE),
('APAGAR',  7,  37,  5,  16000.00, '2024-12-06', 'Consumo Elétrico Estrutura Administrativa', 'NF-000047', TRUE),
('APAGAR',  8,  38,  6,   5100.50, '2024-12-13', 'Frete para Retirada de Maquinários', 'NF-000048', TRUE),
('APAGAR',  9,  39,  7,   2600.00, '2024-12-20', 'Taxa Anual de Uso de Solo Arrendado', 'NF-000049', TRUE),
('APAGAR', 10,  40,  8,   7800.00, '2024-12-27', 'Mão de Obra Coleta Amostras Agronômicas', 'NF-000050', TRUE),
('APAGAR', 11,  31,  9,   4400.25, '2025-01-03', 'Fungicidas Preventivos Safra Nova', 'NF-000051', TRUE),
('APAGAR', 12,  32, 10,   9600.00, '2025-01-10', 'Sementes de Sorgo de Alta Produtividade', 'NF-000052', TRUE),
('APAGAR', 13,  33, 11,   3300.50, '2025-01-17', 'Reparo Emergencial Motobomba D''água', 'NF-000053', TRUE),
('APAGAR', 14,  34, 12,   6100.00, '2025-01-24', 'Filmes Plásticos para Estufas Agrícolas', 'NF-000054', TRUE),
('APAGAR', 15,  35, 13,  12500.00, '2025-02-07', 'Seguro Contra Granizo e Intempéries', 'NF-000055', TRUE),
('APAGAR', 16,  36, 14,   1750.75, '2025-02-14', 'Assessoria em Manejo Integrado Pragas', 'NF-000056', TRUE),
('APAGAR', 17,  37,  1,   8700.00, '2025-03-07', 'Insumos Corretivos de Acidez de Solo', 'NF-000057', TRUE),
('APAGAR', 18,  38,  2,   5500.00, '2025-03-14', 'Óleo Diesel e Filtros de Combustível', 'NF-000058', TRUE),
('APAGAR', 19,  39,  3,   2300.25, '2025-04-04', 'Manutenção Sistema Hidráulico Tratores', 'NF-000059', TRUE),
('APAGAR', 20,  40,  4,  10200.00, '2025-04-11', 'Serviço de Plantio Mecanizado Terceiro', 'NF-000060', TRUE),
-- ARECEBER (20) -----------------------------------------------------------
('ARECEBER',  1, 31, 15,  18000.00, '2024-02-01', 'Venda Lote de Soja em Grãos Comum', 'NF-000061', TRUE),
('ARECEBER',  2, 32, 16,   9500.50, '2024-03-01', 'Venda Lote de Hortaliças Climatizadas', 'NF-000062', TRUE),
('ARECEBER',  3, 33, 17,  24000.00, '2024-04-01', 'Venda de Frutas Cítricas Laranja Lima', 'NF-000063', TRUE),
('ARECEBER',  4, 34, 18,  35000.00, '2024-05-01', 'Venda de Gado de Corte Nelore Engorda', 'NF-000064', TRUE),
('ARECEBER',  5, 35, 19,   8200.00, '2024-06-01', 'Aluguel de Trator com Operador Próprio', 'NF-000065', TRUE),
('ARECEBER',  6, 36, 20,  12500.75, '2024-07-01', 'Repasse de Excedente de Insumos Adubo', 'NF-000066', TRUE),
('ARECEBER',  7, 37, 15,  27000.00, '2024-08-01', 'Venda de Grãos Milho Granel Tipo 1', 'NF-000067', TRUE),
('ARECEBER',  8, 38, 16,  16400.00, '2024-09-01', 'Venda Tomate Italiano Caixa Padrão', 'NF-000068', TRUE),
('ARECEBER',  9, 39, 17,  31000.00, '2024-10-01', 'Venda Safra de Café Arábica Limpo', 'NF-000069', TRUE),
('ARECEBER', 10, 40, 18,  19800.50, '2024-11-01', 'Venda Bezerros Desmamados Raça Pura', 'NF-000070', TRUE),
('ARECEBER', 11, 31, 19,   7600.00, '2024-12-01', 'Locação Temporária Colheitadeira Kombi', 'NF-000071', TRUE),
('ARECEBER', 12, 32, 20,  22500.00, '2025-01-01', 'Venda Defensivos Não Utilizados Sobra', 'NF-000072', TRUE),
('ARECEBER', 13, 33, 15,  14000.25, '2025-01-15', 'Venda Sacaria de Trigo para Moagem', 'NF-000073', TRUE),
('ARECEBER', 14, 34, 16,  41000.00, '2025-02-01', 'Venda Hortaliças Hidropônicas Cooperativa', 'NF-000074', TRUE),
('ARECEBER', 15, 35, 17,  11200.00, '2025-02-15', 'Venda Lote de Melancia Redonda Premium', 'NF-000075', TRUE),
('ARECEBER', 16, 36, 18,  28500.00, '2025-03-01', 'Venda Bovinos Reposição de Rebanho', 'NF-000076', TRUE),
('ARECEBER', 17, 37, 19,   6900.75, '2025-03-15', 'Aluguel de Implementos Arado e Grade', 'NF-000077', TRUE),
('ARECEBER', 18, 38, 20,  33000.00, '2025-04-01', 'Venda Lote de Calcário Não Utilizado', 'NF-000078', TRUE),
('ARECEBER', 19, 39, 15,  17800.00, '2025-05-01', 'Venda de Soja em Grãos Safra Nova', 'NF-000079', TRUE),
('ARECEBER', 20, 40, 16,  25600.00, '2025-06-01', 'Venda de Batata Monalisa Direto Produtor', 'NF-000080', TRUE);

-- =============================================
-- PARCELACONTAS (60 linhas)
-- Movimentos 1-40 : 1 parcela cada (40 linhas)
-- Movimentos 41-50: 2 parcelas cada (20 linhas)
-- Total: 60 linhas
-- =============================================
INSERT INTO PARCELACONTAS (id_movimento, identificacao, data_vencimento, valor, ativo) VALUES
-- 1 parcela por movimento (movs 1-40)
(1,  'MOV1-PARC1',   '2024-02-10',  5800.00, TRUE),
(2,  'MOV2-PARC1',   '2024-02-15',  1250.50, TRUE),
(3,  'MOV3-PARC1',   '2024-02-22',  3400.00, TRUE),
(4,  'MOV4-PARC1',   '2024-03-03',  2100.75, TRUE),
(5,  'MOV5-PARC1',   '2024-03-10',   890.00, TRUE),
(6,  'MOV6-PARC1',   '2024-03-18',  6750.00, TRUE),
(7,  'MOV7-PARC1',   '2024-03-25', 12000.00, TRUE),
(8,  'MOV8-PARC1',   '2024-04-05',  4300.00, TRUE),
(9,  'MOV9-PARC1',   '2024-04-12',  7800.50, TRUE),
(10, 'MOV10-PARC1',  '2024-04-20',  2200.00, TRUE),
(11, 'MOV11-PARC1',  '2024-04-28',  9500.00, TRUE),
(12, 'MOV12-PARC1',  '2024-05-05',  1800.25, TRUE),
(13, 'MOV13-PARC1',  '2024-05-12',  3200.00, TRUE),
(14, 'MOV14-PARC1',  '2024-05-19',  5600.75, TRUE),
(15, 'MOV15-PARC1',  '2024-05-26',  4100.00, TRUE),
(16, 'MOV16-PARC1',  '2024-06-03',  2750.50, TRUE),
(17, 'MOV17-PARC1',  '2024-06-10', 11200.00, TRUE),
(18, 'MOV18-PARC1',  '2024-06-17',  6900.00, TRUE),
(19, 'MOV19-PARC1',  '2024-06-24',  1350.00, TRUE),
(20, 'MOV20-PARC1',  '2024-07-01',  8400.00, TRUE),
(21, 'MOV21-PARC1',  '2024-07-07', 15000.00, TRUE),
(22, 'MOV22-PARC1',  '2024-07-14',  3600.00, TRUE),
(23, 'MOV23-PARC1',  '2024-07-21',  2900.25, TRUE),
(24, 'MOV24-PARC1',  '2024-07-28',  7200.00, TRUE),
(25, 'MOV25-PARC1',  '2024-08-05',  4800.50, TRUE),
(26, 'MOV26-PARC1',  '2024-08-12',  1600.00, TRUE),
(27, 'MOV27-PARC1',  '2024-08-19', 10500.00, TRUE),
(28, 'MOV28-PARC1',  '2024-08-26',  3100.75, TRUE),
(29, 'MOV29-PARC1',  '2024-09-02',  5400.00, TRUE),
(30, 'MOV30-PARC1',  '2024-09-09',  2000.00, TRUE),
(31, 'MOV31-PARC1',  '2024-09-16',  8900.00, TRUE),
(32, 'MOV32-PARC1',  '2024-09-23',  4500.25, TRUE),
(33, 'MOV33-PARC1',  '2024-09-30',  6300.00, TRUE),
(34, 'MOV34-PARC1',  '2024-10-06',  1950.50, TRUE),
(35, 'MOV35-PARC1',  '2024-10-13', 13500.00, TRUE),
(36, 'MOV36-PARC1',  '2024-10-20',  7100.00, TRUE),
(37, 'MOV37-PARC1',  '2024-10-27',  2800.75, TRUE),
(38, 'MOV38-PARC1',  '2024-11-04',  5200.00, TRUE),
(39, 'MOV39-PARC1',  '2024-11-11',  3700.00, TRUE),
(40, 'MOV40-PARC1',  '2024-11-18',  9100.50, TRUE),
-- 2 parcelas por movimento (movs 41-50)
(41, 'MOV41-PARC1',   '2024-11-25',  2100.00, TRUE),
(41, 'MOV41-PARC2',   '2024-12-25',  2100.00, TRUE),
(42, 'MOV42-PARC1',   '2024-12-01',  3350.12, TRUE),
(42, 'MOV42-PARC2',   '2025-01-01',  3350.13, TRUE),
(43, 'MOV43-PARC1',   '2024-12-08',  5900.00, TRUE),
(43, 'MOV43-PARC2',   '2025-01-08',  5900.00, TRUE),
(44, 'MOV44-PARC1',   '2024-12-15',  1225.00, TRUE),
(44, 'MOV44-PARC2',   '2025-01-15',  1225.00, TRUE),
(45, 'MOV45-PARC1',   '2024-12-22',  4100.37, TRUE),
(45, 'MOV45-PARC2',   '2025-01-22',  4100.38, TRUE),
(46, 'MOV46-PARC1',   '2024-12-29',  1950.00, TRUE),
(46, 'MOV46-PARC2',   '2025-01-29',  1950.00, TRUE),
(47, 'MOV47-PARC1',   '2025-01-06',  8000.00, TRUE),
(47, 'MOV47-PARC2',   '2025-02-06',  8000.00, TRUE),
(48, 'MOV48-PARC1',   '2025-01-13',  2550.25, TRUE),
(48, 'MOV48-PARC2',   '2025-02-13',  2550.25, TRUE),
(49, 'MOV49-PARC1',   '2025-01-20',  1300.00, TRUE),
(49, 'MOV49-PARC2',   '2025-02-20',  1000.25, TRUE),
(50, 'MOV50-PARC1',   '2025-01-27',  5100.00, TRUE),
(50, 'MOV50-PARC2',   '2025-02-27',  5100.00, TRUE);

COMMIT;