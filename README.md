# Fréttasmiður

Fréttasmiðurinn er lokaverkefni Guðmundur Óla Norlands fyrir áfangann **Inngangur að máltækni** í *Háskóla Íslands*. Hann er vefforrit sem sér um að smíða fréttir fyrir þig! Gögnin sem smiðurinn nýtir eru einungis frá mbl.is eins og stendur. Gögnin eru mörkuð með hjálp *Gullstaðalsins*: http://malfong.is/?pg=gull

Tilgangur verkefnisins er að athuga hversu lesanlegan og áhugaverðan texta má framleiða með því að nota einungis orðasafn frá íslenskum fréttamiðlum. Málsgreinar eru markaðar og geymdar í gagnagrunni. Þegar frétt er útbúin eru *n* margar mörkunarbeinagrindur (einungis mörk, ekki orðmyndir) sóttar úr gagnagrunninum sem mynda svo fréttabeinagrindina. Allar orðmyndir sem finnast í gagnagrunninum eru því næst nýttar og valdar slembið til að fylla upp í beinagrindina fyrir hvert og eitt mark.

Tilgangurinn er vissulega einnig að hafa gaman, þar sem án undantekninga verða fréttirnar mjög svo súrar og samhengislausar.

Ég mæli sterklega með að skoða fréttasmiðinn í skýinu hér:

Einnig er hægt að setja hann upp *local* með því að fylgja eftirfarandi uppsetningu:

# Uppsetning

Þetta vefforrit er byggt með **Django**: https://www.djangoproject.com/

Mikilvægt er að fylgja öllum eftirfarandi skrefum gaumgæfilega (ath. allar skipanir miðast við rót verkefnisins):

1. Sækja verkefnið með **git pull https://github.com/nachos5/frettasmidur**
2. Búa til gagnagrunn með PostgreSQL, hér eru allar nauðsynlegar upplýsingar fyrir nýgræðinga: http://www.postgresqltutorial.com/
3. Búa til **.env** skrá í rót verkefnisins og stilla breytuna DATABASE_URL með gagnagrunninum sem þú bjóst til, sniðið er svona: DATABASE_URL=postgres://notandi:lykilorð@localhost:5432/heiti_gagnagrunnsins
4. Sækja python pakka með pip:
    1. Mæli sterklega með því að setja upp environment í rót verkefnisins, hér má lesa hvernig það er gert á þínu stýrikerfi: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
    2. Virkja environmentið (er einnig lýst á slóðinni hér fyrir ofan).
    3. Keyra skipunina **pip install -r ./requirements/local.txt**
5. Keyra skipunina **python manage.py migrate** til að búa til töflurnar í gagnagrunninum. [Hér](https://github.com/nachos5/frettasmidur/blob/master/frett_generator/frett/models.py) má skoða *Django-modelin*.
6. Keyra skipunina **python manage.py loaddata ./db.json** til að setja gögn í gagnagrunninn, gögnin innihalda um *2000* málsgreinar, skrapaðar frá MBL. Hér væri einnig hægt að skrapa sjálf/ur nýjar fréttir frá MBL, ef áhugi er fyrir hendi [smelltu hér](#skröpun) til fara í þann kafla.
7. Keyra skipunina **python manage.py collectstatic**.
8. Keyra skipunina **python manage.py runserver**
9. Fara á http://127.0.0.1:8000/!

# Skröpun
* Ef þú komst hingað frá skrefi *6.* í uppsetningunni þá er hægt að setja upp grunngögn í gagnagrunninn með því að skrapa nýjar fréttir frá mbl.is. Það er hægt að gera með því að fara í skelina: **python manage.py shell_plus** og keyra svo **db_initial_data()** úr skránni [**frett_generator.frett.utils.db.py**](https://github.com/nachos5/frettasmidur/blob/master/frett_generator/frett/utils/db.py), þetta mun taka nokkra klukkutíma með *default* stillingunum, hægt að er að minnka flækjustigið með því að stilla [markarann](#mörkun). Hins vegar gæti vel verið að kóðinn sé orðinn úreltur þegar þú ert að lesa þetta vegna breytinga á mbl.
* Hægt er að bæta við fréttum hvenær sem er í gagnagrunninn með því að skoða aðferðirnar í skránni [**frett_generator.frett.utils.scrape.py**](https://github.com/nachos5/frettasmidur/blob/master/frett_generator/frett/utils/scrape.py).

# Mörkun
* Markarann má finna í skránni [**frett_generator.frett.utils.__init__.py**](https://github.com/nachos5/frettasmidur/blob/master/frett_generator/frett/utils/__init__.py)
* Hann er *n-markari* sem merkið að hann heldur utan um samhengi *n* orða og markar eftir því. Því hærra *n* því mögulega meiri nákvæmni en aftur á móti hærra flækjustig.
* Stilla má *default*-gildið á *n* í [**config.settings.base.py**](https://github.com/nachos5/frettasmidur/blob/master/config/settings/base.py)

# Fréttasmíðar
* Fréttasmíðarnar sjálfar fara fram í formi í þessari skrá [**frett_generator.frett.forms.py**](https://github.com/nachos5/frettasmidur/blob/master/frett_generator/frett/forms.py) þar sem hvert skref er ítarlega kommentað.