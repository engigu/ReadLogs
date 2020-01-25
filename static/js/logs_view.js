$(document).ready(function () {
    var fp_path = "logs/celery.log";
    var namespace = "";
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    $(".dropdown").on("change", function (e) {
        var filepath = $('.dropdown').val();
        // getData(filepath, true);
        // console.log(filepath)
        fp_path = filepath;
        socket.emit('client', {'fp_path': filepath});
        $("#terminal").html(""); // 切换清空显示区域
    });


    // socket.emit('client', {'fp_path': fp_path});

    socket.on('response', function (res) {
        console.log(res)
        if (res.path === fp_path) {
            var top_info = res.text;
            // var old = document.getElementById("terminal").innerHTML;
            $("#terminal").append('<li>' + top_info + '</li>');
        }

    });

    $(window).bind('onbeforeunload', function () {    // 离开页面前关闭tail
            socket.emit('leavepage', {'_type': _type});

        }
    );
});