import os
import re
import codecs
import uuid
import pickle
import ast
from math import log

# CAMBIAR "/Users/juanpa1220/Desktop/RIT/rit-aranador-web/"  ### CAMBIAR
ROOT_FOLDER = "/Users/luis/Desktop/GitHub/rit-aranador-web/"
#ROOT_FOLDER = "/Users/juanpa1220/Desktop/RIT/rit-aranador-web/"
DOCS_FOLDER = ROOT_FOLDER + "docs/"
PREPROCESSED_FILES_FOLDER = ROOT_FOLDER + "preprocessed_files/"


def index():
    """
    Crea o actualiza el índice invertido completo
    """
    # cargar el contenido del índice invertido
    reverse_index = binfile_to_dictionary("index_to_bin")

    # cargar el contenido de los id de los docs
    docs_id = binfile_to_dictionary("doc_to_id")

    # crea o actualiza el índice según sea el caso
    fullreverseindex, documentids = full_index(reverse_index, docs_id)

    # guardar los diccionarios como txt
    print_to_txt("fullindex.txt", fullreverseindex)
    print_to_txt("doc_id.txt", documentids)

    # crear archivo binario del index
    dictionary_to_binfile("index_to_bin", fullreverseindex)
    dictionary_to_binfile("doc_to_id", documentids)


def basic_index():
    """
    Crea el índice básico
    """
    reverse_index = {}
    for filename in os.listdir(PREPROCESSED_FILES_FOLDER):
        vocabulary = {}
        vocabulary = index_document(filename)

        for term in vocabulary:
            if term in reverse_index:
                if filename in reverse_index[term].keys():
                    reverse_index[term][filename] = reverse_index[term].get(
                        filename) + 1
                else:
                    reverse_index[term].update(
                        {filename: vocabulary.get(term)})

            if term not in reverse_index:
                reverse_index[term] = {filename: vocabulary.get(term)}

    # imprimir a txt -> falta guardar en binario
    name = "index.txt"
    mode = 'a' if os.path.exists(DOCS_FOLDER + name) else 'w+'
    with codecs.open(DOCS_FOLDER + name, mode, encoding="utf-8", errors='replace') as text_file:
        print(reverse_index, file=text_file)
        text_file.close()


def index_document(filename):
    """
    sacar cantidad de terminos para indice basico
    vocabulary diccionario [termino : frecuencia]
    """
    vocabulary = {}
    try:
        with open(os.path.join(PREPROCESSED_FILES_FOLDER, filename),
                  'r') as f:
            text = f.read()
            rgx = re.compile("(\w[\w']*\w|\w)")
            words = rgx.findall(text)
            f.close()
    except:
        f = open(PREPROCESSED_FILES_FOLDER, filename)
        f.close()

    for word in words:
        if word not in vocabulary.keys():
            vocabulary[word] = 1
        if word in vocabulary.keys():
            vocabulary[word] = vocabulary.get(word) + 1

    return vocabulary


def get_tf(frequency):
    """
    Calcula el TF de cada palabra del documento usando la fórmula: 1 + log2(fij)
    Input:
        frecuency frecuencia del término en el documento
    Output:
        valor del TF para el término
    """
    tf_value = 0
    if frequency > 0:
        tf_value = 1 + log(frequency, 2)

    return tf_value


def get_tf_normalized(frequency, max_frequency):
    """
    Calcula el TF de cada palabra del documento usando la fórmula: frecuencia / maximo de frecuencia en un documento
    Input:
        frecuency frecuencia del término en el documento, max_term_in_document es la frecuencia máxima en un documento
    Output:
        valor del TF para el término
    """
    tf_value_normalized = 0
    if frequency > 0:
        tf_value_normalized = frequency / max_frequency

    return round(tf_value_normalized, 4)


def get_IDF(term, d, N):
    """
    Calcula el IDF de cada palabra del vocabulario usando la fórmula: log2(frecuencia/total de documentos)
    Input:
        un término (palabra)
    Output:
        valor del IDF para el término
    """
    idf_value = 0
    consult = search_term_index(d, term)
    if consult != 0:
        ni = len(consult)
        idf_value = log((N / ni), 2)
    return idf_value

def getN():
    N = 0
    dir = ROOT_FOLDER + "preprocessed_files/"
    for path in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, path)):
            N += 1
    return N


def full_index(reverse_index, documentids):
    """
    Crea el índice invertido completo
    Input:
        reverse_index índice invertido anterior
        documentids diccionario con id de documentos anterior
    Input:
        reverse_index actualización del índice invertido
        documentids actualización del diccionario con id de documentos
    """
    N = getN()
    d = getD()
    for filename in os.listdir(PREPROCESSED_FILES_FOLDER):
        # si el documento ya está en el índice invertido lo ignora
        if filename not in documentids.values():
            vocabulary, max_term_frequency = index_document_locations(filename)
            uuid_value = uuid.uuid1()
            documentids[uuid_value] = filename

            for term in vocabulary:
                positions = vocabulary.get(term)
                frequency = len(positions)
                tf_value = get_tf(frequency)
                # tf_value_normalized = get_tf_normalized(frequency, max_term_frequency)
                peso = tf_value * get_IDF(term, d, N)
                if term in reverse_index:
                    aux_index = 0
                    for line in reverse_index[term]:
                        if line[1] <= peso:
                            reverse_index[term].insert(
                                aux_index, [uuid_value, peso, positions])
                            break
                        elif aux_index > len(reverse_index[term]):
                            reverse_index[term].append(
                                [uuid_value, peso, positions])
                            break
                        aux_index = aux_index + 1

                if term not in reverse_index:
                    reverse_index[term] = [
                        [uuid_value, peso, positions]]
                # print(reverse_index[term])

    return reverse_index, documentids


def index_document_locations(filename):
    """
    Obtienen las posiciones de los términos de un archivo
    Input:
        filename nombre del archivo
    Output:
        diccionario con las posiciones de cada término del documento y la frecuencia máxima en un documento.
    """
    vocabulary = {}
    words = ''
    max_frequency = 0

    try:
        with open(os.path.join(PREPROCESSED_FILES_FOLDER, filename),
                  'r') as f:
            try:
                text = f.read()

                rgx = re.compile("(\w[\w']*\w|\w)")

                words = rgx.findall(text)
                f.close()
            except:
                print('Archivo ignorado por error de codificación\n')
    except:
        f = open(PREPROCESSED_FILES_FOLDER, filename)
        f.close()

    for word in words:
        locations = []
        if word in vocabulary.keys():
            pass
        if word not in vocabulary.keys():
            locations = [i for i, x in enumerate(words) if x == word]
            vocabulary[word] = locations
            if len(locations) > max_frequency:
                max_frequency = len(locations)

    return [vocabulary, max_frequency]


def print_to_txt(name, reverse_index):
    """
    Almacena un diccionario en un documento txt
    Input:
        name nombre del archivo a crear
        reverse_index índice invertido a guardar
    """
    mode = 'a' if os.path.exists(DOCS_FOLDER + name) else 'w+'
    with codecs.open(DOCS_FOLDER + name, mode, encoding="utf-8", errors='replace') as text_file:
        print(reverse_index, file=text_file)
        text_file.close()


def dictionary_to_binfile(name, reverse_index):
    """
    Almacena un diccionario en un archivo binario
    Input:
        name nombre del archivo a crear
        reverse_index índice invertido a guardar
    """
    try:
        geeky_file = open(DOCS_FOLDER + name, 'wb')
        pickle.dump(reverse_index, geeky_file)
        geeky_file.close()

    except:
        print("Something went wrong")


def binfile_to_dictionary(name):
    """
    Almacena el contenido de un archivo binario en un diccionario
    Input:
        name nombre del archivo binario a leer
    Output:
        diccionario previamente creado o {} si no había un archivo binario
    """
    try:
        with open(DOCS_FOLDER + name, 'rb') as handle:
            data = handle.read()
        # Se convierte los datos a un diccionario
        dictionary_data = pickle.loads(data)
        handle.close()

        return dictionary_data
    except FileNotFoundError:
        return {}


def search_term_index(d, term):
    """
    busca un termino en el índice
    Input:
        una palabra
    Output:
        los documentos que contienen ese termino
    """
    result = d.get(term)
    if result:
        return result
    else:
        return 0

def getD():
    """
    busca un termino en el índice
    Input:
        una palabra
    Output:
        los documentos que contienen ese termino
    """
    with open(DOCS_FOLDER + "index.txt", 'r') as f:
        data = f.read()
    d = ast.literal_eval(data)
    return d