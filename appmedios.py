import streamlit as st
import requests
import openai
import time
import json
from PIL import Image
from io import BytesIO
import tweepy  # Para X, configura auth

# Configura tus API keys
NEWS_API_KEY = "tu-newsapi-key"
OPENAI_API_KEY = "tu-openai-key"
openai.api_key = OPENAI_API_KEY

# Título de la app
st.title("Ecosistema Mediático - Ejército de Noticias")
st.write("Por André Granda (@andregrandag) - Guayaquil, EC")

# Sidebar para configs
st.sidebar.header("Configuraciones")
query = st.sidebar.text_input("Query para Alertas", value="alerta: Guayaquil noticias")
estilo_post = st.sidebar.selectbox("Estilo de Post", ["Viral", "Formal", "Informativo"])
plataformas = st.sidebar.multiselect("Plataformas", ["Facebook", "X", "Blog"], default=["X"])

# Sección: Buscador de Alertas en Tiempo Real
st.header("Alertas de Noticias en Tiempo Real")
if st.button("Buscar/Actualizar Alertas"):
    with st.spinner("Buscando noticias..."):
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&sortBy=publishedAt"
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json()['articles'][:5]  # Últimas 5
            st.session_state['alertas'] = [{"titulo": a['title'], "contenido": a['description'], "fecha": a['publishedAt']} for a in articles]
        else:
            st.error("Error en NewsAPI")

if 'alertas' in st.session_state:
    for alerta in st.session_state['alertas']:
        with st.expander(alerta['titulo']):
            st.write(alerta['contenido'])
            st.write(f"Fecha: {alerta['fecha']}")
            if st.button("Generar Post e Imagen", key=alerta['titulo']):
                # Generar Post
                prompt_post = f"Genera un post para {', '.join(plataformas)} en estilo {estilo_post}: {alerta['titulo']} - {alerta['contenido']}"
                response_post = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt_post}])
                post_texto = response_post.choices[0].message.content
                st.subheader("Post Generado")
                st.write(post_texto)

                # Generar Imagen
                prompt_imagen = f"Imagen viral para noticia: {alerta['titulo']}"
                response_imagen = openai.Image.create(prompt=prompt_imagen, n=1, size="512x512")
                imagen_url = response_imagen['data'][0]['url']
                img_response = requests.get(imagen_url)
                img = Image.open(BytesIO(img_response.content))
                st.image(img, caption="Imagen Generada")

                # Placeholder para Publicar (e.g., en X)
                if "X" in plataformas and st.button("Publicar en X"):
                    # Configura Tweepy (agrega tu auth aquí)
                    auth = tweepy.OAuth1UserHandler("consumer_key", "consumer_secret", "access_token", "access_token_secret")
                    api = tweepy.API(auth)
                    api.update_status(status=post_texto)  # Agrega imagen si quieres: api.update_with_media()
                    st.success("Publicado en X!")

# Auto-refresh para real-time (cada 60s)
if st.sidebar.checkbox("Activar Auto-Refresh (cada 60s)"):
    time.sleep(60)
    st.rerun()

# Sección: Medidor de Impacto (Placeholder)
st.header("Medidor de Impacto")
st.write("Aquí irían métricas reales de posts publicados. Por ahora, simulado.")
st.metric("Likes", 150)
st.metric("Shares", 50)

# Publicación Masiva
st.header("Publicación Masiva")
if st.button("Publicar Todas las Alertas"):
    st.write("Simulando publicación masiva... (implementa loop sobre alertas)")
