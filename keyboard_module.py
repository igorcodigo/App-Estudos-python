from pynput import keyboard
import threading
from funcoes_modulo import alterar_status_de_estudo,registrar_refeicao,alarme

# ================================ Sensor de teclas ======================================

# Coleta eventos do teclado apos soltar a tecla ou combinacao de teclas(tipo ctrl+c)
def keyboard_listener():
    # Inicia o listener para escutar eventos de teclado com as funções on_press e on_release.
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()  # Aguarda até que o listener seja parado.


#============= Trata os dados para identificar quais telcas foram pressionas =================
teclas_pressionadas = [] # Conjunto para armazenar as teclas que estão sendo pressionadas 
numero_pressionado = None
def filtro_de_teclas(key):
    try:
        # Try to check if the key has a char attribute
        # print(f"{key.char} tecla do tipo 1 pressionada")
        tecla = key.char
    except AttributeError:
        try:
            # Try to check if the key has a name attribute
            # print(f"{key.name} tecla do tipo 2 pressionada")
            tecla = key.name
        except AttributeError:
            # print(f"{key} tecla do tipo 3 pressionada")
            tecla = key
    return tecla

# Funcao para adicionar a uma lista quais teclas estao sendo pressionadas ao mesmo tempo
def on_press(key):
    global teclas_pressionadas,numero_pressionado
    tecla = filtro_de_teclas(key)
    teclas_pressionadas.append(tecla)
    try:
        if tecla.isdigit(): numero_pressionado = int(tecla)
    except:
        print("tecla",tecla)

# Funcao para chamar a acão correwspondente a tecla ou a combinação de telcas e  limpar a lista de teclas pressionadas assim que alguma delas for liberada/solta)
def on_release(key):
    global teclas_pressionadas,numero_pressionado
    tecla = filtro_de_teclas(key)
    atalhos(tecla)
    teclas_pressionadas,numero_pressionado = [], None


# ==================== logica das teclas ou da combinação de teclas ==========================

#Executa uma ação dependendo da tecla ou da combinação de teclas pressionadas
def atalhos(tecla):
    #Teclas individuais
    if tecla == "page_down":alterar_status_de_estudo()
    elif tecla == "insert":registrar_refeicao()
    elif tecla == "page_up":pass

    # Combinacoes de teclas ==============    
    if 'up' in teclas_pressionadas and numero_pressionado != None: 
        # Cria uma thread em paralelo para poder fazer diferentes alarmes
        threading.Thread(target=lambda: alarme(numero_pressionado)).start()

    else: print(f"Tecla {tecla} sem instrucoes associadas")
        

