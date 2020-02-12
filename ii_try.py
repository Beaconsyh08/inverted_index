import re


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
        terms = clean_text.split(' ')
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
        return {term: self.index[term] for term in query.split(' ') if term in self.index}


def highlight_term(id, term, text):
    # Highlight color "\033[0m" --> reset all
    replaced_text = text.replace(term, "\033[1;32;40m {term} \033[0m".format(term=term))
    return "--- document {id}: {replaced}".format(id=id, replaced=replaced_text)


if __name__ == '__main__':
    db = Database()
    index = InvertedIndex(db)
    document1 = {
        'id': '1',
        'text': 'The big sharks of Belgium drink beer.'
    }
    document2 = {
        'id': '2',
        'text': 'Belgium has great beer. They drink beer all the time.'
    }
    index.index_document(document1)
    index.index_document(document2)

    while True:
        search_term = input("Enter term(s) to search: ")
        result = index.lookup_query(search_term)

        if result:
            for term in result.keys():
                for appearance in result[term]:
                    # print(appearance)
                    document = db.get(appearance.doc_id)
                    print(highlight_term(appearance.doc_id, term, document['text']))
                print("-----------------------------")
        else:
            print("\033[1;31;40m NO MATCH \033[0m")
