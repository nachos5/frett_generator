from .scrape import mbl_frettir
from ..models import Flokkur

# setjum gögn í gagnagrunninn
def db_initial_data():
    print("Gögn sett í gagnagrunninn...")
    Flokkur.objects.get_or_create(nafn="Innlent", slug="innlent")
    Flokkur.objects.get_or_create(nafn="Erlent", slug="erlent")
    Flokkur.objects.get_or_create(nafn="Tækni", slug="togt")
    mbl_frettir()
    print("Gögn komin í gagnagrunninn")
