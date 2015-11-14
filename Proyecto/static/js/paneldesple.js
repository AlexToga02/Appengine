$(function(){
$("#addClass").click(function () {
        $('#qnimate').addClass('popup-box-on');
        $('#tareas').load('/tareas'));
          $('#social').hide();


          });

          $("#removeClass").click(function () {
        $('#qnimate').removeClass('popup-box-on');
          $('#social').show();
          });
})
