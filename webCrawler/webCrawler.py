import sqlite3

import requests
from webCrawler.preprocessing import *

visitedLinks = []

def get_db_connection():
    """
    create database first by running init_db.py
    @return: sqlite conection objetct
    """
    conn = sqlite3.connect('webCrawler/webcrawler.db')
    conn.row_factory = sqlite3.Row
    return conn

def getVisitedLinks():
    """
        Get a list of the visited links, so that it doesn't have to visite them again.
        Output: list with all visited links or an empty list in case there are not visited links
    """
    try:
        with open('webCrawler/visitedLinks.txt') as linksFile:
            vList = list(linksFile)
        finalList = [i.strip() for i in vList]
        linksFile.close()
        return finalList
    except:
        linksFile = open('webCrawler/visitedLinks.txt', 'w')
        linksFile.close()
        return []

def downloadFiles(minute):
    """
        Download files from the given url and preprocessed them
        Input: link where the link of the file is store
    """
    downloadLink = 'http://biblioteca.conare.ac.cr' + minute.find('a')['href']

    # get links previously visited
    visitedLinks = getVisitedLinks()

    if downloadLink not in visitedLinks:
        fileName = minute.getText()
        fileContent = requests.get(downloadLink).content

        # write minute content in a file
        file = open('original_files/' + fileName, 'wb')
        file.write(fileContent)
        file.close()

        # add link to visited links
        visitedLinks.append(downloadLink)

        visitedLinksFile = open('webCrawler/visitedLinks.txt', 'a')
        visitedLinksFile.write(downloadLink + '\n')
        visitedLinksFile.close()

        try:
            with sqlite3.connect("webCrawler/webcrawler.db") as con:
                cur = con.cursor()
                cur.execute("INSERT OR IGNORE INTO actas (fileName, downloadLink) VALUES(?, ?)", (fileName, downloadLink))
                con.commit()
        except:
            pass

        preprocess_documents(fileName)
        # print("Documento: " , fileName, " preprocesado")
