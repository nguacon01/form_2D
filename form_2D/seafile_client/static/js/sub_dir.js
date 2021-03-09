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

    $(".handle_button").each(function(){
        var $this = $(this);
        var repo_id = $this.attr('repo_id'),
            full_path = $this.attr('full_path'),
            method = $this.attr('method');
        var url = 'http://'+location.host+'/seafile_client/handle_button?repo_id='+repo_id+'&full_path='+full_path;
        $this.click(function(){
            var txt = '';
            if(method === "GET"){
                txt = "Are you sure to download this file ?";
            }else{
                txt = "Are you sure to remove this file?"
            }
            var confirm = window.confirm(txt);
            if (confirm){
                fetch(url, {
                    method:method,
                })
                .then(response => {
                    return response.json();
                })
                .then(json => {
                    if (method==='DELETE'){
                        location.reload();
                    }else{
                        window.location = json.download_link;
                    }
                })
                .catch(err => {
                    console.log(err);
                    alert("ERROR! There are some problems with your action. Contact your admin.");
                })
            }
        });
    });
});