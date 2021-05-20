$(document).ready(function(){
    $("#peakpicking").on("change", function(){
        var $this = $(this)
        if($this.val() == "True"){
            $(".peakpicking_child").removeClass('hidden');
        }else{
            $(".peakpicking_child").addClass('hidden');
        }
    });
    if($("#peakpicking").val() == "False"){
        $(".peakpicking_child").addClass('hidden');
    }

    if($("#do_sane").val() == "False"){
        $(".do_sane_child").addClass('hidden');
    }
    if($("#nus").val() == "False"){
        $(".nus_child").addClass('hidden');
        $("#samplingfile").html('None');
    }
    if($("#compress_outfile").val() == "False"){
        $(".compress_outfile_child").addClass('hidden');
    }
    if($("#do_urqrd").val() == "False"){
        $(".do_urqrd_child").addClass('hidden');
    }

    $("#do_sane").on("change", function(){
        handleSaneSelection();
    });

    $("#nus").on("change", function(){
        handleNusSelection();
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
        handlePgSaneSelection();
    });


    //sizemultipliers on change event
    get_values_sizemultipliers();
    $("#sizemultipliers").on('change', function(){
        get_values_sizemultipliers();
        predict_time_calculation();
    });

    $('#sane_rank').on('change', function(){
        predict_time_calculation();
    });
    $('#sane_iterations').on('change', function(){
        predict_time_calculation();
    });
    $('#pgsane_rank').on('change', function(){
        predict_time_calculation();
    });
    $('#pgsane_iterations').on('change', function(){
        predict_time_calculation();
    });

    // predict time of calculation
    predict_time_calculation();
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
            type: "GET",
            contentType: "application/json",
            data: {
                "m1":m1,
                "m2":m2,
                "sizeF1":sizeF1*1024,
                "sizeF2":sizeF2*1024
            },
            url: '/seafile_client/comp_sizes'
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

async function predict_time_calculation(){
    let values = $("#sizemultipliers").val();
    let m1 = 1;
    let m2 = 1;
    let sizeF1 = 2;
    let sizeF2 = 3;
    let spg = 0;
    let rank = 0;
    let iters = 0;
    let didimp = 1;
    let nproc = 7;

    if ($('#do_sane').val() == 'True'){
        spg = 1;
        rank = $('#sane_rank').val();
        iters = $('#sane_iterations').val();
        nproc = 4;
    }
    if ($('#do_pgsane').val() == 'True'){
        spg = 2;
        rank = $('#pgsane_rank').val();
        iters = $('#pgsane_iterations').val();
        nproc = 7
    }
    if (values.match(/^([0-9]{0,1}.?[0-9]\s{1}[0-9]{0,1}.?[0-9])$/g)){
        m1 = values.split(" ")[0];
        m2 = values.split(" ")[1];
    }
    sizeF1 = $("#sizeF1").val();
    sizeF2 = $("#sizeF2").val();

    let params = {
        'nproc':nproc,
        'si1':sizeF1,
        'si2':sizeF2,
        'zf1':m1,
        'zf2':m2,
        'SPG':spg,
        'rank':rank,
        'iters':iters,
        'didimp':didimp
    }
// create query
    let query = Object.keys(params).map(
       k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k])
    ).join('&');

    response = await fetch('/seafile_client/predict_temp?'+query, {
        method : 'GET'
    });
    if (!response.ok){
        console.log(response)
        console.log('the total time of calcualtion is not calculed');
    }else{
        let data = await response.json()
        console.log(data)
    }
}

function handleNusSelection(){
    let nus = $("#nus");
    if(nus.val() == "True"){
        $(".nus_child").removeClass('hidden');
        $("#do_pgsane").val('True');
        $("#do_sane").val('False');
        handleSaneSelection();
    }else{
        $(".nus_child").addClass('hidden');
        $("#do_pgsane").val('False');
        $("#samplingfile").html('None');
    }
    predict_time_calculation();
}

function handlePgSaneSelection(){
    let pgsane = $("#do_pgsane");
    if(pgsane.val() == "True"){
        $("#samplingfile").attr('required',true).attr("readonly", false);
    }else{
        $("#samplingfile").attr('required',false).attr("readonly", true);
    }
    predict_time_calculation();
}

function handleSaneSelection(){
    let sane = $('#do_sane')
    if(sane.val() == "True"){
        $(".do_sane_child").removeClass('hidden');
        $("#nus").val('False');
        handleNusSelection();
    }else{
        $(".do_sane_child").addClass('hidden');
    }
    predict_time_calculation();
}