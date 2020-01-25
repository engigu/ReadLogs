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
        // console.log(res)
        if (res.path === fp_path) {
            var top_info = res.text;
            var current_length = $('#terminal li').length;
            var limit_length = $('#terminal').attr("num"); 
            limit_length = Number(limit_length);
            // console.log(current_length, limit_length);
            if (current_length >= limit_length){
			    $("#terminal li:first").remove();
            }
            $("#terminal").append("<li> None </pli>");
            $("#terminal li:last").text(top_info);
            
            window.scrollTo(0, document.documentElement.clientHeight);

        }

    });

    $(window).bind('onbeforeunload', function () {    // 离开页面前关闭tail
            socket.emit('leavepage', {'_type': _type});

        }
    );
});