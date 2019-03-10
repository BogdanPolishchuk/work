
$("#check_ip").click(function () {
    // send inputted IP addresses by ajax request to server
    $("#loadImg_2").show();
    $.ajax({
        type: "GET",

        url: "check_ip_adr/",

        data: {
            'ip_range': $("#input_ip_adr").val(),
        },

        dataType: "text",

        cache: false,

        success: function (data) {
            $("#loadImg_2").hide();
            if (data == 'ok') {
                console.log("welcome");
                document.getElementById("mess").innerHTML = "Incorrect IP is exist!";
                if (document.getElementById("mess").innerHTML == "Incorrect IP is exist!") {
                    $.get( "rez/", function( data ) {
                        var jData = JSON.stringify(data);
                        console.log(jData);
                        var arr_err = JSON.parse(jData);
                        for (var e in arr_err) {
                            if (e) {
                                document.getElementById('error_ip').value += e + " - " + arr_err[e] + "\n";
                            }
                        }
                    });
                    $.get( "ok_daata/", function( data_ok ) {
                        var ok_Data = JSON.stringify(data_ok);
                        console.log(ok_Data);
                        var arr_ret = JSON.parse(ok_Data);
                        for (var i in arr_ret) {
                            document.getElementById('ok_ip').value += i + ":\n";
                            if (!arr_ret[i].length) {
                                document.getElementById('ok_ip').value += "\t" + "No services" + "\n";
                            }
                            else {
                                for (var j in arr_ret[i]) {
                                    document.getElementById('ok_ip').value += "\t" + arr_ret[i][j] + "\n";
                                }
                            }
                        }
                    });
                }
            } // --- if (data == 'ok')
            else if (data == 'empty'){
                console.log("empty");
                document.getElementById("mess").innerHTML = "Не введён ни один IP адресс";
                $("#mess").css("background-color", "lightblue")
            }
            else if (data == 'ip'){
                console.log("ip");
                document.getElementById("mess").innerHTML = "Data has got";
                if (document.getElementById("mess").innerHTML == "Data has got") {
                    $.get( "ok_daata/", function( data_ok ) {
                        var ok_Data = JSON.stringify(data_ok);
                        console.log(ok_Data);
                        var arr_ret = JSON.parse(ok_Data);
                        for (var i in arr_ret) {
                            document.getElementById('ok_ip').value += i + ":\n";
                            if (!arr_ret[i].length) {
                                document.getElementById('ok_ip').value += "\t" + "No services" + "\n";
                            }
                            else {
                                for (var j in arr_ret[i]) {
                                    document.getElementById('ok_ip').value += "\t" + arr_ret[i][j] + "\n";
                                }
                            }
                        }
                    });
                }
                $("#mess").css("background-color", "lawngreen")
            }

            else if (data == 'no'){
                console.log("no");
                document.getElementById("mess").value = "SHIT!!!!";
            }
        }
    });
});

$("#clear").click(function () {
    // send ajax request to clear all data
    $.ajax({
        type: "GET",

        url: "clear_data/",

        data: {
            'push': 'clear'
        },

        dataType: "text",

        cache: false,

        success: function (data) {
            if (data == 'clear') {
                console.log("clear_data");
                document.getElementById("mess").innerHTML = "";
                $("#mess").css("background-color", "lightgray");
                document.getElementById("error_ip").value = "";
                document.getElementById("input_ip_adr").value = "";
                document.getElementById("ok_ip").value = "";

            }
            else if (data == 'no'){
                console.log("no");
                document.getElementById("mess").value = "SHIT!!!!";
            }
        }
    });
});


