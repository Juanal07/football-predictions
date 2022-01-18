import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os
import ftfy


def launchSparkGoals(opcion):
    os.system("python shots.py " + str(opcion))


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
goles = pd.read_csv("output/{}.csv".format(name))
goles
image = "./images/pitch.png"
img = plt.imread(image)

# TODO: checkear encoding para que funcionen las comillas Eunan O'Kane
players = pd.read_csv("./data/FootballDatabase/players.csv", encoding="latin1")

zip_iterator = zip(players["playerID"], players["name"])
d = dict(zip_iterator)
CHOICES = d

option = st.selectbox(
    "Select option",
    options=list(CHOICES.keys()),
    format_func=format_func,
)
st.write(f"You selected option {option} called {format_func(option)}")
st.write(option)

if st.button("Obetener shoots"):
    launchSparkGoals(option)
    st.experimental_rerun()

scatter_plot(goles)
