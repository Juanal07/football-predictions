import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os

shootResults=["Todos","Goal","OwnGoal","MissedShot","BlockedShot","SavedShot","ShotOnPost"]
shootTipe=["Todos","RightFoot","LeftFoot","Head","OtherBodyPart"]

def launchSparkGoals(jugador, tipoGol, parteCuerpo):
    os.system("python shots.py " + str(jugador) +" "+ str(tipoGol)+" "+ str(parteCuerpo))


def scatter_plot(goles):

    x = np.array(goles["positionX"] * 1.4)
    y = np.array(goles["positionY"] * 0.9)

    img = plt.imread("./images/pitch.png")
    fig, ax = plt.subplots(facecolor="none")
    ax.imshow(img, zorder=0, extent=[0, 1.4, 0, 0.9])
    ax.scatter(x, y, zorder=1, color="#0086ff")
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    st.pyplot(fig)


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
tipoGol = st.selectbox("Escoja el tipo de disparo",
    options=shootResults
)
parteCuerpo = st.selectbox("Escoja el miembro con el que disparo",
    options=shootTipe
)

# st.write(f"You selected option {jugador} called {format_func(jugador)}")
# st.write(jugador)

if st.button("Obetener shoots"):
    launchSparkGoals(jugador, tipoGol, parteCuerpo)
    st.experimental_rerun()
try:
    scatter_plot(goles)
except:
    st.write("Selecciones un jugador")
