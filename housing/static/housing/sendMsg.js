"use strict"

function getMsg() {
    $.ajax({
        url: "/housing/get-msg",
        dataType : "json",
        success: updateMsgBox,
        error: updateError
    });
}

function updateError(xhr) {
    if (xhr.status == 0) {
        displayError("Cannot connect to server")
        return
    }

    if (!xhr.getResponseHeader('content-type') == 'application/json') {
        displayError("Received status=" + xhr.status)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }

    displayError(response)
}

function displayError(message) {
    $("#error").html(message);
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}

function getMsgFromBox(msg_box_id) {
    console.log("-----")
    displayError('')
    $.ajax({
        url: "/housing/get-msg-from-box/" + msg_box_id,
        type: "POST",
        data: "csrfmiddlewaretoken="+getCSRFToken()+"&msg_box_id="+msg_box_id,
        dataType : "json",
        success: updateMsgText4Box,
        error: updateError
    });
}

function sendMsg(msg_box_id) {
    let commentid = "#id_comment_input_text_" + msg_box_id
    let itemTextElement = $(commentid)
    let itemTextValue   = itemTextElement.val()

    // Clear input box and old error message (if any)
    itemTextElement.value = ''
    displayError('')
    $.ajax({
        url: "/housing/send-msg/"+msg_box_id, 
        type: "POST",
        data: "comment_text="+itemTextValue+"&csrfmiddlewaretoken="+getCSRFToken()+"&msg_box_id="+msg_box_id,
        dataType : "json",
        success: updateMsgBox,
        error: updateError
    });
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown";
}



function updateMsgBox(response) {
    console.log("updatebox")
    updateList4Box(response.response_boxes)
    // No msg box is chosen now
    // show empty msg text
    updateList4Text(response.response_texts)
    
}

function updateMsgText4Box(response) {

    updateList4Box(response.response_boxes)
    // show chosen text of box
    updateList4Text(response.response_texts)
}

function updateList4Box(items) {  
    console.log("12345")
    $(items).each(function() {
        // only display the msg boxes belongs to the current user
        if ((this.user2_name == myUserName || this.user1_name == myUserName) ){
            
        let post_item_id = "id_post_div_" + this.id
        if (document.getElementById(post_item_id) == null) {
            console.log("00")
            $("#msg_box").prepend(
                '<div id="id_post_div_'+this.id+'" style="margin-top:8vw" class="row justify-content-center">' +
                '<ul id = "boxes" class="col-2 d-none d-md-block list-group ">'+'</ul>'+
                '<div id = "box_text_'+this.id+'" class="col-8 border">'+
                '<form><textarea id="id_comment_input_text_'+this.id+'" class="form-control" id="query" style="height: 140px" placeholder="type"></textarea>'+
                '<button style = "margin-left: 80%;" class="btn btn-primary my-4" type="submit" value="Submit" onclick="sendMsg('+this.id+')">submit</button>'+
                '</form></div></div>'
            )
            if (this.user1_name ==  myUserName|| this.user2_name == myUserName) {
                console.log("22")
                if (this.user1_name == myUserName) {
                    $("#boxes").append(
                        '<li class="list-group-item d-flex justify-content-between align-items-center">'+
                        this.user2_name +
                        '<button class="badge bg-primary rounded-pill" onclick="getMsgFromBox('+ this.id +')">Read</button></li>'
                    )
                } else {
                    $("#boxes").append(
                        '<li class="list-group-item d-flex justify-content-between align-items-center">'+
                        this.user1_name +
                        '<button class="badge bg-primary rounded-pill" onclick="getMsgFromBox('+ this.id +')">Read</button></li>'
                    )
                }
            }                 
        } 
    }  
    })
}

function parse_datetime(datetime) {
    let date = new Date(datetime.toString())
    var s = date.toLocaleString('en-us', { timeZone: 'US/Eastern' })
    var a = s.split(/\D/);
    var amPm = (date.getHours() < 12) ? "AM" : "PM"
    var hour = (date.getHours() <= 12) ? date.getHours() : date.getHours() - 12
    a[4] = (date.getHours() <= 12) ? date.getHours() : date.getHours() - 12
    //return a[0] + '/' + a[1] + '/' + a[2] + ' ' + a[4] + ':' + a[5] + ' ' + amPm;
    return date.getMonth()+1 + '/' + date.getDate() + '/' + date.getFullYear() + ' ' + hour + ':' + date.getMinutes() + ' ' + amPm;
}

function updateList4Text(items) {
    $(items).each(function() {
        let comment_id = "id_comment_div_" + this.id
        if (document.getElementById(comment_id) == null) {
            if (this.texted_by_id == myUserId) {   
                $("#box_text_"+this.self_box_id).prepend(
                    '<div id="id_comment_div_'+this.id+'"  style = "text-align: end;">' +
                    '<i class="bi bi-chat-right-dots-fill">' + 
                    '<i class="bi bi-person ms-100">' +
                    '<span class = "">'+this.text+'</span></i></i>'
                    + 
                ' </div>'
                    )
            } else {
                console.log("44")
                $("#box_text_"+this.self_box_id).prepend(
                    '<div id="id_comment_div_'+this.id+'"  class="bi bi-person">' +
                    '<i class="bi bi-chat-left-dots-fill">' + 
                    '<span class = "">'+this.text+'</span></i>'
                    +' </div>'
                )
            }
        }     
    })
}
