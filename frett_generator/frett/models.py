from django.conf import settings
from django.db import models

from random import random


class Flokkur(models.Model):
    """Model definition for Flokkur."""

    nafn = models.CharField(max_length=50)

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
        # sækjum maxið
        count = Malsgrein.objects.all().count()
        random_ids = []
        # ef það eru færri en rand_count notum við allar sem fundust
        if rand_count > count:
            rand_count = count
        for i in range(rand_count):
            random_ids.append(int(random() * count))

        return self.filter(id__in=random_ids)


class Malsgrein(models.Model):
    """Model definition for Malgrein."""

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

