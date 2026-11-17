# Arquitetura do Sistema — Smart Parking

## 1. Visão Geral das Camadas

O sistema é estruturado em quatro camadas desacopladas:

1. **Camada Física (Hardware e Firmware):**
   * Composta por **Arduino Uno**, sensor reflexivo infravermelho **TCRT5000**, micro servo motor **MG90S**, 3 botões táteis, LEDs indicadores e buzzer (`firmware/estacionamento_inteligente/estacionamento_inteligente.ino`).
   * *Status:* Montagem inicial realizada em protoboard; integração serial bidirecional e estabilidade dos atuadores/sensores **pendentes de validação física**.

2. **Backend (API REST, Serial e Fila de Eventos):**
   * Desenvolvido em **Python** com **Flask**, **PySerial**, `threading` e `queue` (`backend/leitura_arduino.py`).
   * Gerencia o estado consolidado do estacionamento em memória, expõe endpoints REST para o frontend, mantém uma *thread* de reconexão serial e enfileira eventos para integração externa.

3. **Frontend (Dashboard Web e Simulador):**
   * Interface em **HTML, CSS e JavaScript** (`frontend/templates/index.html`) que consulta `/api/status` e `/api/events` a cada 1 segundo e permite acionar eventos sintéticos via `/api/simulate`.

4. **Integração Externa (Make e Google Sheets):**
   * Pipeline em nuvem (`Python/Flask → Webhook Make → Google Sheets`) alimentado por uma *thread* dedicada (`processar_fila_make`) que envia payloads JSON em UTF-8 via HTTP `POST`.
   * *Status:* **Implementada e testada** com eventos gerados pelo simulador web.

---

## 2. Fluxo Validado vs. Fluxo Pendente

### Fluxo Validado (Operação via Simulador Web)

```text
[Dashboard Web / Simulador]
        │  POST /api/simulate
        ▼
[Backend Python / Flask] ──► Atualiza estado e histórico local (deque)
        │  put_nowait(evento)
        ▼
[Fila em Memória (Queue) + Thread Make]
        │  HTTP POST (JSON / UTF-8)
        ▼
[Webhook Make] ──► [Planilha Google Sheets]
```

* **Comportamento comprovado:** A rota `/api/simulate` altera o estado internamente no backend para testar o dashboard e o pipeline em nuvem (sem enviar dados pela porta serial). Eventos de alteração de vaga (`VAGA`), estado da cancela (`CANCELA`) e detecção de veículo (`VEÍCULO_DETECTADO`) são exibidos no dashboard e gravados automaticamente no Google Sheets via Make sem bloquear a interface.
* **Limitação arquitetural:** A fila de envio ao Make reside exclusivamente em memória RAM (`maxsize=200`). Caso ocorra falha de rede ou indisponibilidade temporária do endpoint, o evento não é persistido em disco nem reenviado automaticamente.

### Fluxo Pendente de Validação (Hardware Físico Conectado)

```text
[Sensores / Botões / Servo MG90S]
        │
        ▼
[Arduino Uno (Firmware C++)]
        │  USB Serial (9600 baud)
        ▼
[Thread Serial Python (PySerial)] ──► [Backend Flask] ──► [Dashboard + Make]
```

* **Distinção de rotas:** Enquanto `/api/simulate` atua apenas em memória no backend, a rota `/api/command` foi preparada para transmitir comandos físicos (`CMD,OPEN`, `CMD,CLOSE`, `CMD,STATUS`) ao Arduino pela porta serial, permanecendo pendente de validação com o circuito conectado.
* **Pendências técnicas e melhorias futuras:**
  * Validação elétrica e ajuste de sensibilidade do sensor TCRT5000 e alimentação dedicada do servo MG90S em bancada.
  * Compilação e upload final do firmware na Arduino IDE e teste *end-to-end* da comunicação bidirecional.
  * **Sincronização inicial na abertura da porta serial:** Atualmente, o backend aguarda 2 segundos após abrir a porta COM e chama `reset_input_buffer()`, descartando mensagens enviadas pelo Arduino durante o reinício (como `SYSTEM,STARTED` e estados iniciais das vagas). Como melhoria futura, o backend deverá enviar automaticamente `CMD,STATUS` logo após conectar à serial para sincronizar o estado inicial com o dashboard.