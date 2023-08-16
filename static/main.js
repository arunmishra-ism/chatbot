$(document).ready(function() {
    $("#messageArea").on("submit", function(event) {
        event.preventDefault();

        const date = new Date();
        const hour = date.getHours();
        const minute = date.getMinutes();
        const str_time = hour + ":" + minute;
        var rawText = $("#text").val();

        var userHtml =
            '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' +
            rawText +
            '<span class="msg_time_send">' +
            str_time +
            "</span></div><div class='img_cont_msg'><img src='https://i.ibb.co/d5b84Xw/Untitled-design.png' class='rounded-circle user_img_msg'></div></div>";

        $("#text").val("");
        $("#messageFormeight").append(userHtml);

        $.ajax({
            data: JSON.stringify({
                message: rawText, // key name (message)
            }),
            contentType: "application/json",
            type: "POST",
            url: "/chat", // URL for Flask route
        }).done(function(data) {
            var botHtml =
                '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="https://i.ibb.co/fSNP7Rz/icons8-chatgpt-512.png" class="rounded-circle user_img_msg"></div><div class="msg_cotainer">' +
                data.response +
                '<span class="msg_time">' +
                str_time +
                "</span></div></div>";
            $("#messageFormeight").append($.parseHTML(botHtml));

            // Scroll to the bottom to show the latest response
            var chatBody = document.getElementById("messageFormeight");
            chatBody.scrollTop = chatBody.scrollHeight;
        });
    });
});
