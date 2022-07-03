$('form .autosubmit').on('change', function() {
   this.form.submit();
});

$.ajaxSetup({
   beforeSend: function( xhr ) {
       xhr.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'))
   }
});