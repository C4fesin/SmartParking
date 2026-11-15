# Arquitetura do Sistema — Smart Parking

## 1. Camadas da Aplicação

1. **Camada Física (Firmware — `firmware/estacionamento_inteligente.ino`)**
   * Executa no **Arduino Uno** em laço não bloqueante (`loop()`).
   * Lê o sensor reflexivo infravermelho **TCRT5000** e os 3 botões táteis (com *debounce* de 50 ms).
   * Aciona o micro servo **MG90S**, os LEDs de vaga, o semáforo da cancela e o buzzer.
   * Comunica-se pela interface USB Serial a **9600 baud**.

2. **Camada de Integração e API (Backend — `backend/leitura_arduino.py`)**
   * Desenvolvida em **Python** com **Flask 3.1.3** e **PySerial 3.5**.
   * Mantém uma *thread* dedicada (`conectar_arduino`) para leitura contínua da serial e reconexão automática a cada 5 segundos em caso de desconexão.
   * Protege o dicionário compartilhado de estado e a fila de eventos (`deque(maxlen=100)`) com `threading.Lock`.

3. **Camada de Visualização e Controle (Frontend — `frontend/templates/index.html`)**
   * Interface web em HTML, CSS e JavaScript com atualização automática via `fetch` a cada 1000 ms.
   * Permite monitorar ocupação e operar o modo simulador via requisições `POST` para `/api/simulate`.

---

## 2. Arquitetura Prevista para Integração Externa (Etapa Futura)

O sistema está estruturado para incorporar o registro externo de eventos sem alterar a lógica do microcontrolador:

```text
Arduino Uno (Serial) ──► Python / Flask (registrar_evento) ──► Webhook Make ──► Google Sheets

