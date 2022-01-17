import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

name = "goles-messi"
goles = pd.read_csv("output/{}.csv".format(name))
goles
image = "./images/pitch.png"
img = plt.imread(image)


def scatter_plot(goles):

    x = np.array(goles["positionX"] * 2)
    y = np.array(goles["positionY"])

    img = plt.imread("./images/pitch.png")
    fig, ax = plt.subplots()
    ax.imshow(img, zorder=0, extent=[0, 2, 0, 1])
    ax.scatter(x, y, zorder=1, color="#0086ff")
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    st.pyplot(fig)


scatter_plot(goles)
