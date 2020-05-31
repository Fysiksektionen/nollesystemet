function updateElementIndex(element, prefix, newIndex){
    var oldIndexTextRegex = new RegExp('(' + prefix + '-\\d+)');
    var newIndexText = prefix + '-' + newIndex;
    if(element.attr('for')) element.attr('for', element.attr('for').replace(oldIndexTextRegex, newIndexText));
    if(element.attr('name')) element.attr('name', element.attr('name').replace(oldIndexTextRegex, newIndexText));
    if(element.attr('id')) element.attr('id', element.attr('id').replace(oldIndexTextRegex, newIndexText));
}

function cloneForm(selector, prefix) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    newElement.find(':input, label').each(function() {
        updateElementIndex($(this), prefix, total);
    });
    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
}

function deleteForm(buttonElement, formSelector, prefix){
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if(total > 1){
        buttonElement.closest(formSelector).remove();
        var forms = $(formSelector);
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        for(var i = 0; i < forms.length; i++){
            $(forms.get(i)).find(':input, label').each(function() {
                updateElementIndex($(this), prefix, i);
            });
        }
    }
}

function filter_table_with_id(tableId, searchValue) {

}