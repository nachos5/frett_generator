import random

from django.conf import settings
from django.db import models
from django.db.models import F, Func, Value, Q
from django.db.models.functions import Length, Replace
from django.urls import reverse


class Flokkur(models.Model):
    """Model definition for Flokkur."""

    nafn = models.CharField(max_length=50)
    slug = models.SlugField()

    class Meta:
        """Meta definition for Flokkur."""

        verbose_name = "Flokkur"
        verbose_name_plural = "Flokkar"

    def __str__(self):
        """Unicode representation of Flokkur."""
        return self.nafn


class MalsgreinQuerySet(models.QuerySet):
    def random(self, rand_count=settings.FJOLDI_MALSGREINA):
        """ 
        Sækir FJOLDI_MALSGREINA (heiltölubreyta í settings) málsgreina af handahófi.
        Einnig hægt að senda inn count inntak til að velja fjölda sem á að skila.
        """
        # sækjum id's
        ids = list(self.values_list("pk", flat=True))
        count = len(ids)
        # ef það eru færri en rand_count notum við allar sem fundust
        if rand_count > count:
            rand_count = count
        random_ids = random.sample(ids, rand_count)

        return self.filter(id__in=random_ids)

    def filter_out_unk(self):
        """ 
        síar út málsgreinar sem innihalda færri mörkunarvillur
        en breytan VILLU_THRESHOLD í settings.
        Málsgreinin þarf einnig að innihalda að minnsta kosti MIN_STAFIR_TOKENS stafi (með aðskilnaðartákninu).
        """
        return (
            self.annotate(tokens_len=Length("tokens"))
            .filter(tokens_len__gt=settings.MIN_STAFIR_TOKENS)
            .annotate(
                no_unk=Func(
                    F("mork"), Value(settings.VILLUMARK), Value(""), function="replace"
                ),
                # finnum lengdarmismuninn á strengnum með og án villnumarka
                unk_count=(Length("mork") - Length("no_unk")) / len(settings.VILLUMARK),
            )
            .filter(unk_count__lt=settings.VILLU_THRESHOLD)
        )


class Malsgrein(models.Model):
    """Model definition for Malgrein."""

    MBL = "MBL"
    SIDA_CHOICES = [
        (MBL, "mbl"),
    ]
    sida = models.CharField(max_length=50, choices=SIDA_CHOICES, default=MBL)

    flokkur = models.ForeignKey(
        Flokkur, on_delete=models.CASCADE, related_name="malsgreinar"
    )

    # aðskilnaðartákn fyrir tokenin og mörkin skilgreint í settings
    tokens = models.TextField(unique=True)
    mork = models.TextField()

    objects = MalsgreinQuerySet.as_manager()

    class Meta:
        """Meta definition for Malsgrein."""

        verbose_name = "Málsgrein"
        verbose_name_plural = "Málsgreinar"

    def __str__(self):
        """Unicode representation of Malsgrein."""
        return self.tokens


class FrettQuerySet(models.QuerySet):
    def valid(self):
        """ Fullkláraðar fréttir með titli """
        return self.filter(Q(titill__isnull=False) & Q(html__isnull=False))


class Frett(models.Model):
    """Model definition for Frett."""

    titill = models.CharField(max_length=100, blank=True, null=True)
    html = models.TextField()
    einstok_ord = models.TextField()

    objects = FrettQuerySet.as_manager()

    class Meta:
        """Meta definition for Frett."""

        verbose_name = "Frétt"
        verbose_name_plural = "Fréttir"

    def __str__(self):
        """Unicode representation of Frett."""
        return self.titill if self.titill else str(self.pk)

    def get_absolute_url(self):
        """Return absolute url for Frett."""
        return reverse("frett", kwargs={"frett_id": self.id})
