$(document).ready(function(){

    $("#peakpicking").on("change", function(){
        var $this = $(this)
        if($this.val() == "True"){
            $(".peakpicking_child").removeClass('hidden');
        }else{
            $(".peakpicking_child").addClass('hidden');
        }
    });

    if($("#do_sane").val() == "False"){
        $(".do_sane_child").addClass('hidden');
    }
    if($("#nus").val() == "False"){
        $(".nus_child").addClass('hidden');
    }
    if($("#compress_outfile").val() == "False"){
        $(".compress_outfile_child").addClass('hidden');
    }
    if($("#do_urqrd").val() == "False"){
        $(".do_urqrd_child").addClass('hidden');
    }

    $("#do_sane").on("change", function(){
        var $this = $(this)
        if($this.val() == "True"){
            $(".do_sane_child").removeClass('hidden');
        }else{
            $(".do_sane_child").addClass('hidden');
        }
    });

    $("#nus").on("change", function(){
        var $this = $(this)
        if($this.val() == "True"){
            $(".nus_child").removeClass('hidden');
            $("#do_pgsane").val('True')
        }else{
            $(".nus_child").addClass('hidden');
            $("#do_pgsane").val('False')
        }
    });

    $("#compress_outfile").on("change", function(){
        var $this = $(this)
        if($this.val() == "True"){
            $(".compress_outfile_child").removeClass('hidden');
        }else{
            $(".compress_outfile_child").addClass('hidden');
        }
    });

    $("#do_urqrd").on("change", function(){
        var $this = $(this)
        if($this.val() == "True"){
            $(".do_urqrd_child").removeClass('hidden');
        }else{
            $(".do_urqrd_child").addClass('hidden');
        }
    });

    $("#do_pgsane").on("change", function(){
        var $this = $(this)
        if($this.val() == "True"){
            $("#samplingfile").attr('required',true).attr("readonly", false);
        }else{
            $("#samplingfile").attr('required',false).attr("readonly", true);
        }
    });


    //sizemultipliers on change event
    get_values_sizemultipliers();
    $("#sizemultipliers").on('change', function(){
        get_values_sizemultipliers();
    });
});


//sizemultipliers function
function get_values_sizemultipliers(){
    var values = $("#sizemultipliers").val();
    if (values.match(/^([0-9]{0,1}.?[0-9]\s{1}[0-9]{0,1}.?[0-9])$/g)){
        var m1 = values.split(" ")[0];
        var m2 = values.split(" ")[1];
        var sizeF1 = $("#sizeF1").val();
        var sizeF2 = $("#sizeF2").val();
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                "m1":m1,
                "m2":m2,
                "sizeF1":sizeF1*1024,
                "sizeF2":sizeF2*1024
            }),
            url: '/metadata/comp_sizes'
        })
        .always(function(res){
            if (res.status == "success"){
                $("#spec_sizes").html("Spec size: " + res.spec_size.sizeF1/1024 + "k x " + res.spec_size.sizeF2/1024+ "k");
                $("#uncomp_sizes").html("Uncompressed sizes: " + res.uncompressed_size + "MB");
            }
        });
    }else{
        console.log("sizemultipliers is in wrong form");
    }
}