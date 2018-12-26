function logIn(){
    console.log(document.getElementById('nomor_ktp').value)
    $.ajax({
        method: 'POST',
        url: 'http://localhost:7000/login',
        beforeSend: function(req) {
            req.setRequestHeader("Content-Type", "application/json");
        },
        data: JSON.stringify({
            "nomor_ktp": document.getElementById('nomor_ktp').value,
            "password":  document.getElementById('password').value
        }),
        success: function(res){
            window.location = "/main.html";
        },
        error: function(err){
            console.log(err)
        }
    })
}