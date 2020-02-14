import re
import time
from tqdm import tqdm
from functools import reduce


class Appearance:
    """
    Represents the appearance of a term in a given document, along with the
    frequency of appearances in the same one.
    """

    def __init__(self, doc_id, frequency):
        self.doc_id = doc_id
        self.frequency = frequency

    def __repr__(self):
        """
        String representation of the Appearance object
        """
        return str(self.__dict__)


class Database:
    """
    In memory database representing the already indexed documents.
    """

    def __init__(self):
        self.db = dict()

    def __repr__(self):
        """
        String representation of the Database object
        """
        return str(self.__dict__)

    def get(self, id):
        return self.db.get(id, None)

    def add(self, document):
        """
        Adds a document to the DB.
        """
        return self.db.update({document['id']: document})

    def remove(self, document):
        """
        Removes document from DB.
        """
        return self.db.pop(document['id'], None)


class InvertedIndex:
    """
    Inverted Index class.
    """

    def __init__(self, db):
        self.index = dict()
        self.db = db

    def __repr__(self):
        """
        String representation of the Database object
        """
        return str(self.index)

    def index_document(self, document):
        """
        Process a given document, save it to the DB and update the index.
        """

        # Remove punctuation from the text.
        clean_text = re.sub(r'[^\w\s]', '', document['text'])
        # # If English
        # terms = clean_text.split(' ')
        # If Chinese
        terms = [t for t in clean_text]

        # 2-gram terms+
        two_gram_terms = []
        # print(terms)
        for index, term in enumerate(terms):
            if index % 5 == 4:
                continue
            else:
                two_gram_terms.append("".join(terms[index:index + 2]))
        terms += two_gram_terms
        terms[:] = (value for value in terms if value != "")

        # print(terms)
        appearances_dict = dict()
        # Dictionary with each term and the frequency it appears in the text.
        for term in terms:
            term_frequency = appearances_dict[term].frequency if term in appearances_dict else 0
            appearances_dict[term] = Appearance(document['id'], term_frequency + 1)

        # Update the inverted index
        update_dict = {key: [appearance] if key not in self.index else self.index[key] + [appearance] for
                       (key, appearance) in appearances_dict.items()}
        self.index.update(update_dict)
        # Add the document into the database
        self.db.add(document)
        # print(appearances_dict)
        return document

    def lookup_query(self, query):
        """
        Returns the dictionary of terms with their correspondent Appearances.
        This is a very naive search since it will just split the terms and show
        the documents where they appear.
        """
        # all_terms = re.findall(r"[\w']+", query)
        terms = re.findall(r"[\w']+", query)
        # delimiter = list(set([t for t in query]) - set(terms))
        # print("delimiter:", delimiter)

        return {term: self.index[term] for term in terms if term in self.index}


def highlight_term(id, terms, text):
    # Highlight color "\033[0m" --> reset all

    for term in terms:
        text = text.replace(term, "\033[1;32;40m{term}\033[0m".format(term=term))
    return "--- document {id}: {replaced}".format(id=id, replaced=text)


def input_from_file(path):
    file_object = open(path, 'r', encoding='UTF-8')
    return file_object


def delimiter_processor(query, result, index):
    # “@” means "or"
    # TODO Could consider about more complicated logic, and or together or with parentheses

    doc_ids = []
    frequency_counts = []
    for values in result.values():
        frequency_counts.append(len(values))
        for apperance in values:
            doc_ids.append(apperance.doc_id)

    if "&" in query:
        intersection_ids_count = {}
        result_ids = []
        for id in doc_ids:
            # appearance times equal to length of query terms
            intersection_ids_count[id] = doc_ids.count(id)

        print(intersection_ids_count)
        for item in intersection_ids_count:
            if intersection_ids_count[item] == len(result.values()):
                result_ids.append(item)

        # print(result_ids)
    else:
        result_ids = list(set(doc_ids))
        list.sort(result_ids)

    # TODO: RANKING HERE


    document_ranking(result_ids, frequency_counts, result, index)
    for result_id in result_ids:
        document = db.get(result_id)
        # print(list(result.keys()))
        print(highlight_term(result_id, list(result.keys()), document['text']))
    print("-----------------------------")


# TODO: return by length or threshold limit
def document_ranking(result_ids, frequency_counts, result, index):
    # tf-idf: wd,t = fd,t and 𝑤q,t = N/ft
    wql_lst = []
    for frequency in frequency_counts:
        # 𝑤q,t = N/ft
        wqt = len(result_ids) / frequency

    term_no = len(result.values())
    doc_no = len(result_ids)
    fre_lsts = [[0 for j in range(term_no)] for i in range(doc_no)]

    for term_pos, values in enumerate(result.values()):
        for apperance in values:
            for doc_pos in range(len(result_ids)):
                if apperance.doc_id == result_ids[doc_pos]:
                    fre_lsts[doc_pos][term_pos] = apperance.frequency

    print("final_fre_lst", fre_lsts)

    """
    一&春&雨
    """


def poem_file_processor(file):
    with tqdm(total=136362) as p_bar:
        for line_number, line in enumerate(file):
            document = {
                'id': line_number,
                'text': line.strip().replace(" ", "")
            }

            # For testing
            # if line_number == 100:
            #     break

            index.index_document(document)
            p_bar.update(1)
    file.close()


if __name__ == '__main__':
    db = Database()
    index = InvertedIndex(db)
    poem_file = input_from_file("poem.txt")
    poem_file_processor(poem_file)

    while True:
        search_term = input("Enter term(s) to search (Delimiter: \033[1;31mAND-\"&\", OR-\"@\"\033[0m):")
        result = index.lookup_query(search_term)

        if result:
            delimiter_processor(search_term, result, index)
        else:
            print("\033[1;31;40mNO MATCH\033[0m")
