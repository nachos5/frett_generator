from bs4 import BeautifulSoup as bs4

from . import takn


def frett_html(frett_malsgreinar):
    """
    Tekur við lista af málsgreinum og skilar html kóða.
    """
    base = '<!DOCTYPE html><html><head></head><body><div id="frett_container"></div></body></html>'
    soup = bs4(base, features="html.parser")
    container = soup.find("div")

    for malsgrein in frett_malsgreinar:
        ordmyndir = []
        prev_mark = ""

        for tvennd in malsgrein:
            # viljum aldrei stófan staf í byrjun orðs nema það sé sérnafn eða á eftir punkti
            ordmynd = tvennd[0]
            mark = tvennd[1]
            if not (
                (mark[0] == "n" and "s" in mark)
                or (mark == "e")
                or (prev_mark == ".")
                or (malsgrein.index(tvennd) == 0)
            ):
                ordmyndir.append(ordmynd.lower())
            else:
                ordmyndir.append(ordmynd[0].upper() + ordmynd[1:])
            prev_mark = mark

        ordmyndir_strengur = takn(" ".join(ordmyndir))
        # "wröppum" málsgreininni í p-tag
        malsgrein_p_tag = soup.new_tag("p")
        malsgrein_p_tag.string = ordmyndir_strengur
        container.append(malsgrein_p_tag)

    return soup.prettify()

