function deleteForm(formclass, prefix, form){
    form.find("input[id*='DELETE']").each(function(){
        this.value = "on";
    });
    form.css("display", "none");
}

function addform(formclass, prefix) {
    let totalFormsElement = $('#id_' + prefix + '-TOTAL_FORMS');
    var numOfForms = totalFormsElement.val();
    var emptyFormElement = $("." + formclass + "-form.emptyform");

    var newFormHTML = emptyFormElement.wrap('<p/>').parent().html().replace(/__prefix__/g, numOfForms);
    emptyFormElement.unwrap();

    var newForm = $.parseHTML(newFormHTML);
    $(newForm).removeAttr("style");
    $(newForm).removeClass("emptyform");

    emptyFormElement.before(newForm);

    totalFormsElement.val(parseInt(numOfForms) + 1);
}

function bindFormset(formclass, prefix) {
    $(".add-" + formclass).click(function (){
        addform(formclass, prefix)
    });
    $(".remove-" + formclass).click(function (){
        deleteForm(formclass, prefix, $(this).closest("." + formclass + "-form"))
    });
}