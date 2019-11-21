import itertools
import os
import time
import zipfile

from collections import Counter
from operator import itemgetter

import pandas as pd

from django.conf import settings


class Markari:
    """ 
    Þessi klasi geymir gullstaðalinn og markar eftir honum.
    
    Dæmi um notkun:
    m = Markari(n=5) # default n skilgreint í settings
    m.marka("hestur")
    m.reset_prev() # til að "gleyma"
    """

    def __init__(self, *args, **kwargs):
        # fjöldi "orðsamhengis" (bigram etc.)
        if "n" in kwargs and kwargs["n"] >= 2:
            n = kwargs.pop("n")
        else:
            n = settings.DEFAULT_N_MORKUN
        self.n = n
        # lesum gullstaðalinn
        gull = os.path.join(settings.STATIC_ROOT, "maltaekni-gogn/MIM-GOLD-1_0.zip")
        zf = zipfile.ZipFile(gull)
        data = []
        for zipinfo in zf.filelist:
            filename = zipinfo.filename
            with zf.open(filename) as f:
                # fyrir hverja skrá í gullstaðlinum geymum við tvenndir á forminu (orðmynd, mark)
                # í lista sem við geymum svo í heildarlistanum data
                tuples = [
                    (
                        line.decode("utf8").split("\t")[0].strip(),
                        line.decode("utf8").split("\t")[-1].strip(),
                    )
                    for line in f
                ]
                data.append(tuples)

        # höfum bara einn stóran lista af tvenndum
        data = list(itertools.chain(*data))

        # til að n-tagga þarf að geyma gögnin svona
        # hvert stak eru n orð hlið við hlið
        shift_lists = []
        for i in range(self.n):
            shift_lists.append(data[i:])
        n_data = list(zip(*shift_lists))
        # geymum í dicti á forminu (tvennd):fjöldi
        n_data = Counter(n_data)
        # látum markarann geyma n-1 síðustu mörkin sem hann markaði
        self.prev = []

        self.data = n_data

    def reset_prev(self):
        """ 
        markarinn man það sem hann markaði áður og notar þær upplýsingar
        til að m-marka, kalla á þetta fall til að "gleyma".
        """
        self.prev = []

    def marka(self, ordmynd, n=-1):
        if n == -1:
            n = self.n
        # erum ekki með nægt samhengi til að nota þetta n
        if len(self.prev) < n - 1:
            # förum í n-ið fyrir neðan
            return self.marka(ordmynd, n - 1)
        # sækjum öll þau tilvik sem orðmyndin kemur fyrir sem n-ta orðið
        x = [
            (key, value)
            for key, value in self.data.items()
            if len(key[0][0]) > 0 and key[n - 1][0].lower() == ordmynd.lower()
        ]
        # fannst ekkert
        if not x:
            # skilum villu ef n = 1
            if n == 1:
                self.reset_prev()
                return settings.VILLUMARK
            # annars tékkum n-ið fyrir neðan
            else:
                self.reset_prev()
                return self.marka(ordmynd, n - 1)

        if n == 1:
            y = x
        else:
            y = []
        # sækjum þau tilvik þar sem fyrri orðið eru tögguð með prev mörkunum
        for i in range(len(self.prev)):
            for key, value in x:
                if key[i][1] == self.prev[i]:
                    y.append((key, value))
        # ef það fannst eitthvað finnum við það sem kemur oftast fyrir
        if y:
            z = max(y, key=itemgetter(1))
        # annars notum við n-ið fyrir neðan (endurkvæmni)
        else:
            self.reset_prev()
            return self.marka(ordmynd, n - 1)

        mark = z[0][n - 1][1]

        # uppfærum prev
        self.prev.append(mark)
        self.prev = self.prev[-n:]
        if len(self.prev) == self.n:
            self.prev = self.prev[1:]

        return mark


def takn(strengur):
    return (
        strengur.replace(" .", ".")
        .replace(" ,", ",")
        .replace(" !", "!")
        .replace(" ?", "?")
        .replace(" ;", ";")
        .replace(" :", ":")
        .replace("( ", "(")
        .replace(") ", ")")
        .replace("[ ", "[")
        .replace("] ", "]")
        .replace(" %", "%")
    )

