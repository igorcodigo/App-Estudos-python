import tkinter as tk

# Root =============================================================================
def create_and_configure_root():
    root = tk.Tk()
    # Initialize the main window
    root.title('Daily Schedule')
    root.grid_columnconfigure(0, weight=1)
    root.iconbitmap('Midias\Livro Fechado.ico')
    return root

#Frames / Containers ========================================================================
def create_and_configure_frames(root):
    # Frame dos tempos
    tempo_frame = tk.Frame(root)
    tempo_frame.grid(row=0, column=0)

    # Frame for meal times
    meal_frame = tk.LabelFrame(root, text="Horario das refeicoes do dia", padx=10, pady=10)
    meal_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
    meal_frame.grid_columnconfigure(0, weight=1)
    meal_frame.grid_rowconfigure(0, weight=1)
    return tempo_frame,meal_frame

#Labels =============================================================================
def create_and_configure_labels(tempo_frame):
    time_labels = [("Tempo do ciclo atual", 1), ("Iniciando . . .", 2), ("Tempo total de estudos do dia", 3),("Sem dados", 4)]
    labels = []
    for text, r in time_labels:
        if r == 2 or r == 4:
            label_objeto = tk.Label(tempo_frame, text=text, padx=5, pady=2, anchor='center', font=("Helvetica", 16))
        else:
            label_objeto = tk.Label(tempo_frame, text=text, relief="solid", bd=1, padx=5, pady=2, anchor='w')
        label_objeto.grid(row=r, column=0, sticky="nsew", pady=5, padx=11)
        labels.append(label_objeto)
    return labels


# =================== Funcao para criar os objetos da interface configurados ============
def criar_objetos_da_interface():
    root = create_and_configure_root()
    tempo_frame, meal_frame = create_and_configure_frames(root)
    labels = create_and_configure_labels(tempo_frame)
    # Lista para refeicoes ===========================================================
    meal_listbox = tk.Listbox(meal_frame)
    meal_listbox.grid(row=0, column=0, sticky="nsew")
    return root,tempo_frame,meal_frame,labels,meal_listbox
