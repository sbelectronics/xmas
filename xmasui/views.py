from django.shortcuts import render
from django.template import RequestContext, loader
from xmascontroller import Christmas, COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_WHITE, COLOR_YELLOW, COLOR_MAGENTA, COLOR_ORANGE, COLOR_BLACK, COLOR_CYAN, \
                           SolidColorAnimation, RainbowSequenceAnimation, FadeColorAnimation, AllColorCycleAnimation, ColorMorphAnimation, RandomFillAnimation
import xmascontroller
import json

# Create your views here.

from django.http import HttpResponse


def index(request):
    template = loader.get_template('xmasui/index.html')
    context = RequestContext(request, {});
    return HttpResponse(template.render(context))

def setFPS(request):
    Christmas.setFPS(int(request.GET.get("fps","0")))

    return HttpResponse("okey dokey")

def setPower(request):
    Christmas.setPower(request.GET.get("value","true")=="true")

    return HttpResponse("okey dokey")

def setPreprogrammed(request):
    value = request.GET.get("value",0)
    try:
        value = int(value)
    except:
        value = -1
    Christmas.setPreprogrammed(value)

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
        elif (color=="cyan"):
            colors.append(COLOR_CYAN)
        elif (color=="orange"):
            colors.append(COLOR_ORANGE)
        elif (color=="black"):
            colors.append(COLOR_BLACK)
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
    elif (program == "morph"):
        Christmas.setAnimation(ColorMorphAnimation(Christmas, colors))
    elif (program == "randomfill"):
        Christmas.setAnimation(RandomFillAnimation(Christmas, colors))

    return HttpResponse("okey dokey")

def getSettings(request):
    result = {}
    animation = Christmas.animation
    if (animation):
        result["program"] = animation.program_name
        result["colors"] = animation.getColorNames()
        result["numEach"] = animation.numEach
    result["fps"] = Christmas.FPS
    result["power"] = Christmas.power

    return HttpResponse(json.dumps(result), content_type='application/javascript')


