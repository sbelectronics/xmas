COLORS = ["red", "green", "blue", "white", "magenta", "yellow", "cyan"];

function xmas() {
    onSingleColor = function(color) {
         console.log("singlecolor " + color);
         var button_selector = "#single-" + color;
         var icon_selector = "#icon-single-" + color;
         $(".btn-single-color").removeClass("active");
         $(".icon-single-color").hide();
         $(button_selector).addClass("active")
         $(icon_selector).show();
         xmas.sendProgram("single")
    }

    onCustomColor = function(color) {
         console.log("customcolor " + color);
         var button_selector = "#custom-" + color;
         var icon_selector = "#icon-custom-" + color;
         if ($(button_selector).hasClass("active")) {
             $(button_selector).removeClass("active");
             $(icon_selector).hide();
         } else {
             $(button_selector).addClass("active");
             $(icon_selector).show();
         }
         xmas.sendProgram("custom");
    }

    onFPSChange = function() {
        console.log("FPSChange");
        fps = $("#slider-fps").slider("value");
        $("#slider-fps-value").text(fps);
        xmas.sendFPS(fps);
    }

    getSelectedColors = function(which) {
        colors = [];
        for (index in COLORS) {
            color = COLORS[index];
            if (which == "custom") {
                button_selector = "#custom-" + color;
            } else {
                button_selector = "#single-" + color;
            }
            if ($(button_selector).hasClass("active")) {
                colors.push(color);
            }
        }
        return colors;
    }

    sendProgram = function(which) {
        colors = xmas.getSelectedColors(which);
        if (which=="single") {
            program="single";
            url="/xmas/setProgram?program=single&color=" + colors.join();
        } else {
            program=$("#custom-function").val();
            count=$("#custom-count").val();
            url="/xmas/setProgram?program=" + program + "&color=" + colors.join("&color=") + "&count=" + count;
        }
        console.log("sendprogram " + url);
        $.ajax({url: url,
               });
    }

    sendFPS = function(fps) {
        $.ajax({url: "/xmas/setFPS?fps=" + fps});
    }

    initButtons = function() {
        initSingleColorButton = function(color) {
            var button_id = "#single-" + color;
            $(button_id).click(function() { xmas.onSingleColor(color); });
        }

        initCustomColorButton = function(color) {
            var button_id = "#custom-" + color;
            $(button_id).click(function() { xmas.onCustomColor(color); });
        }

        for (index in COLORS) {
            initSingleColorButton(COLORS[index]);
            initCustomColorButton(COLORS[index]);
        }

        $("#slider-fps").slider({min: 1, max:20, change: this.onFPSChange});

        $("#custom-count").change(function() { xmas.sendProgram("custom"); });
        $("#custom-function").change(function() { xmas.sendProgram("custom"); });

    }

    start = function() {
         this.initButtons();
    }

    return this;
}

$(document).ready(function(){
    xmas = xmas()
    xmas.start();
});

