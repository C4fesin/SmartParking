# Especificações Técnicas — Smart Parking

## 1. Mapeamento de Pinos (Arduino Uno)

| Pino Arduino | Tipo | Componente | Função |
| :---: | :---: | :--- | :--- |
| `D2` | `INPUT` | Sensor IR TCRT5000 | Detecta presença de veículo na cancela (`LOW` = detectado) |
| `D3` | `INPUT_PULLUP` | Botão Vaga 01 | Alterna estado da Vaga 01 (`LIVRE` / `OCUPADA`) |
| `D4` | `INPUT_PULLUP` | Botão Vaga 02 | Alterna estado da Vaga 02 (`LIVRE` / `OCUPADA`) |
| `D5` | `INPUT_PULLUP` | Botão Vaga 03 | Alterna estado da Vaga 03 (`LIVRE` / `OCUPADA`) |
| `D6` | `OUTPUT` | LED Vaga 01 | Indica ocupação da Vaga 01 |
| `D7` | `OUTPUT` | LED Vaga 02 | Indica ocupação da Vaga 02 |
| `D8` | `OUTPUT` | Buzzer | Sinalização sonora de movimentação da cancela |
| `D9` | `PWM / Servo` | Micro Servo MG90S | Movimenta a cancela (`0°` fechada / `90°` aberta) |
| `D10` | `OUTPUT` | LED Vaga 03 | Indica ocupação da Vaga 03 |
| `D11` | `OUTPUT` | LED Vermelho | Semáforo: cancela fechada |
| `D12` | `OUTPUT` | LED Amarelo | Semáforo: cancela em transição |
| `D13` | `OUTPUT` | LED Verde | Semáforo: cancela aberta |

---

## 2. Protocolo de Comunicação Serial (9600 baud)

### Mensagens enviadas pelo Arduino (`Arduino → Python`)
* `SYSTEM,STARTED` — Inicialização concluída ou resposta a `CMD,STATUS`.
* `GATE,OPEN` / `GATE,CLOSED` — Estado atual da cancela.
* `SLOT,<1|2|3>,FREE` / `SLOT,<1|2|3>,OCCUPIED` — Estado individual de cada vaga.
* `EVENT,VEHICLE_DETECTED` — Veículo detectado pelo sensor TCRT5000.
* `EVENT,GATE_CLOSED` — Cancela fechada com sucesso.
* `EVENT,REMOTE_OPEN` — Abertura acionada remotamente via comando serial.
* `EVENT,CLOSE_BLOCKED` — Fechamento bloqueado pela trava de segurança (veículo sob o sensor).
* `EVENT,SLOT_CHANGED,<1|2|3>` — Alteração acionada pelo botão físico da vaga.
* `ERROR,UNKNOWN_COMMAND,<comando>` — Comando não reconhecido recebido pela serial.

### Comandos enviados pelo Python (`Python → Arduino`)
* `CMD,OPEN\n` — Solicita abertura da cancela.
* `CMD,CLOSE\n` — Solicita fechamento da cancela (sujeito à trava do sensor).
* `CMD,STATUS\n` — Solicita envio completo do estado atual do sistema, cancela e vagas.