from personal_collections.heap_priority_queue import HeapPriorityQueue
from personal_collections.suffix_tree import SuffixTree


class DNAContamination():

    # ------------------------------- DNAContamination concrete methods -------------------------------

    def __init__(self, s, l):
        """Create an initially empty DNAContamination"""
        self._threshold = l
        self._string = s
        self.C = []
        self._heap = HeapPriorityQueue()
        self.suffix_tree = SuffixTree([s])

    def addContaminant(self, c):
        """Add the contaminant c to the set C and saves the degree of contamination of s by c"""
        self.C.append(c)
        commons = self.suffix_tree._common_maximal_substrings(c[1], self._threshold)
        if (commons != 0):
            self._heap.add(-commons, c[0])

    def getContaminants(self, k):
        """Return the k contaminants with larger degree of contamination among the added contaminants"""
        app = []
        contaminants = []
        for i in range(k):
            try:
                cont = self._heap.remove_min()
                contaminants.append(cont[1])
                app.append(cont)
            except:
                break
        for a in app:
            self._heap.add(a[0], a[1])
        return contaminants
