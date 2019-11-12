from django.template.response import TemplateResponse

from .forms import FrettGeneratedForm


def heim(request):
    form = FrettGeneratedForm(request.POST or None)
    # ef postað var á þetta view og formið er í lagi vistum við í gagnagrunninum
    if form.is_valid():
        form.save()
    ctx = {"form": form}
    return TemplateResponse(request, "pages/heim.html", ctx)

