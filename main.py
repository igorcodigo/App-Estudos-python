import threading
from interface_modulo import criar_objetos_da_interface
from keyboard_module import keyboard_listener
from funcoes_modulo import configuracao_inicial,adicionando_tempos, armazena_no_csv,calcular_tempo_ciclo

def on_close_window():
    if calcular_tempo_ciclo() > 0: armazena_no_csv(int(calcular_tempo_ciclo()))
    root.destroy()

root,tempo_frame,meal_frame,labels,meal_listbox = criar_objetos_da_interface()
# Configura o evento de fechamento da janela para chamar a funçã on_close_window
root.protocol("WM_DELETE_WINDOW",on_close_window)

# Cria e inicia uma thread que executa a função adicionando_tempo em paralelo
threading.Thread(target=adicionando_tempos, daemon=True).start()
# Inicia a thread para a função keyboard_listener
threading.Thread(target=keyboard_listener, daemon=True).start()


    
widgets_interface = root,tempo_frame,meal_frame,labels,meal_listbox
configuracao_inicial(widgets_interface)
root.mainloop()