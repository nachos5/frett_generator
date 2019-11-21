from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from .forms import FrettGeneratedForm, TitillForm
from .models import Frett


def heim(request):
    form = FrettGeneratedForm(request.POST or None)
    # ef postað var á þetta view og formið er í lagi vistum við í gagnagrunninum
    if form.is_valid():
        # formið skilar frétt, redirectum svo á url fréttarinnar
        frett_obj = form.save()
        return redirect(frett_obj.get_absolute_url())
    nyjast = Frett.objects.valid().order_by("-id")[:20]
    ctx = {"form": form, "nyjast": nyjast}
    return TemplateResponse(request, "pages/heim.html", ctx)


def frett(request, frett_id):
    frett_obj = get_object_or_404(Frett, id=frett_id)
    titill_form = None
    if not frett_obj.titill:
        titill_form = TitillForm(request.POST or None, instance=frett_obj)
        if titill_form.is_valid():
            frett_obj = titill_form.save()
            if frett_obj.titill:
                messages.success(request, "Takk fyrir að nota Fréttasmiðinn!")
                titill_form = None
        else:
            messages.info(
                request,
                "Fréttasmiðurinn biður um aðstoð þína við að búa titil fréttarinnar!",
            )
    ctx = {"frett": frett_obj, "titill_form": titill_form}
    return TemplateResponse(request, "pages/frett.html", ctx)
