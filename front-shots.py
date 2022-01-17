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
    # Create numpy array for the visualisation
    x = np.array(goles["positionX"])
    y = np.array(goles["positionY"])
    # y = np.array([99, 86, 87, 88, 111, 86, 103, 87, 94, 78, 77, 85, 86])

    fig = plt.figure(figsize=(20, 4))

    img = plt.imread("./images/pitch.png")
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[0, 1.2, 0, 1])
    ax.scatter(x, y, color="#e0b034")
    # plt.show()

    # fig.add_subplot(111, facecolor=img)
    # plt.xlim(0, 1)
    # plt.ylim(0, 1)
    # plt.scatter(x, y)

    st.pyplot(fig)


scatter_plot(goles)
