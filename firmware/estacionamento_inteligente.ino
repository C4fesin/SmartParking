
#include <Servo.h>
#include <string.h>

// =====================================
// PINOS DO SISTEMA
// =====================================

// Sensor da cancela
const int PINO_SENSOR = 2;

// Botoes das vagas
const int BOTAO_VAGA_1 = 3;
const int BOTAO_VAGA_2 = 4;
const int BOTAO_VAGA_3 = 5;

// LEDs indicadores das vagas
const int LED_VAGA_1 = 6;
const int LED_VAGA_2 = 7;
const int LED_VAGA_3 = 10;

// Componentes da cancela
const int PINO_BUZZER = 8;
const int PINO_SERVO = 9;

const int LED_VERMELHO = 11;
const int LED_AMARELO = 12;
const int LED_VERDE = 13;

// =====================================
// CONFIGURACAO DA CANCELA
// =====================================

Servo cancela;

const int ANGULO_FECHADO = 0;
const int ANGULO_ABERTO = 90;

const unsigned long TEMPO_ABERTA = 3000;

bool cancelaAberta = false;
bool veiculoAnterior = false;

unsigned long tempoAbertura = 0;

// =====================================
// CONFIGURACAO DAS VAGAS
// =====================================

const int botoes[3] = {
  BOTAO_VAGA_1,
  BOTAO_VAGA_2,
  BOTAO_VAGA_3
};

const int ledsVagas[3] = {
  LED_VAGA_1,
  LED_VAGA_2,
  LED_VAGA_3
};

bool vagasOcupadas[3] = {
  false, false, false
};

bool leituraAnterior[3] = {
  HIGH, HIGH, HIGH
};

bool estadoEstavel[3] = {
  HIGH, HIGH, HIGH
};

unsigned long ultimoDebounce[3] = {
  0, 0, 0
};

const unsigned long DEBOUNCE = 50;

// =====================================
// COMUNICACAO SERIAL
// =====================================

void enviarEstadoVaga(int numero) {

  Serial.print("SLOT,");
  Serial.print(numero);
  Serial.print(",");

  if (vagasOcupadas[numero - 1]) {
    Serial.println("OCCUPIED");
  } else {
    Serial.println("FREE");
  }
}

void enviarEstadoCancela() {

  if (cancelaAberta) {
    Serial.println("GATE,OPEN");
  } else {
    Serial.println("GATE,CLOSED");
  }
}

// =====================================
// ATUALIZAR LED DE CADA VAGA
// =====================================

void atualizarLedVaga(int indice) {

  if (vagasOcupadas[indice]) {
    digitalWrite(ledsVagas[indice], HIGH);
  } else {
    digitalWrite(ledsVagas[indice], LOW);
  }
}

// =====================================
// CONTROLE DO SEMAFORO
// =====================================

void atualizarSemaforo(
  bool vermelho,
  bool amarelo,
  bool verde
) {

  digitalWrite(LED_VERMELHO, vermelho);
  digitalWrite(LED_AMARELO, amarelo);
  digitalWrite(LED_VERDE, verde);
}

// =====================================
// ABRIR CANCELA
// =====================================

void abrirCancela() {

  if (cancelaAberta) return;

  cancelaAberta = true;

  atualizarSemaforo(LOW, HIGH, LOW);

  tone(PINO_BUZZER, 1000, 200);

  cancela.write(ANGULO_ABERTO);

  atualizarSemaforo(LOW, LOW, HIGH);

  tone(PINO_BUZZER, 1500, 300);

  tempoAbertura = millis();

  enviarEstadoCancela();
  
  
// =====================================
// COMANDOS RECEBIDOS DO PYTHON
// =====================================

void enviarTodosEstados() {

  Serial.println("SYSTEM,STARTED");

  enviarEstadoCancela();

  for (int i = 0; i < 3; i++) {
    enviarEstadoVaga(i + 1);
  }
}

void processarComando(char* comando) {

  if (strcmp(comando, "CMD,OPEN") == 0) {

    abrirCancela();

    Serial.println("EVENT,REMOTE_OPEN");

  }

  else if (strcmp(comando, "CMD,CLOSE") == 0) {

    // Nunca fechar enquanto houver veículo detectado
    if (digitalRead(PINO_SENSOR) == LOW) {

      Serial.println("EVENT,CLOSE_BLOCKED");

    } else {

      fecharCancela();

    }

  }

  else if (strcmp(comando, "CMD,STATUS") == 0) {

    enviarTodosEstados();

  }

  else {

    Serial.print("ERROR,UNKNOWN_COMMAND,");
    Serial.println(comando);

  }
}

// Leitura serial sem bloquear o loop principal
void receberComandosSerial() {

  static char buffer[40];
  static byte indice = 0;

  while (Serial.available() > 0) {

    char caractere = Serial.read();

    if (caractere == '\n') {

      buffer[indice] = '\0';

      if (indice > 0) {
        processarComando(buffer);
      }

      indice = 0;

    }

    else if (caractere != '\r') {

      if (indice < sizeof(buffer) - 1) {

        buffer[indice++] = caractere;

      } else {

        // Descarta comandos maiores que o buffer
        indice = 0;

      }
    }
  }
}

}

// =====================================
// FECHAR CANCELA
// =====================================

void fecharCancela() {

  if (!cancelaAberta) return;

  atualizarSemaforo(LOW, HIGH, LOW);

  cancela.write(ANGULO_FECHADO);

  delay(300);

  atualizarSemaforo(HIGH, LOW, LOW);

  cancelaAberta = false;

  enviarEstadoCancela();

  Serial.println("EVENT,GATE_CLOSED");
}

// =====================================
// LEITURA DOS BOTOES
// =====================================

void atualizarVagas() {

  for (int i = 0; i < 3; i++) {

    bool leitura = digitalRead(botoes[i]);

    if (leitura != leituraAnterior[i]) {
      ultimoDebounce[i] = millis();
    }

    if (millis() - ultimoDebounce[i] > DEBOUNCE) {

      if (leitura != estadoEstavel[i]) {

        estadoEstavel[i] = leitura;

        // Botao pressionado
        if (estadoEstavel[i] == LOW) {

          // Alterna o estado da vaga
          vagasOcupadas[i] = !vagasOcupadas[i];

          // Atualiza o LED correspondente
          atualizarLedVaga(i);

          // Envia informacoes pela serial
          enviarEstadoVaga(i + 1);

          Serial.print("EVENT,SLOT_CHANGED,");
          Serial.println(i + 1);
        }
      }
    }

    leituraAnterior[i] = leitura;
  }
}

// =====================================
// INICIALIZACAO
// =====================================

void setup() {

  Serial.begin(9600);

  // Sensor
  pinMode(PINO_SENSOR, INPUT);

  // Botoes
  for (int i = 0; i < 3; i++) {
    pinMode(botoes[i], INPUT_PULLUP);
  }

  // LEDs das vagas
  for (int i = 0; i < 3; i++) {
    pinMode(ledsVagas[i], OUTPUT);
    digitalWrite(ledsVagas[i], LOW);
  }

  // Buzzer
  pinMode(PINO_BUZZER, OUTPUT);

  // Semaforo
  pinMode(LED_VERMELHO, OUTPUT);
  pinMode(LED_AMARELO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);

  // Servo
  cancela.attach(PINO_SERVO);
  cancela.write(ANGULO_FECHADO);

  atualizarSemaforo(HIGH, LOW, LOW);

  delay(500);

  Serial.println("SYSTEM,STARTED");

  enviarEstadoCancela();

  // Envia estado inicial das vagas
  for (int i = 0; i < 3; i++) {
    atualizarLedVaga(i);
    enviarEstadoVaga(i + 1);
  }
}

// =====================================
// LOOP PRINCIPAL
// =====================================


void loop() {

  // Recebe comandos enviados pelo Python
  receberComandosSerial();

  // Atualiza os botoes e as vagas
  atualizarVagas();

  // Detecta veiculo
  bool veiculoDetectado =
    (digitalRead(PINO_SENSOR) == LOW);

  // Detecta nova aproximacao
  if (
    veiculoDetectado &&
    !veiculoAnterior &&
    !cancelaAberta
  ) {

    Serial.println("EVENT,VEHICLE_DETECTED");

    abrirCancela();
  }

  veiculoAnterior = veiculoDetectado;

  // Fecha automaticamente quando o sensor estiver livre
  // e o tempo minimo tiver passado
  if (
    cancelaAberta &&
    !veiculoDetectado &&
    millis() - tempoAbertura >= TEMPO_ABERTA
  ) {

    fecharCancela();
  }
}
