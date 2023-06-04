import math

from index.index import binfile_to_dictionary
from webCrawler.preprocessing import preprocess_text
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

#ROOT_FOLDER = "/Users/juanpa1220/Desktop/RIT/rit-aranador-web/"
ROOT_FOLDER = "/Users/luis/Desktop/GitHub/rit-aranador-web/"
DOCS_FOLDER = ROOT_FOLDER + "docs/"
FULL_INDEX_FILE_NAME = "fullindex.txt"


class IndexSearcher:
    def __init__(self):
        """
        Initialized the reverse_index and docs_id values
        """
        self.reverse_index = binfile_to_dictionary("index_to_bin")
        self.docs_id = binfile_to_dictionary("doc_to_id")

    def search(self, consult: str):
        """
        Makes the search in the loaded index file
        :param consult: The input terms to be searched
        """
        results = []
        preprocessed_consult = self.preprocess_consult(consult)
        consult_vector = []
        print("Consulta preprocesada:", " ".join(preprocessed_consult))
        indices = []
        docs = []

        for term in preprocessed_consult:
            result_set_size = 5
            print("\nTermino a buscar:", term)
            peso_termino = self.get_peso_termino(preprocessed_consult, term)
            consult_vector.append(peso_termino)
            indices.append(self.get_indices(term))
            # documents = self.get_documents_from_index(term, result_set_size)
            # self.print_results(documents)
            # results.append(self.return_results(documents))

        print("\n\nvector consulta", consult_vector)
        # print(indices)
        docs = self.get_docs_from_result_index(indices)
        # print(docs)
        docs_vectors = self.get_docs_vectors(indices, docs)
        # print(docs_vectors)
        similitud = self.calc_similitud(consult_vector, docs_vectors)
        print(similitud)
        similitud = sorted(similitud.items(), key=lambda x: x[1], reverse=True)
        print(similitud)
        results = self.get_results(similitud)
        return results

    @staticmethod
    def preprocess_consult(consult: str) -> list:
        """
        Preprocessed the consult
        :param consult: the consult
        :return: the preprocessed consult
        """
        return preprocess_text(consult)

    def get_documents_from_index(self, term: str, result_set_size: int) -> list:
        """
        Gets the documents containing the input term form the loaded index dictionary
        :param term: the term to be search
        :param result_set_size: the number of terms to be returned as result set
        :return: a list of resulted documents
        :rtype: list
        """
        result = []
        if term in self.reverse_index.keys():
            files_and_positions = list(self.reverse_index[term])
            for item in files_and_positions:
                if result_set_size > 0:
                    result.append(item)
                    result_set_size -= 1
                else:
                    break
        return result

    def get_indices(self, term):
        if term in self.reverse_index.keys():
            return list(self.reverse_index[term])

    def print_results(self, documents: list):
        """
        Prints the resulted documents
        :param documents: the documents to be printed
        """
        if len(documents) > 0:
            print("Resultados:")
            counter = 1
            for doc in documents:
                print("Documento {0} {1}: {2}".format(counter, self.docs_id[doc[0]], doc))
                counter += 1
        else:
            print("No se encontraron resultados para este termino.")

    def return_results(self, documents: list):
        """
        return the resulted documents
        :param documents: the documents to be printed
        """
        results = []
        if len(documents) > 0:
            for doc in documents:
                my_list = [self.docs_id[doc[0]], doc]
                results.append(my_list)
        else:
            results = []
            print("No se encontraron resultados para este termino.")
        return results

    def get_peso_termino(self, preprocessed_consult, term):
        f = self.get_f(preprocessed_consult, term)
        n = len(preprocessed_consult)

        p = (1 + math.log(f, 2)) * math.log((n / f), 2)
        #p = math.log(1 + (n / f), 2)
        print("peso termino", term, ":", p)
        return p

    def get_f(self, preprocessed_consult, term):
        f = 0
        for t in preprocessed_consult:
            if t == term:
                f += 1
        return f

    def get_docs_from_result_index(self, indices):
        docs = []
        for i in indices:
            for j in i:
                doc = j[0]
                if doc not in docs:
                    docs.append(doc)
        return docs

    def get_docs_vectors(self, indices, docs):
        vectors = {}
        for doc in docs:
            vectors[doc] = self.get_pesos(indices, doc)
        return vectors

    def get_pesos(self, indices, doc):
        pesos = []
        for i in indices:
            for j in i:
                if j[0] == doc:
                    pesos.append(j[1])
                    break

        while len(pesos) != len(indices):
            pesos.append(0)

        return pesos

    def calc_similitud(self, consult_vector, docs_vectors):
        results = {}

        if len(consult_vector) > 1:
            array_vec_1 = np.array([consult_vector])
            for key in docs_vectors.keys():
                v_doc = docs_vectors[key]
                array_vec_2 = np.array([v_doc])
                similitud = cosine_similarity(array_vec_1, array_vec_2)
                similitud = similitud[0][0]
                results[key] = similitud
        else:
            for key in docs_vectors.keys():
                results[key] = docs_vectors[key][0]

        return results

    def get_results(self, similitud):
        result = []
        print(len(similitud))
        if len(similitud) == 0:
            return result
        if len(similitud) > 20:
            n = 20
            for s in similitud:
                if n == 0:
                    continue
                result.append(self.docs_id[s[0]])
                n -= 1
        else:
            for s in similitud:
                result.append(self.docs_id[s[0]])
        return result
