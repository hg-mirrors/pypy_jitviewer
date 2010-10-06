
function select_loop(no)
{
    $.get('/loop?no=' + no, undefined, function(arg) {
        $("#main").html(arg);
        $("#main").focus();
    });
}