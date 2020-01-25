var fp_path = '';

var namespace = "";
var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);



// var getData = function (filepath, isNewFile) {
// 	// $(".renderBlock").html("<p>Loading.....</p>");
// 	$.ajax({
// 		url: "/api/getcontent",
// 		type: "POST",
// 		data: JSON.stringify({ path: filepath, isNewFile: isNewFile }),
// 		dataType: "json",
// 		contentType: "application/json; charset=utf-8",
// 		success: function (data) {
// 			renderData(data);
// 		},

// 	});
// };




var renderData = function (data) {
	console.log(data['modified'])
	if (data['modified'] == true) {
		$(".renderBlock").html("");
		for (var i in data['lines']) {
			$(".renderBlock").append("<p> None </p>");
			$(".renderBlock p:nth-last-of-type(1)").text(data['lines'][i]);
		}
		if (data.length == 0) {
			$(".renderBlock").html("<p>No Data Available</p>");
		}
	}
};


// setInterval(function () {
// 	var filepath = $('.dropdown').val();
// 	getData(filepath, false);
// }, 3000);



socket.on('response', function (res) {
	console.log(res);
	if (res.path === fp_path) {
		var top_info = res.text;
		// var old = document.getElementById("terminal").innerHTML;
		// document.getElementById("terminal").innerHTML = old + '</br>' + top_info;

		$(".renderBlock").append("<p> None </p>");
		$(".renderBlock p:nth-last-of-type(1)").text(top_info);

		// $(".renderBlock").html("");

		// for (var i in data['lines']) {
		// 	$(".renderBlock").append("<p> None </p>");
		// 	$(".renderBlock p:nth-last-of-type(1)").text(data['lines'][i]);
		// }
		// if (data.length == 0) {
		// 	$(".renderBlock").html("<p>No Data Available</p>");
		// }

	}

});



$(".dropdown").on("change", function (e) {
	var filepath = $('.dropdown').val();
	// getData(filepath, true);
	fp_path = filepath;
	socket.emit('client', { 'fp_path': filepath });
	$(".renderBlock").html(""); // 切换清空显示区域


});

// $(document).ready(function () {
// 	var filepath = $('.dropdown').val();
// 	getData(filepath, true);
// });


