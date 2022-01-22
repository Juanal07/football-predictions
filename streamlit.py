from lib2to3.pgen2 import driver
from urllib import request
from attr import attributes
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
    # print(datos2)
    attributes.append(img)
    campo = ["Nombre completo:", "Fecha de nacimiento:","Lugar de nacimiento:","País de nacimiento:","Altura:","Peso:","Demarcación:"]
    i=0
    for row in campo:
        print(datos.index(row))
        try:
            if campo[i]=="Nombre completo:":
                name = row.find('div', class_='col-md-9').text
                name = re.sub('  ','',name) #Hecho de forma cutre se puede cambiar a regex complejo
                name = re.sub('\n','',name)
                name = re.sub('\r','',name)
                print(name)
                attributes.append(name)
            elif campo[i]=="Demarcación:":
                try:
                    pos = re.findall('"float-left">((\w+|\w+.\w+))</div', str(row))
                    print(pos[0])
                    attributes.append(pos[0][1])
                except:                    
                    pos = re.findall('"float-left">((\w+))</div', str(row))
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
            i += 1
        except:
            print("fallo")
            attributes.append("No hay datos")
    print(attributes)
    

def updatePlayers():
    os.system("python start-spark.py")


def format_func(option):
    return CHOICES[option]


if st.button("Actualizar jugadores"):
    updatePlayers()
    st.experimental_rerun()

name = "goals-test"
try:
    goles = pd.read_csv("output/{}.csv".format(name))
except:
    goles = pd.DataFrame()

tabla = goles.drop(goles.columns[[0, 2, 6, 7]], axis=1)
tabla
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
tipoGol = st.selectbox("Escoja el resultado del disparo", options=shootResults)
parteCuerpo = st.selectbox("Escoja cómo se realizó el disparo", options=shootTipe)

# st.write(f"You selected option {jugador} called {format_func(jugador)}")
# st.write(jugador)

if st.button("Obtener disparos"):
    launchSparkGoals(jugador, tipoGol, parteCuerpo)
    st.experimental_rerun()

# Mostramos los datos del Webscrapper
atrs = []
scrap(format_func(jugador), atrs)
print("Lista final")
# Para eliminar porblemas con dobles nacionalidades
# if len(atrs)>8:
#     atrs.pop(5)
print(atrs)

st.image(atrs[0])
st.write("Nombre Completo: "+ atrs[1])
st.write("Fecha de Nacimiento, Edad: "+ atrs[2])
st.write("Ciudad de Nacimiento: "+ atrs[3])
st.write("Nacionalidad: "+ atrs[4])
st.write("Altura: "+ atrs[5])
st.write("Peso: "+ atrs[6])
st.write("Posción: "+ atrs[7])

try:
    scatter_plot(goles)
except:
    st.write("Selecciones un jugador")
