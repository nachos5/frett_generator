import itertools
import random

from django import forms
from django.conf import settings
from django.shortcuts import get_object_or_404

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Flokkur


class FrettGeneratedForm(forms.Form):
    """FrettGeneratedForm definition."""

    flokkur = forms.ModelChoiceField(queryset=Flokkur.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Vista", css_class="btn btn-primary"))

    def save(self, *args, **kwargs):
        data = self.data
        flokkur_id = data["flokkur"]
        flokkur = get_object_or_404(Flokkur, id=flokkur_id)

        #### sækjum málsgreinar úr flokknum

        flokkur_malsgreinar = flokkur.malsgreinar.all()
        # sækjum random málsgreinar úr flokknum (skoða random í models.py)
        malsgreinar = flokkur_malsgreinar.random()

        # notum þessar random malsgreinar til að mynda markabeinagrindina
        malsgreinar_mork = []
        for malsgrein in malsgreinar:
            # búum til lista af mörkum
            malsgreinar_mork.append(malsgrein.mork.split(settings.ADSKILNADARTAKN))

        ### næsta skref er að sækja orðmyndir fyrir mörkin

        # byrjum á að sækja "orðabanka" úr gagnagrunninum úr valda flokknum
        ordabanki_strengir = list(
            flokkur.malsgreinar.random(rand_count=100).only("tokens", "mork")
        )
        # búum til lista af tokens og mörkum
        ordabanki_tokens = list(
            itertools.chain(
                *[x.tokens.split(settings.ADSKILNADARTAKN) for x in ordabanki_strengir]
            )
        )
        ordabanki_mork = list(
            itertools.chain(
                *[x.mork.split(settings.ADSKILNADARTAKN) for x in ordabanki_strengir]
            )
        )
        # orðabankinn er listi af tvenndum á forminu (token, mark)
        ordabanki = list(zip(ordabanki_tokens, ordabanki_mork))
        # print(ordabanki)

        test = []

        for x in malsgreinar_mork[0]:
            y = [z for z in ordabanki if z[1] == x]
            # velja eitt random
            r = random.choice(y)
            print(r)

