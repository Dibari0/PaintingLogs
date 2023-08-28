import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
import numpy as np

# Leer la base de datos de trazas
traces = pd.read_csv('traces.csv')

# Preprocesamiento de datos
texts = [trace.split() for trace in traces['log_trace']]
texts = [' '.join(text) for text in texts]

# Convertir los textos en una matriz de frecuencia de términos (term frequency matrix)
vectorizer = CountVectorizer()
tf_matrix = vectorizer.fit_transform(texts)

# Ajustar el modelo LDA
num_topics = 5
lda_model = LatentDirichletAllocation(n_components=num_topics, max_iter=10, random_state=42)
lda_model.fit(tf_matrix)

# Obtener los tópicos y las palabras más relevantes de cada tópico
top_words = 10
feature_names = vectorizer.get_feature_names()
topics = []
for topic_idx, topic in enumerate(lda_model.components_):
    topic_top_words = [feature_names[i] for i in topic.argsort()[:-top_words - 1:-1]]
    topics.append((topic_idx, topic_top_words))

# Mostrar los tópicos y las palabras más relevantes de cada tópico
for topic in topics:
    print(f'Topic {topic[0]}: {" ".join(topic[1])}')

# Obtener la distribución de tópicos para cada traza
topic_distribution = lda_model.transform(tf_matrix)

# Graficar la distribución de tópicos para cada traza
plt.figure(figsize=(10, 6))
plt.bar(np.arange(len(topic_distribution)), topic_distribution[:,0], color='b', alpha=0.5, label='Topic 0')
plt.bar(np.arange(len(topic_distribution)), topic_distribution[:,1], bottom=topic_distribution[:,0], color='g', alpha=0.5, label='Topic 1')
plt.bar(np.arange(len(topic_distribution)), topic_distribution[:,2], bottom=topic_distribution[:,:2].sum(axis=1), color='r', alpha=0.5, label='Topic 2')
plt.bar(np.arange(len(topic_distribution)), topic_distribution[:,3], bottom=topic_distribution[:,:3].sum(axis=1), color='c', alpha=0.5, label='Topic 3')
plt.bar(np.arange(len(topic_distribution)), topic_distribution[:,4], bottom=topic_distribution[:,:4].sum(axis=1), color='m', alpha=0.5, label='Topic 4')
plt.xlabel('Traces')
plt.ylabel('Topic distribution')
plt.title(f'Topic distribution for {num_topics} topics')
plt.legend()
plt.show()