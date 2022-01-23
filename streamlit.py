import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
import os
import requests
import re
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="Fútbol Big Data",
    page_icon="⚽",
)

shootResults = [
    "Todos",
    "Goal",
    "OwnGoal",
    "MissedShots",
    "BlockedShot",
    "SavedShot",
    "ShotOnPost",
]
shootTipe = ["Todos", "RightFoot", "LeftFoot", "Head", "OtherBodyPart"]


def confidence_ellipse(x, y, ax, n_std=3.0, facecolor='none', **kwargs):

    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensionl dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, **kwargs)

    # Calculating the stdandard deviation of x from
    # the squareroot of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    # calculating the stdandard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)

def launchSparkGoals(jugador, tipoGol, parteCuerpo):
    os.system(
        "python shots.py " + str(jugador) + " " + str(tipoGol) + " " + str(parteCuerpo)
    )


def scatter_plot(goles):
    try:
        x = np.array(goles["positionX"] * 1.05)
        y = np.array(goles["positionY"] * 0.68)
        fig, ax = plt.subplots(facecolor="none")
        ax.scatter(x, y, zorder=1, color="#ffc45d")
        img = plt.imread("./images/pitch.png")
        ax.imshow(img, zorder=0, extent=[0, 1.05, 0, 0.68])
        confidence_ellipse(x, y, ax, edgecolor='red')
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        st.pyplot(fig)
    except:
        x = np.array(goles["positionX"] * 1.05)
        y = np.array(goles["positionY"] * 0.68)
        fig, ax = plt.subplots(facecolor="none")
        ax.scatter(x, y, zorder=1, color="#ffc45d")
        img = plt.imread("./images/pitch.png")
        ax.imshow(img, zorder=0, extent=[0, 1.05, 0, 0.68])
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        st.pyplot(fig)

def scrap(jugador, attributes):
    print(jugador)
    jugador = re.sub(' ','+', jugador)
    URL = 'https://www.bdfutbol.com/es/buscar.php?d='+jugador+'&bj=on'
    print(URL)
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    # print(soup)
    tabla = soup.find('table')
    # print(tabla)
    linkJugador = tabla.find('a')['href']
    linkJugador = 'https://www.bdfutbol.com/es/'+linkJugador
    print(linkJugador)

    pageJugador = requests.get(linkJugador)
    soupJugador = BeautifulSoup(pageJugador.content, 'html.parser')
    # print(soupJugador)
    img = soupJugador.find('div', class_="carousel-inner")
    img = img.find('img')['src']
    img = 'https://www.bdfutbol.com/'+img[6:]
    print(img)

    datos = soupJugador.find('div', class_="col taula-dades pl-0 pr-0 pb-0 pt-0 pt-2 pb-2 d-flex align-items-center")
    datos2 = datos.find_all('div', class_='row')
    datos2.pop(-2)
    print(len(datos2))
    attributes.append(img)
    campo = ["Nombre completo:", "Fecha de nacimiento:","Lugar de nacimiento:","País de nacimiento:","Altura:","Peso:","Demarcación:"]
    i=0
    for row in campo:
        try:
            if row=="Nombre completo:":
                name = datos2[i].find('div', class_='col-md-9').text
                name = re.sub('  ','',name) #Hecho de forma cutre se puede cambiar a regex complejo
                name = re.sub('\n','',name)
                name = re.sub('\r','',name)
                print(name)
                attributes.append(name)
            elif row=="Demarcación:":
                try:
                    pos = re.findall('"float-left">((\w+|\w+.\w+))</div', str(datos2))
                    print(pos[0])
                    attributes.append(pos[0][1])
                except:                    
                    pos = re.findall('"float-left">((\w+))</div', str(datos2))
                    print(pos)
                    attributes.append(pos[0])
            else:
                try:
                    data = re.findall('('+campo[i]+').*\n.*">(.*)<', str(datos2))
                    res=re.sub('</a>','',data[0][1])
                    print(res)
                    attributes.append(res)
                except:
                    attributes.append("No hay datos")
        except:
            print("fallo")
            attributes.append("No hay datos")
        i += 1
    print(attributes)
    

def updatePlayers():
    os.system("python start-spark.py")

def updatePrediciones():
    os.system("python predictionModel.py")


def format_func(option):
    return CHOICES[option]

# Inicio de HTML

secciones= ["Introducción", "Localización de Disparos", "Predicción de Precios"]

st.sidebar.title("Menú")
menu = st.sidebar.radio(options=secciones, index=0, label="Elija que desea mostrar")

if menu=="Introducción":
    st.write("""
        # Bienvenido a nuestro trabajo de Final Big Data!\n
        👋 En esta web encontrará información sobre datasets de fútbol europeo.\n
        🌅 La información se ha obtenido de datasets de Kaggle y webscrapers. \n
        📄 Para más info consulte la memoria adjunta al código entregado.\n
        👈 En la barra lateral podrá ir navegando por las distintas opciones desarrolladas""")

if menu=="Localización de Disparos":

    st.title("Localización de Disparos")

    st.markdown("En la siguiente página podrá seleccionar un jugador y se le mostrarán todos los disparos que haya efectuado.\
                Adicionalmete, podrá filtrar por el tipo de disparo efectuado y el resultado del mismo.")


    st.caption("En este botón podrá actualizar la lista de jugadores del desplegable, para añadir si se han añadido nuevos a la lista.")
    if st.button("Actualizar jugadores"):
        updatePlayers()
        st.experimental_rerun()

    name = "goals-test"
    try:
        goles = pd.read_csv("output/{}.csv".format(name))
    except:
        goles = pd.DataFrame()

    tabla = goles.drop(goles.columns[[0, 2, 6, 7]], axis=1)
    # tabla
    image = "./images/pitch.png"
    img = plt.imread(image)

    # TODO: checkear encoding para que funcionen las comillas Eunan O'Kane
    players = pd.read_csv("./data/FootballDatabase/players.csv", encoding="latin1")

    zip_iterator = zip(players["playerID"], players["name"])
    d = dict(zip_iterator)
    CHOICES = d

    jugador = st.selectbox(
        "Escoja un jugador",
        options=list(CHOICES.keys()),
        format_func=format_func,
    )

    c1, c2= st.columns(2)
    tipoGol = c1.selectbox("Escoja el resultado del disparo", options=shootResults)
    parteCuerpo = c2.selectbox("Escoja cómo se realizó el disparo", options=shootTipe)

    # st.write(f"You selected option {jugador} called {format_func(jugador)}")
    # st.write(jugador)

    if st.button("Obtener disparos"):
        launchSparkGoals(jugador, tipoGol, parteCuerpo)
        st.experimental_rerun()

    # Mostramos los datos del Webscrapper
    atrs = []
    scrap(format_func(jugador), atrs)

    st.subheader("Datos del jugador")

    col1, col2 = st.columns(2)

    col1.image(atrs[0])
    col2.write("Nombre Completo: "+ atrs[1])
    col2.write("Fecha de Nacimiento, Edad: "+ atrs[2])
    col2.write("Ciudad de Nacimiento: "+ atrs[3])
    col2.write("Nacionalidad: "+ atrs[4])
    col2.write("Altura: "+ atrs[5])
    col2.write("Peso: "+ atrs[6])
    col2.write("Posción: "+ atrs[7])

    st.subheader("Campo de tiros")

    try:
        scatter_plot(goles)
        st.subheader("Tabla de tiros")
        tabla
    except:
        st.write("Selecciones un jugador")

if menu=="Predicción de Precios":
    st.title("Predicción de Precios")

    st.markdown("En esta página se predicen los valores de mercado de los jugadores de las \
        ligas europeas. Primeramente se muestran todo ellos en una tabla junto con sus \
        estadísticas más relevantes y luego se puede seleccionar un jugador en concreto para \
        verlo con más detalle.")

    st.subheader("Tabla de predicciones de precios")

    file = "players2_predicted"
    predsDF = pd.read_csv("output/{}.csv".format(file))

    # tablaPreds = predsDF.drop(predsDF.columns[[0, 2, 6, 7]], axis=1)
    tablaPreds = predsDF.filter(predsDF.columns[[1,24,9,8]])
    tablaPreds

    st.caption("En este botón podrá actualizar las prediciones de jugadores.")
    if st.button("Actualizar prediciones"):
        updatePrediciones()
        st.experimental_rerun()

    st.subheader("Precio predecido del jugador €")

    predictions = pd.read_csv(path)

    zip_iterator2 = zip(predictions["player_id"], predictions["pretty_name"])
    d2 = dict(zip_iterator2)
    CHOICES = d2

    prediccion = st.selectbox(
        "Escoja un jugador",
        options=list(CHOICES.keys()),
        format_func=format_func,
    )

    # st.write(f"You selected option {prediccion} called {format_func(prediccion)}")

    jPred = predictions.loc[predictions["player_id"]==prediccion]
    # print(jPred)
    # st.write(jPred)
    precio = float(jPred["prediction"])*1.19
    formatted_float = "{:,.2f} €".format(precio)
    # print(formatted_float)
    colp1, colp2 = st.columns(2)
    colp1.write(":euro: Predecimos que su precio en el mercado es:")
    colp2.subheader(formatted_float)
    # Mostramos los datos del jugador
    st.subheader("Datos del jugador")
    dp1, dp2 = st.columns(2)
    pName = jPred.iloc[0]["pretty_name"]
    # print(pName)
    dp1.write("Nombre del jugador: "+ pName)
    pNac = jPred.iloc[0]["date_of_birth"]
    dp1.write("Fecha de Nacimiento: "+ pNac)
    pPais = jPred.iloc[0]["country_of_citizenship"]
    dp1.write("País de Nacimiento: "+ pPais)
    pPos = jPred.iloc[0]["position"]
    dp1.write("Posición: "+ pPos)
    pSub = jPred.iloc[0]["sub_position"]
    dp1.write("Subposición: "+ pSub)
    pPie = jPred.iloc[0]["foot"]
    dp1.write("Pie: "+ pPie)
    pAlt = jPred.iloc[0]["height_in_cm"]
    dp1.write("Altura (cm): "+ str(pAlt))

    gt = jPred.iloc[0]["total_goals"]
    dp2.write("Goles totales: "+ str(gt))
    gg = jPred.iloc[0]["g/g"]
    dp2.write("Goles por partido: "+ str(round(gg,3)))
    yg = jPred.iloc[0]["y/g"]
    dp2.write("Tarjetas amarillas por Partido: "+ str(round(yg,3)))
    rg = jPred.iloc[0]["r/g"]
    dp2.write("Tarjetas rojas por Partido: "+ str(round(rg,3)))
    mg = jPred.iloc[0]["m/g"]
    dp2.write("Minutos por partido: "+ str(round(mg,3)))
    ta = jPred.iloc[0]["total_assists"]
    dp2.write("Asistencias totales: "+ str(ta))
    ag = jPred.iloc[0]["a/g"]
    dp2.write("Asistencias por Partido: "+ str(round(ag,3)))
    gs = jPred.iloc[0]["g/s"]
    dp2.write("Partidos por temporada: "+ str(round(gs,2)))