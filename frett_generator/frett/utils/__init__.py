import os
import zipfile

import pandas as pd

from django.conf import settings


class Markari:
    """ Þessi klasi geymir SH-sniðið frá BÍN og markar eftir því """

    def __init__(self, *args, **kwargs):
        # lesum sh-sniðið
        shsnid = os.path.join(settings.STATIC_ROOT, "maltaekni-gogn/SHsnid.csv.zip")
        zf = zipfile.ZipFile(shsnid)
        df = pd.read_csv(zf.open("SHsnid.csv"), sep=";")
        df.columns = [
            "uppflettiord",
            "audkenni",
            "ordflokkur",
            "hluti",
            "beygingarmynd",
            "mark",
        ]
        self.df = df

    def marka_token(self, ordmynd):
        # leitum í dataframe-inum
        rod = self.df.loc[self.df["beygingarmynd"] == ordmynd]
        if not rod.empty:
            mark = rod["mark"].values[0]
        else:
            # fannst ekkert mark
            mark = settings.VILLU_MARK

        return mark

