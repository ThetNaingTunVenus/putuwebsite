console.log('message test');

$('#btnsave').click(function(){
    let msg = $('#msgid').val();
    // console.log(msg);
    mydata = {msg:msg};
    $.ajax({
        url: "{% url 'myapp:messageaddview' %}",
        method: "POST",
        data:mydata,
        success: function(data){
                    console.log(data)
        }
    })
})