
import serial
import threading
import time

from datetime import datetime
from collections import deque
from flask import Flask, jsonify, render_template , request

# ==========================================
# CONFIGURACOES
# ==========================================

PORTA_SERIAL = "COM3"  # Altere para a porta do seu Arduino
BAUD_RATE = 9600

app = Flask(__name__)

# ==========================================
# ESTADO DO ESTACIONAMENTO
# ==========================================

estado = {
    "sistema": "INICIANDO",
    "cancela": "FECHADA",
    "vagas": {
        1: "LIVRE",
        2: "LIVRE",
        3: "LIVRE"
    },
    "ultima_atualizacao": None
}

eventos = deque(maxlen=100)

lock = threading.Lock()

# ==========================================
# CONTROLE DA CONEXAO SERIAL
# ==========================================

arduino = None

serial_lock = threading.Lock()

serial_conectada = False

# ==========================================
# REGISTRAR EVENTOS
# ==========================================

def registrar_evento(tipo, dados=None):

    evento = {
        "tipo": tipo,
        "dados": dados or {},
        "horario": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    with lock:
        eventos.append(evento)

    print(f"[EVENTO] {tipo} - {dados or {}}")


# ==========================================
# INTERPRETAR MENSAGENS DO ARDUINO
# ==========================================

def processar_mensagem(mensagem):

    partes = mensagem.strip().split(",")

    if not partes:
        return

    tipo = partes[0]

    # Inicializacao
    if tipo == "SYSTEM" and len(partes) >= 2:

        with lock:
            estado["sistema"] = partes[1]

        registrar_evento("SYSTEM", {"estado": partes[1]})

    
    # Estado da cancela
    elif tipo in ("GATE", "CANCELA") and len(partes) >= 2:

        valor = partes[1]

        if valor in ("OPEN", "ABERTA"):
            situacao = "ABERTA"
        elif valor in ("CLOSED", "FECHADA"):
            situacao = "FECHADA"
        else:
            return

        with lock:
            estado["cancela"] = situacao
            estado["ultima_atualizacao"] = datetime.now().isoformat()

        registrar_evento("CANCELA", {"estado": situacao})

    # Estado das vagas
    elif tipo in ("SLOT", "VAGA") and len(partes) >= 3:

        try:
            numero = int(partes[1])
            valor = partes[2]

            if numero not in (1, 2, 3):
                return

            if valor in ("FREE", "LIVRE"):
                situacao = "LIVRE"
            elif valor in ("OCCUPIED", "OCUPADA"):
                situacao = "OCUPADA"
            else:
                return

            with lock:
                estado["vagas"][numero] = situacao
                estado["ultima_atualizacao"] = datetime.now().isoformat()

            registrar_evento(
                "VAGA",
                {
                    "vaga": numero,
                    "estado": situacao
                }
            )

        except ValueError:
            print("[ERRO] Numero de vaga invalido")

    # Outros eventos
    elif tipo == "EVENT":

        if len(partes) >= 2:

            nome_evento = partes[1]

            registrar_evento(
                nome_evento,
                {"informacoes": partes[2:]}
            )

    else:
        print(f"[AVISO] Mensagem desconhecida: {mensagem}")


# ==========================================
# CONEXAO SERIAL
# ==========================================


# ==========================================
# CONEXAO SERIAL
# ==========================================

def conectar_arduino():

    global arduino, serial_conectada

    while True:

        try:

            print(f"[SERIAL] Conectando em {PORTA_SERIAL}...")

            conexao = serial.Serial(
                PORTA_SERIAL,
                BAUD_RATE,
                timeout=1,
                write_timeout=1
            )

            with serial_lock:
                arduino = conexao
                serial_conectada = True

            print("[SERIAL] Arduino conectado!")

            # O Arduino pode reiniciar ao abrir a serial
            time.sleep(2)

            with serial_lock:
                if arduino is conexao and conexao.is_open:
                    conexao.reset_input_buffer()

            while True:

                with serial_lock:

                    if arduino is not conexao or not conexao.is_open:
                        break

                    linha = conexao.readline().decode(
                        "utf-8",
                        errors="replace"
                    ).strip()

                if linha:
                    print(f"[ARDUINO] {linha}")
                    processar_mensagem(linha)

        except serial.SerialException as erro:

            print(f"[SERIAL] Falha na conexao: {erro}")

        except Exception as erro:

            print(f"[ERRO] Comunicacao serial: {erro}")

        finally:

            with serial_lock:

                if arduino is not None:
                    try:
                        arduino.close()
                    except Exception:
                        pass

                arduino = None
                serial_conectada = False

            print("[SERIAL] Desconectado.")
            print("[SERIAL] Tentando novamente em 5 segundos...")

            time.sleep(5)


# ==========================================
# ENVIAR COMANDO PARA O ARDUINO
# ==========================================

def enviar_comando_arduino(comando):

    with serial_lock:

        if arduino is None or not serial_conectada:
            return False, "Arduino desconectado"

        try:

            mensagem = comando + "\n"

            arduino.write(mensagem.encode("utf-8"))
            arduino.flush()

            print(f"[PYTHON -> ARDUINO] {comando}")

            return True, "Comando enviado"

        except (serial.SerialException, OSError) as erro:

            print(f"[SERIAL] Erro ao enviar comando: {erro}")

            return False, "Falha ao enviar comando pela serial"


# ==========================================
# API - STATUS COMPLETO
# ==========================================
@app.route("/")
def dashboard():
    return render_template("index.html")
@app.route("/api/status", methods=["GET"])
def obter_status():

    with lock:

        dados = {
            "sistema": estado["sistema"],
            "cancela": estado["cancela"],
            "vagas": {
                str(k): v
                for k, v in estado["vagas"].items()
            },
            "vagas_livres": sum(
                v == "LIVRE"
                for v in estado["vagas"].values()
            ),
            "vagas_ocupadas": sum(
                v == "OCUPADA"
                for v in estado["vagas"].values()
            ),
            "ultima_atualizacao": estado["ultima_atualizacao"]
        }

    return jsonify(dados)


# ==========================================
# API - HISTORICO DE EVENTOS
# ==========================================

@app.route("/api/events", methods=["GET"])
def obter_eventos():

    with lock:
        dados = list(eventos)

    return jsonify(dados)

# ==========================================
# SIMULADOR - COMANDOS PELO DASHBOARD
# ==========================================

@app.route("/api/simulate", methods=["POST"])
def simular_comando():

    dados = request.get_json(silent=True) or {}
    acao = dados.get("acao")

    # Ocupar ou liberar uma vaga
    if acao in ("ocupar", "liberar"):

        try:
            numero = int(dados.get("vaga"))
        except (TypeError, ValueError):
            return jsonify({"erro": "Número de vaga inválido"}), 400

        if numero not in (1, 2, 3):
            return jsonify({"erro": "Vaga inexistente"}), 400

        situacao = "OCUPADA" if acao == "ocupar" else "LIVRE"

        processar_mensagem(f"VAGA,{numero},{situacao}")

    # Abrir ou fechar a cancela
    elif acao == "abrir":
        processar_mensagem("CANCELA,ABERTA")

    elif acao == "fechar":
        processar_mensagem("CANCELA,FECHADA")

    # Simular a chegada de um veículo
    elif acao == "veiculo":
        processar_mensagem("EVENT,VEÍCULO_DETECTADO")
        processar_mensagem("CANCELA,ABERTA")

    # Restaurar o estado inicial
    elif acao == "resetar":
        processar_mensagem("SYSTEM,INICIANDO")
        processar_mensagem("CANCELA,FECHADA")

        for numero in (1, 2, 3):
            processar_mensagem(f"VAGA,{numero},LIVRE")

    else:
        return jsonify({"erro": "Ação desconhecida"}), 400

    return jsonify({
        "resultado": "OK",
        "acao": acao
    })

    
# ==========================================
# API - COMANDOS PARA O ARDUINO FISICO
# ==========================================

@app.route("/api/command", methods=["POST"])
def comandar_arduino():

    dados = request.get_json(silent=True) or {}

    acao = dados.get("acao")

    comandos = {
        "abrir": "CMD,OPEN",
        "fechar": "CMD,CLOSE",
        "status": "CMD,STATUS"
    }

    if acao not in comandos:

        return jsonify({
            "erro": "Comando desconhecido"
        }), 400

    sucesso, mensagem = enviar_comando_arduino(
        comandos[acao]
    )

    if not sucesso:

        return jsonify({
            "erro": mensagem
        }), 503

    return jsonify({
        "resultado": "OK",
        "acao": acao,
        "mensagem": mensagem
    })

# ==========================================
# API - VERIFICAR SERVIDOR
# ==========================================

@app.route("/health", methods=["GET"])
def verificar_servidor():

    with serial_lock:
        conectado = serial_conectada

    return jsonify({
        "servidor": "ONLINE",
        "arduino": "CONECTADO" if conectado else "DESCONECTADO"
    })


# ==========================================
# INICIAR APLICACAO
# ==========================================

if __name__ == "__main__":

    thread_serial = threading.Thread(
        target=conectar_arduino,
        daemon=True
    )

    thread_serial.start()

    print("[FLASK] API iniciada")
    print("[FLASK] Endereco: http://127.0.0.1:5000")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )
