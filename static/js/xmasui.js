COLORS = ["red", "green", "blue", "white", "magenta", "yellow", "cyan",  "black", "orange"];

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
         if (xmas.postUI) {
             xmas.sendProgram("custom");
         }
    }

    onFPSChange = function() {
        console.log("FPSChange");
        fps = $("#slider-fps").slider("value");
        $("#slider-fps-value").text(fps);
        if (xmas.postUI) {
            xmas.sendFPS(fps);
        }
    }

    onPowerOn = function() {
        var button_selector = "#power-on";
        var icon_selector = "#icon-power-on";
        console.log("PowerOn");
        $(".btn-power").removeClass("active");
        $(".icon-power").hide();
        $(button_selector).addClass("active");
        $(icon_selector).show();
        if (xmas.postUI) {
            xmas.setPower(true);
        }
    }

    onPowerOff = function() {
        var button_selector = "#power-off";
        var icon_selector = "#icon-power-off";
        console.log("PowerOff");
        $(".btn-power").removeClass("active");
        $(".icon-power").hide();
        $(button_selector).addClass("active");
        $(icon_selector).show();
        if (xmas.postUI) {
            xmas.setPower(false);
        }
    }

    onRandom = function() {
        if (xmas.postUI) {
            xmas.setPreprogrammed(-1);
        }
        setTimeout(xmas.requestSettings, 1000);
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

    setPower = function(value) {
        $.ajax({url: "/xmas/setPower?value=" + value});
    }

    setPreprogrammed = function(value) {
        $.ajax({url: "/xmas/setPreprogrammed?value=" + value});
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

        $("#power-on").click(function() { xmas.onPowerOn(); });
        $("#power-off").click(function() { xmas.onPowerOff(); });

        $("#random").click(function() { xmas.onRandom(); });

    }

    parseSettings = function(settings) {
        console.log(settings);
        this.postUI = false;
        try {
            $("#slider-fps").slider({value: settings["fps"]});
            if (settings["power"]) {
                $("#icon-power-on").click();
            } else {
                $("#icon-power-off").click();
            }

            $(".btn-single-color").removeClass("active");
            $(".custom-color-button").removeClass("active");
            $(".icon-custom-color").hide();

            for (index in settings["colors"]) {
                color = settings["colors"][index];
                if (settings["program"] == "single") {
                    onSingleColor(color);
                } else {
                    onCustomColor(color);
                }
            }

            if (settings["program"] != "single") {
                $("#custom-function").val(settings["program"]);
            }

            $("#custom-count").val(settings["numEach"]);
        }
        finally {
            this.postUI = true;
        }
    }

    requestSettings = function() {
        $.ajax({
            url: "/xmas/getSettings",
            dataType : 'json',
            type : 'GET',
            success: function(newData) {
                xmas.parseSettings(newData);
            },
            error: function() {
                console.log("error retrieving settings");
            }
        });
    }

    start = function() {
         this.postUI = true;
         this.initButtons();
         this.requestSettings();
    }

    return this;
}

$(document).ready(function(){
    xmas = xmas()
    xmas.start();
});

