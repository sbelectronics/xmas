function xmas() {
    onSingleColor = function(color) {
         console.log("singlecolor " + color);
         var button_selector = "#single-" + color;
         $(".btn-single-color").removeClass("active")
         $(button_selector).addClass("active")
         xmas.sendProgram("single")
    }

    onCustomColor = function(color) {
         console.log("customcolor " + color)
         var button_selector = "#custom-" + color;
         if ($(button_selector).hasClass("active")) {
             $(button_selector).removeClass("active")
         } else {
             $(button_selector).addClass("active")
         }
         xmas.sendProgram("custom");
    }

    sendProgram = function(which) {
        console.log("sendProgram " + which);
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

        single_colors = ["red", "green", "blue", "white"]
        for (index in single_colors) {
            initSingleColorButton(single_colors[index]);
            initCustomColorButton(single_colors[index]);
        }

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

