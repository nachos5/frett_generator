import itertools
import os
import zipfile

from collections import Counter
from operator import itemgetter

import pandas as pd

from django.conf import settings


class Markari:
    """ Þessi klasi geymir gullstaðalinn og markar eftir honum """

    def __init__(self, *args, **kwargs):
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
        # geymum hann svo í dicti á forminu (tvennd):fjöldi
        single_data = Counter(data)

        # til að "bigram" tagga þarf að geyma gögnin svona
        # hvert stak eru tvö orð hlið við hlið
        bi_data = list(zip(data, data[1:]))
        # geymum í dicti á forminu (tvennd):fjöldi
        bi_data = Counter(bi_data)
        # látum markarann geyma síðasta markið sem hann skilaði
        self.prev = None

        # til að "trigram" tagga þarf að geyma gögnin svona
        # hvert stak eru tvö orð hlið við hlið
        bi_data = list(zip(data, data[1:]))
        # geymum í dicti á forminu (tvennd):fjöldi
        bi_data = Counter(bi_data)
        # látum markarann geyma síðasta markið sem hann skilaði
        self.prev = None

        self.single_data = single_data
        self.bi_data = bi_data

    def marka(self, ordmynd):
        # sækjum öll þau tilvik sem orðmyndin kemur fyrir
        x = [
            (key, value) for key, value in self.single_data.items() if key[0] == ordmynd
        ]
        # fannst ekkert
        if not x:
            return settings.VILLUMARK

        # fáum og skilum því sem kemur oftast fyrir
        x = max(x, key=itemgetter(1))
        mark = x[0][1]
        self.prev = mark
        return mark

    def bigram_marka(self, ordmynd):
        if not self.prev:
            return self.marka(ordmynd)
        # sækjum öll þau tilvik sem orðmyndin kemur fyrir sem seinna orðið
        x = [
            (key, value) for key, value in self.bi_data.items() if key[1][0] == ordmynd
        ]
        # fannst ekkert
        if not x:
            return settings.VILLUMARK

        # sækjum þau tilvik þar sem fyrra orðið er taggað með prev markinu
        y = [(key, value) for key, value in x if key[0][1] == self.prev]
        # ef það fannst eitthvað finnum við það sem kemur oftast fyrir
        if y:
            z = max(y, key=itemgetter(1))
        # annars notum við bara "einmarkara"
        else:
            return self.marka(ordmynd)

        mark = z[0][1][1]
        self.prev = mark
        return mark
