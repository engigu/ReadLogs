$(document).ready(function () {
    var fp_path = "logs/celery.log";
    var namespace = "";
    // var socket = io.connect('http://' + document.domain + ':' + location.port + namespace, { "transports":['websocket'] });
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace,);

    $(".dropdown").on("change", function (e) {
        var filepath = $('.dropdown').val();
        fp_path = filepath;
        socket.emit('client', {'fp_path': filepath});
        $("#terminal").html(""); // 切换清空显示区域
    });


    // socket.emit('client', {'fp_path': fp_path});

    socket.on('response', function (res) {
        // console.log(res)
        if (res.path === fp_path) {
            var top_info = res.text;
            // console.log('++++',top_infos)

            // for (let i = 0; i < top_infos.length; i++) {

                // var top_info = top_infos[i];
                // console.log(top_info)

                var current_length = $('#terminal li').length;
                var limit_length = $('#terminal').attr("num");
                limit_length = Number(limit_length);
                // console.log(current_length, limit_length);
                if (current_length >= limit_length) {
                    $("#terminal li:first").remove();
                }

                $("#terminal").append("<li> None </pli>");
                var last_li = $("#terminal li:last");
                last_li.text(top_info);
                window.scrollTo(0, last_li.offset().top); // 页面滑动到这个位置

            }
        // }


    });

});