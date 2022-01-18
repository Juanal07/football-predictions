import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os

os.system("python start-spark.py")

name = "goals-test"
goles = pd.read_csv("output/{}.csv".format(name))
goles
image = "./images/pitch.png"
img = plt.imread(image)

def launchSparkGoals():
    os.system("python shots.py")


def scatter_plot(goles):

    x = np.array(goles["positionX"] * 1.4)
    y = np.array(goles["positionY"] * 0.9)

    img = plt.imread("./images/pitch.png")
    fig, ax = plt.subplots(facecolor='none')
    ax.imshow(img, zorder=0, extent=[0, 1.4, 0, 0.9])
    ax.scatter(x, y, zorder=1, color="#0086ff")
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    st.pyplot(fig)

if st.button('Lanzar spark'):
        launchSparkGoals()
        st.experimental_rerun()


scatter_plot(goles)
