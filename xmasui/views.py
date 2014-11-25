from django.shortcuts import render
from django.template import RequestContext, loader
from xmascontroller import Christmas, COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_WHITE, COLOR_YELLOW, COLOR_MAGENTA, \
                           SolidColorAnimation, RainbowSequenceAnimation, FadeColorAnimation, AllColorCycleAnimation
import xmascontroller

# Create your views here.

from django.http import HttpResponse


def index(request):
    template = loader.get_template('xmasui/index.html')
    context = RequestContext(request, {});
    return HttpResponse(template.render(context))

def setFPS(request):
    Christmas.setFPS(int(request.GET.get("fps","0")))

    return HttpResponse("okey dokey")

def setProgram(request):
    colors=[]
    for color in request.GET.getlist("color",[]):
        if (color=="red"):
            colors.append(COLOR_RED)
        elif (color=="green"):
            colors.append(COLOR_GREEN)
        elif (color=="blue"):
            colors.append(COLOR_BLUE)
        elif (color=="white"):
            colors.append(COLOR_WHITE)
        elif (color=="magenta"):
            colors.append(COLOR_MAGENTA)
        elif (color=="yellow"):
            colors.append(COLOR_YELLOW)
        else:
            print "XXX unknown color", color

    if (colors==[]):
        colors = [COLOR_BLUE]

    count = int(request.GET.get("count","0"))

    program = request.GET.get("program", "single")
    if (program == "single"):
        Christmas.setAnimation(SolidColorAnimation(Christmas, colors))
    elif (program == "sequence"):
        Christmas.setAnimation(RainbowSequenceAnimation(Christmas, colors, numEach=count))
    elif (program == "fade"):
        Christmas.setAnimation(FadeColorAnimation(Christmas, colors, numEach=count))
    elif (program == "cycle"):
        Christmas.setAnimation(AllColorCycleAnimation(Christmas, colors))

    return HttpResponse("okey dokey")

