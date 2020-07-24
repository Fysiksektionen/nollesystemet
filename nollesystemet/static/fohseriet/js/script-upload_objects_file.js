document.getElementById("script-upload_objects_file").parentNode.querySelector('.custom-file-input').onchange = function (e){
    const form = $(this).parents("form:first");
    if ( confirm('Är du säker på att du vill ladda upp filen ' + e.target.files[0].name +'? Åtgärden går inte att ångra.') ) {
        e.target.form.submit();
    }
}