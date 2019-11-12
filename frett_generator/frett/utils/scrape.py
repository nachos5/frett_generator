import requests
import time

from bs4 import BeautifulSoup as bs4
from nltk.tokenize import word_tokenize

from django.conf import settings

from . import Markari
from ..models import Flokkur, Malsgrein


def mbl_frettatenglar(fretta_id="2381464", countdown=2):
    """ Aðferð sem skilar lista af mbl fréttum, aðferðin er endurkvæm, því hærra sem countdown gildið er,
        þeim mun fleiri fréttum er skilað """

    # stöðvunarskilyrði vegna endurkvæmninar
    if countdown == 0:
        return []

    print("Sæki tengla...")
    base_url = "https://www.mbl.is"
    # mbl sækir fleiri fréttir í gegnum API svona (dæmi um einn tengil)
    url = "{base_url}/frettir/post_news2/frettir-innlent/gmn/?p={fretta_id}&count=12&slug=&container_id=None".format(
        base_url=base_url, fretta_id=fretta_id
    )
    response = requests.get(url)
    time.sleep(0.25)
    soup = bs4(response.text, "html.parser")
    tenglar = []
    tenglar_divs = soup.findAll("div", {"class": "media smt mb-2"})
    for tengill_div in tenglar_divs:
        # a taggið með fréttunum er fyrsta taggið undir þessum divum
        tengill = tengill_div.find("a")
        tenglar.append(base_url + tengill["href"])
    # á hverjum og einum tengli er svo id til að sækja meira á forminu GMN_lastid=2381330; í script taggi
    next_id = soup.find("script").text.split("=")[1][:-1]
    # endurkvæmni
    tenglar += mbl_frettatenglar(fretta_id=next_id, countdown=countdown - 1)

    return tenglar


def mbl_frett(
    markari,
    flokkur="innlent",
    url="https://www.mbl.is/frettir/innlent/2019/11/10/afram_skelfur_jord_vid_oskju_einn_maeldist_3_4/",
):
    """ Tekur við slóð á frétt og vistar málsgreinar (tokens og mörk) hennar í gagnagrunninum """

    response = requests.get(url)
    soup = bs4(response.text, "html.parser")
    efni = soup.find("div", {"class": "main-layout"}).findAll("p")

    flokkur_obj = Flokkur.objects.get(nafn=flokkur)
    for malsgrein in efni:
        tokens = word_tokenize(malsgrein.text)
        mork = [markari.marka_token(token) for token in tokens]
        if len(tokens) == 0 or len(mork) == 0:
            continue
        # setjum málgreinina í gagnagrunninn
        Malsgrein.objects.create(
            flokkur=flokkur_obj,
            tokens=settings.ADSKILNADARTAKN.join(tokens),
            mork=settings.ADSKILNADARTAKN.join(mork),
        )
        print("Málsgrein sett í gagnagrunninn")


def mbl_frettir():
    """ Aðferð sem sækir fréttatengla og setur allar málgreinar úr öllum fréttunum í gagnagrunninn """

    markari = Markari()
    tenglar = mbl_frettatenglar(countdown=100)
    for tengill in tenglar:
        mbl_frett(markari, url=tengill)
