import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from functions import *
from matplotlib.figure import Figure
from PIL import Image

# Variables globales
error_traces = []  # Inicializar la lista de trazas con errores

# Función para crear un gráfico aleatorio
def create_random_plot():
  
    trace = trace_var.get()
    topics= lda_model.get()
    
    ax.clear()  # Limpiar el gráfico anterior

    data=TplPionier(config=config.ds_medium).index
    error_indexes=list(data[data['ERROR'] == True].index) 
    if trace in error_indexes:
        error_label='True'
    else:
        error_label='False'

    corpus=load_corpus( instrument='Pionier', size='medium')
    trace_logs = corpus.tokens.iloc[trace]

    #import the topics per log for the trace given
    topics_pertrace= load_topic_list(num_topics=topics)
    if not topics_pertrace:
        return None 
    
    trace_topics = topics_pertrace[trace]

    #graph settings:
    num_logs = len(trace_logs)
    #fig, ax = plt.subplots(figsize=(25, 5))
    for i in range(num_logs):
        topic = trace_topics[i]
        log = trace_logs[i]
        color = f'C{topic}'
        ax.bar(i, 1, color=color, edgecolor='black')
        ax.text(i, 0.5,f' {topic}', ha='center', va='center',fontsize=10)
    ax.set_xlim([-0.5, num_logs-0.5])
    ax.set_ylim([0, 1])
    ax.set_xlabel('Log')
    ax.set_ylabel('Tópico')
    ax.set_title(f'Topics per trace {trace}. Number of logs {num_logs}. ERROR: {error_label}, LDA {topics} topics')
  
    canvas.draw()  # Dibujar el gráfico en el lienzo

def generate_full_error():
    full_model_window = tk.Toplevel(root)
    full_model_window.title("Gráfico Aleatorio")
    topic= lda_model.get()

    #ax.clear()  # Limpiar el gráfico anterior
    fig = plt.figure(figsize=(15, 5))
    ax = fig.add_subplot(111)

    image_path = f"C:\\Users\\rlagos\\Desktop\\Mandinga\\Testeo_LDA\\NLP\\LDA\\plots\\LDA_{topic}\\ERRORS_{topic}.png"
    image = Image.open(image_path)
    #ax.clear()
    plt.imshow(image) 
    plt.axis('off')
    ax.set_title(f' LDA {topic} topics, ERROR TRACES')

    # Agregar la figura a la ventana de Tkinter
    canvas = FigureCanvasTkAgg(fig, master=full_model_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

def non_errors_graphs():
    full_model_window_2 = tk.Toplevel(root)
    full_model_window_2.title("Gráfico Aleatorio")

    topic= lda_model.get()
    graph_type=type_nonerror_combobox.get()

    fig = plt.figure(figsize=(15, 5))
    ax = fig.add_subplot(111)

    if str(graph_type) == 'Random Plot':
        suffix='RANDOM'

    elif str(graph_type) == 'Longer traces':
        suffix='LONGEST'
    
    elif str(graph_type) == 'Shorter traces':
        suffix='SHORTEST'

    image_path = f"C:\\Users\\rlagos\\Desktop\\Mandinga\\Testeo_LDA\\NLP\\LDA\\plots\\LDA_{topic}\\NON_ERRORS_{suffix}.png"
    image = Image.open(image_path)
    #ax.clear()
    plt.imshow(image) 
    plt.axis('off')
    ax.set_title(f' LDA {topic} topics, {suffix} TRACES')

    canvas = FigureCanvasTkAgg(fig, master=full_model_window_2)
    canvas.draw()
    canvas.get_tk_widget().pack()


# Función para buscar trazas con ERROR
def search_error_traces():
    global error_traces
    # Simulación de búsqueda de trazas con ERROR
    data=TplPionier(config=config.ds_medium).index
    error_indexes=list(data[data['ERROR'] == True].index) 

    trace_combobox['values'] = error_indexes

# Configuración de la interfaz
root = tk.Tk()
root.title('Painting Logs')

############
painting_logs = tk.Label(root, text="Painting Logs", font=("Courier New", 12))
painting_logs.place(x=10, y=10)
painting_logs.config(bg="pink")
#########

########## Topic selection ###################
lda_model=tk.IntVar()
lda_combobox= ttk.Entry(root, textvariable=lda_model)
lda_combobox.place(x=310, y=20)

lda_label= tk.Label(root, text="Select topics: (3-4-10)")
lda_label.place(x=310, y=0)
##############################################

########## Trace selection ###################
trace_var = tk.IntVar()
trace_entry = ttk.Entry(root, textvariable=trace_var)
trace_entry.place(x=160, y=20)

models_label_2 = tk.Label(root, text="Select a trace: 0-2845")
models_label_2.place(x=160, y=0)

trace_combobox = ttk.Combobox(root, values=list(range(2401)))
trace_combobox.place(x=1350, y=30)
###############################################

# Alineación del tercer botón en la esquina superior derecha
search_error_button = tk.Button(root, text='Search Error Traces', command=search_error_traces)
search_error_button.pack(anchor='se')

# Alineación del botón Change Model centrado y abajo de las barras de búsqueda
change_model_button = tk.Button(root, text='Generate Model', command=create_random_plot)
change_model_button.pack(anchor="n")
change_model_button.config(width=15, height=2)

# Crear un lienzo para el gráfico
fig = plt.figure(figsize=(15, 5))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

button_frame = tk.Frame(root)
button_frame.pack(pady=20)

generate_full_model_button = tk.Button(button_frame, text="All traces error", command=generate_full_error)
generate_full_model_button.pack(side=tk.LEFT, padx=10)

generate_model2_button = tk.Button(button_frame, text="Generate Model 2", command=non_errors_graphs)
generate_model2_button.pack(side=tk.LEFT, padx=10)

type_nonerror_combobox = ttk.Combobox(button_frame, values=["Random Plot", "Longer traces", "Shorter traces"])
type_nonerror_combobox.pack(side=tk.LEFT, padx=10)

# Mostrar la interfaz
root.mainloop()













