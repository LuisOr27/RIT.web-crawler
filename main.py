import sqlite3
import threading
import time

import requests
import schedule
from bs4 import BeautifulSoup

import webCrawler.webCrawler
from index.index import *
from index.indexSearcher import IndexSearcher
from ux.app import create_app
from webCrawler.webCrawler import downloadFiles, get_db_connection


def job():
    """
        Call main function to be executed every 30 days
    """
    main()


def pedirNumeroEntero():
    correcto = False
    num = 0
    while not correcto:
        try:
            num = int(input("Introduce un numero entero: "))
            correcto = True
        except ValueError:
            print('Error, introduce un numero entero')

    return num

def climenu():
    salir = False
    opcion = 0
    searcher = IndexSearcher()

    while not salir:
        print("\n1. Crawler 1")
        print("2. Index 2")
        print("3. searcher 3")
        print("4. Schedule")
        print("5. IDF")
        print("6. Salir")

        print("Elige una opcion")

        opcion = pedirNumeroEntero()

        if opcion == 1:
            print("Opcion 1")
            """
                Start web crawler app
            """
            print("\n\nEntro al webCrawler\n\n")

            # webCrawler page
            mainUrl = "http://biblioteca.conare.ac.cr/index.php/recursos-electronicos/actas-conare/actas-por-ano.html"

            mainContent = requests.get(mainUrl)
            soup = BeautifulSoup(mainContent.content, 'lxml')
            years = soup.find('div', {'class': 'pd-categories-view'}).find_all('a')

            # Every year in webCrawler url that contains minutes
            for year in years:
                yearLink = 'http://biblioteca.conare.ac.cr' + year['href']
                yearContent = requests.get(yearLink)
                yearSoup = BeautifulSoup(yearContent.content, 'lxml')
                minutes = yearSoup.find('div', {'class': 'pd-category'}).find_all('div', 'pd-float')

                # Every file in the year
                for minute in minutes:
                    thread = threading.Thread(target=downloadFiles, args=(minute,))
                    thread.start()

            thread.join()
        elif opcion == 2:
            print("Index 2")
            basic_index()
            index()
        elif opcion == 3:
            # ejemplo de consulta: Presupuesto fiscal del fees testtttt
            consult = input("introduzca la consulta: ")
            print(searcher.search(consult=consult))
        elif opcion == 4:
            print("Scheduler 4")
            schedule.every(30).days.at("10:30").do(job)
            while True:
                schedule.run_pending()
                time.sleep(1)

        elif opcion == 5:
            consult = input("introduzca una palabra: ")
            print("IDF para " + consult + " = ", get_IDF(consult))


        elif opcion == 6:
            salir = True
        else:
            print("Introduce un numero entre 1 y 3")

    print("Fin")


def main():
    #climenu()
    searcher = IndexSearcher()
    app = create_app(searcher)
    app.run(debug=True)

if __name__ == "__main__":
    main()
