import pandas as pd
from datetime import datetime
import time
import numpy as np
import tkinter as tk
import pygame

root,tempo_frame,meal_frame,labels,meal_listbox = 0,0,0,0,0
estudando,ultimo_page_down = None, None
stop,stop2 = None, None
ciclo,tempo_total = 0,0
ciclos_de_estudos_tempos = [0]
refeicoes_registradas = []
formatacao_data = "%d/%m/%Y"
df = None




def configuracao_inicial(widgets_interface):
    global df,ciclos_de_estudos_tempos,ciclo,ciclo_refeicoes,refeicoes_registradas,            root,tempo_frame,meal_frame,labels,meal_listbox
    # Le o CSV e armazena ele em uma variavel
    df = pd.read_csv('Registros_Diarios2.csv')
    print(df)
    root,tempo_frame,meal_frame,labels,meal_listbox = widgets_interface

    Data_da_ultima_linha = df.iloc[-1]['Data']

    # Obtem a data de hoje e formata ela em um certo padrao
    Hoje_Formatado = datetime.now().date().strftime(formatacao_data)

    #Se já houver registros da data de hoje no programa
    if Hoje_Formatado == Data_da_ultima_linha:
        valores_estudo_string = df.loc[df.index[-1], 'Tempo de estudo']
        if valores_estudo_string == '' or pd.isna(valores_estudo_string):
            df.loc[df.index[-1], 'Tempo de estudo'] = "0,0"
            df.to_csv("Registros_Diarios2.csv", index=False)
        elif ',' in valores_estudo_string:           
            ciclos_de_estudos_tempos = list(map(int, valores_estudo_string.split(',')))             
            ciclo = len(ciclos_de_estudos_tempos)
    
        valores_refeicoes_string = df.loc[df.index[-1], 'Horario das refeicoes']
        if valores_refeicoes_string != "" and pd.notna(valores_refeicoes_string):
            refeicoes_registradas = list(valores_refeicoes_string.split(','))
            ciclo_refeicoes = len(refeicoes_registradas)
            refrescar_listbox_horario_refeicoes(refeicoes_registradas, meal_listbox)

    #Geralmente ocorre quando passo o csv com os cabecalhos e deixo um 0 na coluna da data
    elif Data_da_ultima_linha == 0:
        df.loc[df.index[-1], 'Data'] = Hoje_Formatado
        df.to_csv("Registros_Diarios2.csv", index=False) 
        Data_da_ultima_linha = df.iloc[-1]['Data']

    total_segundos = somar_todos_os_tempos_de_estudos_do_dia(df)
    atualizar_label_tempo_total(total_segundos)

#Funcao que contem um loop para calcular o tempo do ciclo de estudos atual e realiza as outras acoes relacionadas
def adicionando_tempos():
    # Inicializa contadores 
    contador = 0
    contador2 = 0
    # Inicia um laço infinito para verificar constantemente e atualizar o tempo 
    while True:
        # Verifica se a condição para iniciar a contagem de tempo (estudando) é verdadeira e se houve uma ação de "page down".
        if estudando == True and ultimo_page_down is not None:
            # Calcula o tempo total gasto no ciclo atual.
            total_segundos = calcular_tempo_ciclo()
            # Atualiza a exibição para mostrar o tempo atual gasto.
            atualizar_label_tempo_atual(total_segundos)
            # Converte o tempo total de float para inteiro para facilitar o manuseio de minutos e segundos.
            segundos_inteiros = int(total_segundos)
            # Calcula os minutos totais a partir dos segundos.
            minutos = (segundos_inteiros // 60)
            # A cada 6000 iterações (aproximadamente 10 minutos se cada iteração for de 0.1 segundos), atualiza o título da janela.
            if  contador2 % 6000 == 0:
                print(minutos)
                print(contador2)
                texto_titulo = 'Daily Schedule ' + str(minutos)
                root.title(texto_titulo)
                
                contador2 = 0

            # Após cada 100 iterações (10 segundos), se ainda estiver estudando, registra o tempo em um arquivo CSV.
            if contador >= 100 and estudando == True:
                contador = 0
                armazena_no_csv(segundos_inteiros)
                                

            contador+=1
            contador2+=1
            time.sleep(0.1)
        # Se não estiver estudando ou se a ação de "page down" não tiver acontecido, espera mais tempo (1 segundo) antes de verificar novamente.
        else: time.sleep(0.1 if ultimo_page_down is not None else 1)

#Altera o status de estudando e realiza as outras acoes relacionadas
def alterar_status_de_estudo():
    global estudando, ultimo_page_down, ciclo, stop
    # Page Down é usada para indicar a alteração do status do estudo, se estava estudando (estudando == true), agora vai entrar em intervalo (estudando == False) e vice versa
    if estudando == None:
        stop = False
        estudando = True
        ciclos_de_estudos_tempos.append(0) 
        print("Iniciando rotina de estudos")
        play_audio(r'Midias\reactos-boot-85864.mp3')
        root.iconbitmap('Midias\Livro Aberto.ico')
    elif estudando == False:
        stop = False
        estudando = True
        ciclos_de_estudos_tempos.append(0) 
        ciclo = ciclo + 1
        print("Retomando estudos")
        play_audio(r'Midias\announcement-sound-4-21464.mp3')
        root.iconbitmap('Midias\Livro Aberto.ico')

    elif estudando == True:
        stop = True
        estudando = False
        df_atual = armazena_no_csv(int(calcular_tempo_ciclo()))
        total_segundos = somar_todos_os_tempos_de_estudos_do_dia(df_atual)
        atualizar_label_tempo_total(total_segundos)
        print("Entrando em intervalo")
        play_audio(r'Midias\Microsoft-Windows-XP-Shutdown-Sound.mp3')
        root.iconbitmap('Midias\Livro Fechado.ico')

    ultimo_page_down = datetime.now()

def registrar_refeicao():
    global refeicoes_registradas
    hora_atual_formatada = datetime.now().strftime("%H:%M")
    refeicoes_registradas.append(hora_atual_formatada)
    refrescar_listbox_horario_refeicoes(refeicoes_registradas, meal_listbox)
    armazena_refeicao_no_csv(refeicoes_registradas)
    play_audio(r'Midias\Minecraft Eating.wav', volume=0.9)




#Armazena os tempos em csv na linha do dia atual
def armazena_no_csv(duracao_em_segundos):
    global ciclos_de_estudos_tempos,ciclo
    # Retorna uma string indicando se a data de hoje corresponde a uma linha existente 
    comparativo_data,df_atual = comparar_data_de_hoje_com_CSV()
    ciclos_de_estudos_tempos[ciclo] = duracao_em_segundos # Adiciona o ultimo ciclo de estudos a lista ciclos_de_estudos_tempos

    if comparativo_data == "ultima linha":
        # Salva no csv a lista com o tempo dos ciclos de estudo
        df_atual = salvar_string_na_ultima_linha_do_csv(df_atual,'Tempo de estudo',ciclos_de_estudos_tempos)
        return df_atual     
def armazena_refeicao_no_csv(refeicoes_registradas):
    comparativo,df_atual = comparar_data_de_hoje_com_CSV()
    if comparativo == "ultima linha": 
        df_atual = salvar_string_na_ultima_linha_do_csv(df_atual,'Horario das refeicoes',refeicoes_registradas)
        return df_atual 
        

# ================================= Funcoes auxiliares =====================================
def somar_todos_os_tempos_de_estudos_do_dia(df):
    ultima_linha = df.iloc[-1]
    total_segundos = sum(int(tempo) for tempo in ultima_linha['Tempo de estudo'].split(',') if tempo.isdigit())
    print(total_segundos)
    return int(total_segundos)
def calcular_tempo_ciclo():
    agora = datetime.now()
    if ultimo_page_down !=None:
        tempo_do_ciclo_atual = agora - ultimo_page_down
        total_segundos = tempo_do_ciclo_atual.total_seconds()
    else: total_segundos = 0
    return total_segundos

def comparar_data_de_hoje_com_CSV():
    global ultimo_page_down,ciclos_de_estudos_tempos,refeicoes_registradas
    try:
        df_atual = pd.read_csv("Registros_Diarios2.csv")
    except FileNotFoundError: pass
    Data_da_ultima_linha = df_atual.iloc[-1]['Data']
    Data_de_hoje = datetime.now().date()

    # Se a Data_da_ultima_linha for uma string 
    if isinstance(Data_da_ultima_linha, str):
        # converte para objeto datetime.date
        Data_da_ultima_linha = datetime.strptime(Data_da_ultima_linha,formatacao_data).date()
        # Compara a data de hoje com a data fornecida
        if Data_de_hoje > Data_da_ultima_linha: 
            refeicoes_registradas = []
            df_novo = criar_nova_linha(df_atual)
            df_atual = df_novo
            comparativo = "ultima linha"
        elif Data_de_hoje == Data_da_ultima_linha: 
            comparativo = "ultima linha"
        elif Data_de_hoje < Data_da_ultima_linha: 
            print("Error")
            comparativo = None
        # Devo criar um codigo para vasculhar todas as datas e colocar a a linha na posicao correta por ordem de data para evitar bug s
        return comparativo, df_atual
def salvar_string_na_ultima_linha_do_csv(df_atual,coluna,item):
        df_atual.loc[df_atual.index[-1], f'{coluna}'] = ','.join(map(str, item))

        # Envia dados para o arquivo CSV
        df_atual.to_csv("Registros_Diarios2.csv", index=False)
        return df_atual  
#É chamada quando o dia atual é diferente do dia da ultima linha do csv
def criar_nova_linha(df_atual):
    global ciclo,ciclos_de_estudos_tempos,ultimo_page_down
    Hoje_Formatado = datetime.now().date().strftime(formatacao_data)
    # Adiciona uma nova linha ao DataFrame atual e envio para o arquivo
    df_atual.loc[len(df_atual)] = np.nan
    df_atual.loc[df_atual.index[-1], 'Data'] = Hoje_Formatado
    df_atual.loc[df_atual.index[-1], 'Tempo de estudo'] = 0
    df_atual.to_csv("Registros_Diarios2.csv", index=False)
    # Captura o arquivo modificado dataframe armazena como o novo dataframe atualizado  
    try:
        time.sleep(0.5)
        df_novo = pd.read_csv("Registros_Diarios2.csv")        
    except FileNotFoundError: pass
    
    ultimo_page_down = datetime.now()
    ciclo = 0
    #Pega os valores da nova linha e atribui as variaveis
    valores_estudo_string = df_novo.loc[df_novo.index[-1], 'Tempo de estudo']
    ciclos_de_estudos_tempos = list(map(int, valores_estudo_string.split(',')))
    return df_novo

def play_audio(file_path, volume=0.17):
    # import pygame, ja importei no comeco do codigo
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.set_volume(volume)  # Set the volume
    pygame.mixer.music.play()

#  ======================= Funcoes que alteram a interface Tkinter =========================

def refrescar_listbox_horario_refeicoes(refeicoes_registradas, listbox):
    listbox.delete(0, tk.END)  # Clear all the current meal times
    for meal_time in refeicoes_registradas: listbox.insert(tk.END, meal_time) #Add all meals
def atualizar_label_tempo_atual(total_segundos):
    if stop !=True:
        num_formatado = "{:.2f}".format(total_segundos)
        if total_segundos > 59:
            minutos_atuais = str(int((total_segundos % 3600) // 60))
            segundos_atuais = total_segundos % 60
            segundos_atuais_formatos =  "{:.2f}".format(segundos_atuais)
            texto = minutos_atuais + 'min ' + segundos_atuais_formatos + 's'
        else:
            texto = num_formatado + " seconds"
        labels[1].config(text=texto)
    else: pass
def atualizar_label_tempo_total(total_segundos): 
    # Converter total de segundos em horas, minutos e segundos
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60
    texto = f"{horas}h {minutos}min {segundos}s"
    labels[3].config(text=texto)

# =================================== Funcoes extras ========================================

# Pomodoro ou outras coisas uteis, ainda esta em desenvolvimento
def alarme(numero):
    import io
    from gtts import gTTS
    # Funcao que converte o texto em audio e armazena em um buffer de memória
    def converte_texto_em_audio(texto):
        tts = gTTS(text=texto, lang='pt')
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        play_audio(buffer, volume=0.60)
    
    minutos = numero*60 #numero da tecla x segundos

    texto_iniciou_timer = f". Iniciado o timer de {minutos} minutos"
    converte_texto_em_audio(texto_iniciou_timer)

    # Intervalo antes de executar o resto do codigo(Ou seja avisar que o alarme encerrou)
    time.sleep((60*numero))
    texto_encerrou_timer = f". Encerrou o timer de {minutos} minutos"
    converte_texto_em_audio(texto_encerrou_timer)


