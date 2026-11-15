# Smart Parking — Estacionamento Inteligente

Protótipo acadêmico de automação e monitoramento de estacionamento que integra **Arduino Uno**, **Python**, **Flask**, **PySerial** e um **Dashboard Web** responsivo para controle de acesso e acompanhamento em tempo real de 3 vagas.

---

## Arquitetura do Sistema

```text
[Hardware: Arduino Uno]
  ├── Sensor IR TCRT5000 (detecção de veículos na cancela)
  ├── Micro Servo MG90S (acionamento da cancela)
  ├── 3 Botões físicos (alternância de ocupação das vagas)
  ├── LEDs indicadores (status das vagas e semáforo da cancela)
  └── Buzzer (sinalização sonora)
          │
          ▼  Comunicação Serial (9600 baud)
[Backend: Python 3 + Flask 3.1.3 + PySerial 3.5]
  ├── Thread dedicada para leitura serial e reconexão automática
  ├── API REST (/api/status, /api/events, /api/simulate, /api/command, /health)
  └── [Planejado] Disparo de eventos: Python/Flask → Webhook Make → Google Sheets
          │
          ▼  HTTP / JSON (Polling a cada 1s)
[Frontend: Dashboard Web (HTML5, CSS3, JavaScript)]
  ├── Indicadores de vagas totais, livres e ocupadas
  ├── Monitoramento individual das 3 vagas e estado da cancela
  ├── Histórico de eventos em tempo real
  └── Painel de simulação para testes sem hardware conectado


   Hardware Utilizado
Microcontrolador: Arduino Uno

Sensor de Presença: Sensor reflexivo infravermelho TCRT5000

Atuador da Cancela: Micro servo motor MG90S

Entradas de Vagas: 3 botões físicos táteis (simulação de ocupação LIVRE/OCUPADA)

Sinalização Visual: 3 LEDs indicadores de vagas + 3 LEDs de semáforo da cancela (vermelho, amarelo e verde)

Sinalização Sonora: Buzzer

Montagem: Protótipo desenvolvido em protoboard

Status Atual do Desenvolvimento
Implementado (Software e Estrutura)
Estrutura modular do backend em Python (backend/leitura_arduino.py) com controle de concorrência (threading.Lock).

API REST em Flask com rotas de monitoramento, comando serial, simulação e diagnóstico (/health).

Dashboard web em HTML, CSS e JavaScript (frontend/templates/index.html) com tema escuro e atualização assíncrona.

Painel de simulação funcional no dashboard para operação independente do hardware.

Protocolo serial bidirecional preparado no backend e estruturado no firmware (firmware/estacionamento_inteligente.ino), incluindo trava de segurança contra fechamento sobre veículos.

Ainda Não Validado (Em Bancada)
Compilação final e upload do firmware corrigido na Arduino IDE.

Comunicação bidirecional física (Python ↔ Arduino) via porta serial COM.

Funcionamento estável do micro servo MG90S e do sensor TCRT5000 na montagem física em protoboard (incluindo ajuste de sensibilidade e alimentação).

Integração completa entre circuito físico e dashboard web em operação contínua.

Validação final do buzzer e implementação futura da integração externa (Python/Flask → Webhook Make → Google Sheets).

Estrutura do Repositório
SmartParking/
├── backend/
│   ├── leitura_arduino.py        # Servidor Flask, API REST e ponte serial
│   └── requirements.txt          # Dependências Python (Flask e PySerial)
├── docs/
│   ├── arquitetura/              # Documentação de arquitetura e fluxos futuros
│   ├── circuito-fisico/          # Fotografias da montagem real em protoboard
│   ├── especificacoes-tecnicas/  # Pinagem, protocolo serial e endpoints da API
│   └── simulacao-tinkercad/      # Capturas do circuito simulado no Tinkercad
├── firmware/
│   └── estacionamento_inteligente.ino  # Firmware C++ para Arduino Uno
├── frontend/
│   └── templates/
│       └── index.html            # Interface web do dashboard e simulador
├── .gitignore
└── README.md

Instalação e Execução Local
1. Clonar o repositórioBashgit clone [https://github.com/C4fesin/SmartParking.git](https://github.com/C4fesin/SmartParking.git)
cd SmartParking
2. Criar e ativar um ambiente virtual PythonBashpython -m venv .venv
Windows (PowerShell):Bash.venv\Scripts\Activate.ps1
Linux / macOS:Bashsource .venv/bin/activate
3. Instalar as dependênciasBashpip install -r backend/requirements.txt
4. Configurar a porta serial (opcional para modo simulador)No arquivo backend/leitura_arduino.py, ajuste a constante PORTA_SERIAL (ex.: "COM3" no Windows ou "/dev/ttyUSB0" no Linux) conforme a porta atribuída ao Arduino Uno. Caso o Arduino não esteja conectado, o servidor continuará operando em modo simulador e tentará reconectar a cada 5 segundos.5. Executar o servidor FlaskBashpy backend/leitura_arduino.py
(Ou python backend/leitura_arduino.py, conforme a configuração do seu sistema).Acesse no navegador:Plaintext[http://127.0.0.1:5000](http://127.0.0.1:5000)
Endpoints da API FlaskRotaMétodoDescrição/GETRenderiza o dashboard web (frontend/templates/index.html)/api/statusGETRetorna o estado atual do sistema, cancela e contagem de vagas/api/eventsGETRetorna o histórico recente de eventos registrados (até 100 registros)/api/simulatePOSTExecuta ações de simulação (ocupar, liberar, abrir, fechar, veiculo, resetar)/api/commandPOSTEnvia comandos seriais ao Arduino (abrir → CMD,OPEN, fechar → CMD,CLOSE, status → CMD,STATUS)/healthGETVerifica o status online do servidor Flask e da conexão serial com o ArduinoEvolução PlanejadaIntegração Externa (Make + Google Sheets): Envio automático dos eventos registrados pelo backend Flask para um webhook do Make, gravando o histórico operacional do estacionamento em uma planilha do Google Sheets.