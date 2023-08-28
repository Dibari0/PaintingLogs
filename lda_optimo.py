import pandas as pd
import numpy as np
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt

# Leer la base de datos de trazas
traces = pd.read_csv('traces.csv')

# Preprocesamiento de datos
texts = [trace.split() for trace in traces['log_trace']]
texts = [' '.join(text) for text in texts]

# Convertir los textos en una matriz de frecuencia de términos (term frequency matrix)
vectorizer = CountVectorizer()
tf_matrix = vectorizer.fit_transform(texts)

# Obtener el rango de número de tópicos que queremos probar
min_topics = 2
max_topics = 10

# Iterar sobre cada número de tópicos y calcular la perplejidad
perplexities = []
for num_topics in range(min_topics, max_topics+1):
    lda_model = LatentDirichletAllocation(n_components=num_topics, max_iter=10, random_state=42)
    lda_model.fit(tf_matrix)
    perplexity = lda_model.perplexity(tf_matrix)
    perplexities.append(perplexity)

# Crear el gráfico de perplejidad vs. número de tópicos
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(range(min_topics, max_topics+1), perplexities, marker='o')
ax.set_xlabel('Number of topics')
ax.set_ylabel('Perplexity')
ax.set_title('Perplexity vs. Number of Topics')

# Mostrar el gráfico
plt.show()
