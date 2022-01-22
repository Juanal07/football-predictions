import requests
import re
from bs4 import BeautifulSoup

# Programa de prueba antes de la integración final en el script de Streamlit

jugador = "Daley Blind"
# jugador = "Wayne Rooney"
print(jugador)
# https://www.transfermarkt.co.uk/schnellsuche/ergebnis/schnellsuche?query=Wayne%20Rooney # No se podía usar sin JS
# https://www.bdfutbol.com/es/buscar.php?d=iker+casillas&bj=on
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
# print(datos)
datos2 = datos.find_all('div', class_='row')
print(datos2)
print('\n\n\n')
atrs = []
atrs.append(img)
campo = ["Nombre completo:", "Fecha de nacimiento:","Lugar de nacimiento:","País de nacimiento:","Altura:","Peso:","Demarcación:"]
i=0
for row in datos2:
    try:
        if campo[i]=="Nombre completo:":
            name = row.find('div', class_='col-md-9').text
            name = re.sub('  ','',name) #Hecho de forma cutre se puede cambiar a regex complejo
            name = re.sub('\n','',name)
            name = re.sub('\r','',name)
            print(name)
            atrs.append(name)
        elif campo[i]=="Demarcación:":
            name = row.find('div', class_='float-left').text
            name = re.sub('  ','',name) #Hecho de forma cutre se puede cambiar a regex complejo
            name = re.sub('\n','',name)
            name = re.sub('\r','',name)
            print(name)
            atrs.append(name)
        else:
            f = re.findall('('+campo[i]+').*\n.*">(.*)<', str(datos2))
            res=re.sub('</a>','',f[0][1])
            print(res)
            atrs.append(res)
        i += 1
    except:
        print("fallo")

    # Versión original
    # try:
    #     name = row.find('div', class_='col-md-9').text
    #     name = re.sub('  ','',name) #Hecho de forma cutre se puede cambiar a regex complejo
    #     name = re.sub('\n','',name)
    #     name = re.sub('\r','',name)
    #     print(name)
    #     atrs.append(name)
    # except:
    #     print('fin')
print(atrs)