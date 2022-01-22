from lib2to3.pgen2 import driver
from urllib import request
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
import os

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
        ax.scatter(x, y, zorder=1, color="#0086ff")
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
        ax.scatter(x, y, zorder=1, color="#0086ff")
        img = plt.imread("./images/pitch.png")
        ax.imshow(img, zorder=0, extent=[0, 1.05, 0, 0.68])
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        st.pyplot(fig)

def scrap(jugador):
    print(jugador)
    

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
tipoGol = st.selectbox("Escoja el tipo de disparo", options=shootResults)
parteCuerpo = st.selectbox("Escoja el miembro con el que disparo", options=shootTipe)

# st.write(f"You selected option {jugador} called {format_func(jugador)}")
# st.write(jugador)

scrap(format_func(jugador))

if st.button("Obetener shoots"):
    launchSparkGoals(jugador, tipoGol, parteCuerpo)
    st.experimental_rerun()
try:
    scatter_plot(goles)
except:
    st.write("Selecciones un jugador")
