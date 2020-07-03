$('.bootstrap-select').selectpicker();

// If delete-button present – add waring on submit and disable all
// validation by disabling all fields prior to submit.
$(":input[type='submit'][name='delete']").click(function (e) {
    const form = $(this).parents("form:first");
    if ( confirm('Är du säker på att du vill radera detta objekt? Åtgärden går inte att ångra.') ) {
        $(form).find(":input:not([type='submit']):not([name='csrfmiddlewaretoken'])").each(function () {
            $(this).removeAttr( "required" );
            $(this).attr( "disabled", true );
        });
    } else {
        e.preventDefault();
    }
})

