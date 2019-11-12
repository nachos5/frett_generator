from .scrape import mbl_frettir
from ..models import Flokkur

# setjum gögn í gagnagrunninn
def db_initial_data():
    print("Gögn sett í gagnagrunninn...")
    Flokkur.objects.get_or_create(nafn="innlent")
    Flokkur.objects.get_or_create(nafn="erlent")
    mbl_frettir()
    print("Gögn komin í gagnagrunninn")
