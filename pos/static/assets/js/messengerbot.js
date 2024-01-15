console.log('message test');

$('#btnsave').click(function(){
    let msg = $('#msgid').val();
    console.log(msg);
    mydata = {msg:msg};
    $.ajax({
        url: "/save_data/",
        method: "POST",
        data:mydata,
        success: function(data){
                    console.log(data.status)
                    console.log(data.msgdata)
                    window.location = "/"
        }
    })
})