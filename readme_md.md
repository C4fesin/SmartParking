# 🚗 Smart Parking - Estacionamento Inteligente

![Status do Projeto](https://img.shields.io/badge/Status-Em%20Desenvolvimento-success)
![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1.3-black?logo=flask&logoColor=white)
![Arduino](https://img.shields.io/badge/Arduino-C++-00979D?logo=arduino&logoColor=white)

Um protótipo completo de estacionamento inteligente que demonstra a integração ponta a ponta entre **Hardware (Arduino)**, **Backend (Python/Flask)** e **Frontend (Dashboard Web)**. 

Este projeto acadêmico foi desenvolvido para resolver o problema de monitoramento de vagas e controle de acesso, com aplicação direta em automação, IoT (Internet das Coisas) e sistemas embarcados.

---

## 🎯 Objetivo do Projeto

Desenvolver um sistema de controle e monitoramento onde sensores físicos se comunicam com uma aplicação web em tempo real. O projeto permite:
- Monitoramento individual de vagas (Livre/Ocupada).
- Controle de acesso seguro por meio de uma cancela automatizada (com trava de segurança antiesmagamento).
- Visualização de dados e histórico de eventos em um Dashboard moderno.
- Simulação via software para testes sem a necessidade do hardware conectado.

## 🛠️ Tecnologias e Arquitetura

O projeto é dividido em três camadas principais:

### 1. Hardware (Firmware)
- **Placa:** Arduino Uno
- **Sensores:** Infravermelho (para detecção de veículos na cancela)
- **Atuadores:** Servo Motor SG90 (cancela), Buzzer (alertas sonoros) e LEDs (sinalização visual)
- **Entradas:** Botões físicos simulando os sensores de ocupação das vagas.
- **Comunicação:** Serial (9600 baud) enviando e recebendo strings de comando.

### 2. Backend (Servidor)
- **Linguagem:** Python
- **Framework Web:** Flask (API REST e Servidor Web)
- **Comunicação Serial:** PySerial
- **Concorrência:** Uso de `threading` e `Locks` para garantir leitura serial não-bloqueante simultânea às requisições web.

### 3. Frontend (Dashboard)
- **Tecnologias:** HTML5, CSS3, JavaScript (Fetch API)
- **Design:** Interface responsiva com tema escuro (Dark Theme), otimizada para monitoramento contínuo.
- **Integração:** Consumo assíncrono da API Flask (`/api/status`, `/api/events`).

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- [Python 3.x](https://www.python.org/downloads/) instalado.
- [Arduino IDE](https://www.arduino.cc/en/software) para gravar o código no microcontrolador.

### 1. Configurando o Hardware
1. Abra o arquivo `firmware/estacionamento_inteligente.ino` na Arduino IDE.
2. Monte o circuito conforme o esquema (veja a pasta `/docs`).
3. Conecte o Arduino ao computador e faça o upload do código.
4. Verifique em qual porta o Arduino está conectado (ex: `COM3` no Windows ou `/dev/ttyUSB0` no Linux) e atualize a variável `PORTA_SERIAL` no arquivo `leitura_arduino.py`.

### 2. Configurando o Servidor Python
Abra o terminal na raiz do projeto e instale as dependências:
```bash
pip install -r backend/requirements.txt
```

Inicie o servidor Flask:
```bash
python backend/leitura_arduino.py
```

### 3. Acessando o Dashboard
Com o servidor rodando, abra o navegador e acesse:
```
http://127.0.0.1:5000
```

---

## 📡 Documentação da API (REST)

O servidor expõe endpoints que permitem monitorar e controlar o sistema:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET`  | `/` | Retorna o Dashboard em HTML. |
| `GET`  | `/api/status` | Retorna o estado atual da cancela e das vagas (JSON). |
| `GET`  | `/api/events` | Retorna o histórico de eventos do sistema (JSON). |
| `POST` | `/api/simulate` | Recebe comandos de simulação (`acao`: `ocupar`, `abrir`, etc.) via dashboard. |
| `POST` | `/api/command` | Envia comandos diretos para o hardware via Serial (`CMD,OPEN`, `CMD,CLOSE`). |
| `GET`  | `/health` | Verifica a saúde do servidor e o status da conexão serial. |

---

## 🔒 Segurança e Tratamento de Falhas
- **Hardware:** O Arduino bloqueia o comando de fechar a cancela (`CMD,CLOSE`) caso o sensor infravermelho detecte um veículo sob ela, emitindo o evento `EVENT,CLOSE_BLOCKED`.
- **Software:** O script Python possui mecanismos de auto-reconexão. Se o cabo do Arduino for desconectado, a thread serial aguarda e tenta restabelecer a conexão a cada 5 segundos sem derrubar a API web.

---
*Projeto desenvolvido como portfólio para áreas de Automação, IoT e Engenharia de Software.*