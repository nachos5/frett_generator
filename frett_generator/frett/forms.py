import itertools
import random

from django import forms
from django.conf import settings
from django.shortcuts import get_object_or_404
from django_select2.forms import Select2Widget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout, Submit

from .models import Flokkur, Frett
from .utils import takn
from .utils.html import frett_html


class FrettGeneratedForm(forms.Form):
    """FrettGeneratedForm definition."""

    flokkur = forms.ModelChoiceField(
        queryset=Flokkur.objects.filter(malsgreinar__isnull=False).distinct()
    )

    fjoldi_malsgreina_choices = []
    for i in range(5, 16):
        fjoldi_malsgreina_choices.append((str(i), str(i)))
    fjoldi_malsgreina = forms.ChoiceField(
        label="Fjöldi málsgreina", choices=fjoldi_malsgreina_choices
    )

    endurtaka_nafnord_hjalpartexti = """
        Hakaðu við þennan reit ef þú vilt að smiðurinn reyni að endurtaka nafnorð sem hafa komið áður fram.
        Annars eru orðin valin af handahófi úr öllu orðasafninu í hvert skipti. """
    endurtaka_nafnord = forms.BooleanField(
        required=False,
        label="Endurtaka nafnorð",
        help_text=endurtaka_nafnord_hjalpartexti,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit("submit", "Smíða frétt", css_class="btn btn-primary")
        )

    def save(self, *args, **kwargs):
        data = self.data
        flokkur_id = data["flokkur"]
        fjoldi_malsgreina = int(data["fjoldi_malsgreina"])
        if "endurtaka_nafnord" in data:
            endurtaka_nafnord = data["endurtaka_nafnord"]
        else:
            endurtaka_nafnord = False

        flokkur = get_object_or_404(Flokkur, id=flokkur_id)

        #### sækjum málsgreinar úr flokknum

        # sækjum málsgreinar sem innihalda færri ómörkuð mörk en eitthvað ákveðið threshold
        flokkur_malsgreinar = flokkur.malsgreinar.filter_out_unk()
        # sækjum random málsgreinar úr flokknum (skoða random í models.py)
        malsgreinar = flokkur_malsgreinar.random(rand_count=fjoldi_malsgreina)
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

        frett_malsgreinar = []

        # geymum lista með nafnorðum sem eru komin í fréttina
        prev_nafnord = []
        prev_mark_match = []
        # ítrum í gegnum allar málsgreinarnar
        for malsgrein in malsgreinar_mork:
            frett_malsgrein = []
            # ítrum í gegnum mörk málsgreinarinnar
            for mark in malsgrein:
                # sækjum orð úr orðabankanum með þessu marki
                x = [y for y in ordabanki if y[1] == mark]
                # ef endurtaka nafnorð þá tékkum við líka á þeim orðum sem komin eru
                if endurtaka_nafnord:
                    prev_mark_match = [n for n in prev_nafnord if n[1] == mark]
                # fannst ekkert
                if not x:
                    continue
                # velja eitt random
                if not prev_mark_match:
                    rand_ord = random.choice(x)
                # 75/25 hvort við veljum prev orð eða nýtt
                else:
                    if random.random() < 0.9:
                        rand_ord = random.choice(prev_mark_match)
                    else:
                        rand_ord = random.choice(x)
                # ef nafnorð bætum við í prev_nafnord
                if rand_ord[1][0] == "n":
                    prev_nafnord.append(rand_ord)
                # bætum við í málsgreinina
                frett_malsgrein.append(rand_ord)

            frett_malsgreinar.append(frett_malsgrein)
        # núna þurfum við að útbúa html kóða fyrir fréttina og skila
        html = frett_html(frett_malsgreinar)

        # setjum í db!
        einstok_ord = [x[0] for x in itertools.chain(*frett_malsgreinar)]
        frett_obj = Frett.objects.create(
            html=html, einstok_ord=settings.ADSKILNADARTAKN.join(einstok_ord)
        )
        return frett_obj


class TitillForm(forms.ModelForm):
    class Meta:
        """Meta definition for Titillform."""

        model = Frett
        fields = ("titill",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.titill:
            einstok_ord = self.instance.einstok_ord.split(settings.ADSKILNADARTAKN)
            einstok_ord = [("", "---------")] + list(set(zip(einstok_ord, einstok_ord)))
            self.max_ord = 10
            for i in range(self.max_ord):
                if i == 0:
                    required = True
                else:
                    required = False
                self.fields["titill-{i}".format(i=i)] = forms.ChoiceField(
                    label="Orð {i}".format(i=i + 1),
                    choices=einstok_ord,
                    widget=Select2Widget,
                    required=required,
                )

            self.helper = FormHelper()
            self.helper.form_method = "post"
            self.helper.layout = Layout(
                Div(
                    "titill-0",
                    "titill-1",
                    "titill-2",
                    "titill-3",
                    "titill-4",
                    "titill-5",
                    "titill-6",
                    "titill-7",
                    "titill-8",
                    "titill-9",
                    css_id="form-titill-container",
                )
            )
            self.helper.add_input(
                Submit("submit", "Staðfesta titil", css_class="btn btn-primary")
            )

    def clean(self, *args, **kwargs):
        data = self.cleaned_data
        values = list(data.values())[1:]
        titill_strengur = takn(" ".join(values))
        data["titill"] = titill_strengur

        return data
