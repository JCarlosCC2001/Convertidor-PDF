import socket
import threading
import json
import sys
import logging

logger = logging.getLogger(__name__)

PORT = 54321
HOST = '127.0.0.1'

_server_socket = None

def verificar_instancia_unica(archivos):
    """
    Verifica si ya hay otra instancia corriendo.
    Si la hay, le manda los archivos a través de un socket local y termina el programa actual.
    Si NO la hay, reserva el puerto y retorna False (permitiendo que el programa siga su ejecución).
    """
    global _server_socket
    _server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Intenta reservar el puerto. Si otra instancia está corriendo, esto fallará.
        _server_socket.bind((HOST, PORT))
        _server_socket.listen()
        return False
    except socket.error:
        # Ya hay otra instancia corriendo en ese puerto
        try:
            with socket.create_connection((HOST, PORT), timeout=1) as sock:
                if archivos:
                    # Enviar los archivos como JSON codificado
                    data = json.dumps(archivos).encode('utf-8')
                    sock.sendall(data)
        except Exception as e:
            logger.error("Error al enviar archivos a la instancia principal: %s", e)
        
        # Salir silenciosamente para no abrir otra ventana
        sys.exit(0)

def iniciar_escucha_segundo_plano(callback):
    """
    Inicia el bucle accept() en segundo plano usando el socket ya reservado.
    Llama a callback(archivos) cada vez que recibe datos de otra instancia.
    """
    def _listen():
        global _server_socket
        if not _server_socket:
            return
        while True:
            try:
                conn, addr = _server_socket.accept()
                with conn:
                    data = conn.recv(65536)
                    if data:
                        try:
                            archivos = json.loads(data.decode('utf-8'))
                            if archivos:
                                callback(archivos)
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                logger.error("Error recibiendo archivos en instancia unica: %s", e)
                
    t = threading.Thread(target=_listen, daemon=True)
    t.start()
