$(function(){
$("#addClass").click(function () {
        $('#qnimate').addClass('popup-box-on');
        $('#getperfil').load('/perfil');
          $('#social').hide();

          });

          $("#removeClass").click(function () {
        $('#qnimate').removeClass('popup-box-on');
          $('#social').show();


          });
})
