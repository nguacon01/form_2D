$(document).ready(function () {
    // create job buttons
    $(".create_job").each(function(){
        var $this = $(this);
        var job_name = $this.attr('job_name'),
            email = $this.attr('job_email'),
            directory = $this.attr('directory'),
            mscf_file = $this.attr('mscf_file'),
            username = $this.attr('job_username');
        var host = location.host.split(':')['0'];
        $this.click(function(){
            $.ajax({
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    "job_name":job_name,
                    "email":email,
                    "directory":directory,
                    "mscf_file":mscf_file,
                    "username":username
                }),
                url: 'http://'+host+':2361/api/v1.1/create_job/'
            })
            .always(function(res){
                if (res.code){
                    alert(res.msg);
                }else{
                    alert('Something went wrong. Contact your admin.');
                }
            });
        });
    });
});