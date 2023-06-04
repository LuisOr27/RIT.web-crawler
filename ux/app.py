import sqlite3
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import json, sys
import requests
from flask_wtf import FlaskForm
from wtforms import widgets, SelectMultipleField
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT_FOLDER = "/Users/luis/Desktop/GitHub/rit-aranador-web/"
#ROOT_FOLDER = "/Users/juanpa1220/Desktop/RIT/rit-aranador-web/"


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class SimpleForm(FlaskForm):
    string_of_files = ['one\r\ntwo\r\nthree\r\n']
    list_of_files = string_of_files[0].split()
    # create a list of value/description tuples
    files = [(x, x) for x in list_of_files]
    example = MultiCheckboxField('Label', choices=files)

def get_db_connection():
    """
    create database first by running init_db.py
    @return: sqlite conection objetct
    """
    conn = sqlite3.connect('ux/database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_webcrawler_connection():
    """
    create database first by running init_db.py
    @return: sqlite conection objetct
    """
    conn = sqlite3.connect(ROOT_FOLDER+"webCrawler/webcrawler.db")
    conn.row_factory = sqlite3.Row
    return conn

def precision_P_to_N(list,max):
    count = 0
    for element in list:
        if int(element) <= max:
            count = count +1
        else: break
    return count/max

def grafic(y,search):
    x = [5,10,20]
    col = (np.random.random(), np.random.random(), np.random.random())
    plt.plot(x,y,c=col,label=search)
    plt.legend(loc="upper left")
    plt.xlabel('Cantidad de documentos')
    plt.ylabel('Precisión')
    plt.title("Grafico para la consulta: "+search)
    plt.xlim([5,20])
    plt.ylim([0,1])
    plt.savefig(ROOT_FOLDER + "ux/static/images/graficos/new_plot.jpg")

def grafic_P_to_N(y,y2,y3):
    plt.cla()
    plt.clf()
    file_path = os.path.join(ROOT_FOLDER+"ux/static/images/graficos/", "history_plot.jpg")
    os.remove(file_path)
    #plt.clf()
    len1 = len(y)
    x = list(np.arange(1,len1+1))
    plt.plot(x,y, "-b",label="P@5")
    plt.plot(x, y2, "-r", label="P@10")
    plt.plot(x, y3, "-y", label="P@20")
    plt.legend(loc="upper left")
    plt.xlabel('Cantidad de consultas')
    plt.ylabel('Precisión')
    plt.title("Métricas del historial de consultas")
    plt.ylim([0,1])
    plt.savefig(ROOT_FOLDER + "ux/static/images/graficos/history_plot.jpg")
    plt.close()
    plt.cla()
    plt.clf()

def convert_select_to_list(num):
    conn = get_db_connection()
    if num ==1:
        posts = conn.execute('SELECT P_5 FROM record')
    elif num == 2:
        posts = conn.execute('SELECT P_10 FROM record')
    else:
        posts = conn.execute('SELECT P_20 FROM record')

    rows = posts.fetchall();
    final_result = [i[0] for i in rows]
    conn.close()
    return final_result


def create_app(searcher_instance):
    """Create and configure an instance of the Flask application.
    @rtype: object
    """

    app = Flask(__name__, instance_relative_config=True)
    SECRET_KEY = 'development'
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SEARCHER'] = searcher_instance
    bootstrap = Bootstrap(app)

    @app.route('/example', methods=['post', 'get'])
    def hello_world():
        form = SimpleForm()
        if form.validate_on_submit():
            print(form.example.data)
            return render_template("success.html", data=form.example.data)
        else:
            print("Validation Failed")
            print(form.errors)
        return render_template('example.html', form=form)

    @app.route("/about")
    def about():
        """
        about page
        @return:
        """
        return render_template("about.html")

    @app.route('/')
    def new_search():
        """

        @return: homepage for search
        """
        return render_template('search.html')

    @app.route('/addrecsearch', methods=['POST', 'GET'])
    def addrecsearch():
        """
        form to display serch results and add to record database
        @return:
        """
        if request.method == 'POST':
            try:
                search = request.form['search']
                msg = "Record successfully added"

            except:
                msg = "error in insert operation"

            finally:
                msg = "Record successfully added"
                files = app.config['SEARCHER'].search(search)

                # extraer nombres de los files sin el .txt
                actas = []
                for file in files:
                    x = file.rsplit(".", 1)
                    actas.append(x[0])

                # buscar los urls de las actas
                urls = []

                for acta in actas:
                    conn = get_webcrawler_connection()
                    posts = conn.execute("SELECT filename, downloadLink FROM actas WHERE filename LIKE ?", (acta,))
                    rows = posts.fetchall()
                    urls.append(rows[0])
                    conn.close()

        return render_template('searchresult.html', value=search, msg=msg, files=files, urls=urls)

    @app.route('/addrecresults', methods=['POST', 'GET'])
    def addrecresults():
        """
        form to safe the metrics results
        @return:
        """

        if request.method == 'POST':
            try:
                search = request.form['search']
                checks = request.form.getlist('relevance')
                P_5 = precision_P_to_N(checks, 5)
                P_10 = precision_P_to_N(checks, 10)
                P_20 = precision_P_to_N(checks, 20)
                grafic([P_5,P_10,P_20],search)
                with sqlite3.connect("ux/database.db") as con:
                    cur = con.cursor()

                    cur.execute("INSERT INTO record (search,p_5,p_10,p_20) VALUES(?,?,?,?)", (search, P_5, P_10, P_20))

                    con.commit()
                    msg = "Record successfully added"
            except:
                msg = "error in insert operation"
                files = ""

            finally:
                msg = "Record successfully added"

        app.config['UPLOAD_FOLDER'] = 'static/images'
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'graficos/new_plot.jpg')
        return render_template('metricsresult.html',user_image = full_filename,msg=msg)

    @app.route('/record')
    def record():
        """

        @return: ver historial de busquedas
        """

        conn = get_db_connection()
        posts = conn.execute('SELECT * FROM record')
        rows = posts.fetchall();


        conn.close()
        return render_template("record.html", rows=rows)

    @app.route('/graphics')
    def graphics():
        """
        @return: ver graficas
        """

        grafic_P_to_N(convert_select_to_list(1),convert_select_to_list(2),convert_select_to_list(3))
        app.config['UPLOAD_FOLDER'] = 'static/images'
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'graficos/history_plot.jpg')
        return render_template("graphics.html",image = full_filename)

    @app.route('/fileurls')
    def fileurls():
        """

        @return: ver fileurls
        """

        conn = get_webcrawler_connection()
        posts = conn.execute('SELECT * FROM actas')
        rows = posts.fetchall();
        conn.close()
        return render_template("fileurls.html", rows=rows)


    '''
    #ejemplos de otra pagina con bootstrap y js
    @app.route('/index')
    def index():
        return render_template('index.html',name='index')


    @app.route('/query/', methods=['GET'])
    def query():
        if request.method == 'GET':
            has_result = 0
            error = 0
            q = request.args.get('q')
            start_index = request.args.get('start')
            # read engineID
            f = open('data/engine.json')
            s = json.load(f)

            for i in range(len(s['engine'])):
                sn = 'engine_' + str(i + 1)
                key = s['engine'][i][sn]['key']
                cx = s['engine'][i][sn]['cx']
                engine_name = s['engine'][i][sn]['name']

                # search request
                url = "https://www.googleapis.com/customsearch/v1"
                if start_index:
                    query_string = {"key": key, "cx": cx, "num": "10", "q": q, "start": start_index}
                else:
                    query_string = {"key": key, "cx": cx, "num": "10", "q": q}
                response = requests.request("GET", url, params=query_string)
                json_data = json.loads(response.text)

                try:
                    # case 1: results
                    if json_data['items']:
                        has_result = 1
                        break
                except:
                    # case 2: error
                    try:
                        json_data['error']
                        if i == len(s['engine']) - 1:
                            error = 1
                            # print json_data
                            error_msg = 'error_code' + str(json_data['error']['code'])
                            return render_template('index.html', q=q, error=error, error_msg=error_msg,
                                                   engine_name=engine_name)
                        else:
                            continue
                    # case 3: no result
                    except:
                        break

            if has_result == 1:
                # print "results"
                result = []
                results = []
                items = json_data['items']
                current_start_index = json_data['queries']['request'][0]['startIndex']
                page_index = (current_start_index - 1) / 10 + 1
                # print "page is : " + str(page_index)
                if current_start_index == 1:
                    has_previous = 0
                    search_info = 'About ' + json_data['searchInformation']['formattedTotalResults'] + ' results (' + \
                                  json_data['searchInformation']['formattedSearchTime'] + ' seconds)'
                else:
                    has_previous = 1
                    search_info = "Page " + str(current_start_index / 10 + 1) + ' of About ' + \
                                  json_data['searchInformation']['formattedTotalResults'] + ' results (' + \
                                  json_data['searchInformation']['formattedSearchTime'] + ' seconds)'
                # print(items)
                for item in items:
                    result = {"title": item['htmlTitle'], "link": item['link'], "displayLink": item['htmlFormattedUrl'],
                              "snippet": item['htmlSnippet']}
                    try:
                        for k in item['pagemap'].keys():
                            # print(typeof(k))
                            if k == 'cse_thumbnail':
                                print('has thumbnail!')
                                result["thumbnail"] = item['pagemap']['cse_thumbnail'][0]
                                result["thumbnail"]["height"] = int(item['pagemap']['cse_thumbnail'][0]['height'])
                    except Exception as e:
                        print('%s : %s' % (Exception, e))
                    results.append(result)
                    result = {}
                return render_template('index.html', q=q, results=results, error=error, engine_name=engine_name,
                                       search_info=search_info, has_previous=has_previous,
                                       current_start_index=current_start_index, page_index=page_index)
            else:
                search_info = 'About ' + json_data['searchInformation']['formattedTotalResults'] + ' results (' + \
                              json_data['searchInformation']['formattedSearchTime'] + ' seconds)'
                return render_template('index.html', q=q, error=error, engine_name=engine_name, search_info=search_info)

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    '''
    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)