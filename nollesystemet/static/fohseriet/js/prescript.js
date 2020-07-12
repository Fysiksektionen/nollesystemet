function deleteForm(form){
    form.find("input[id*='DELETE']").each(function(){
        this.value = "on";
    });
    form.css("display", "none");
}

function addform(prefix) {
    let totalFormsElement = $('#id_' + prefix + '-TOTAL_FORMS');
    var numOfForms = totalFormsElement.val();
    var emptyFormElement = $("." + prefix + "-form.emptyform");

    var newFormHTML = emptyFormElement.wrap('<p/>').parent().html().replace(/__prefix__/g, numOfForms);
    emptyFormElement.unwrap();

    var newForm = $.parseHTML(newFormHTML);
    $(newForm).removeAttr("style");
    $(newForm).removeClass("emptyform");

    emptyFormElement.before(newForm);

    totalFormsElement.val(parseInt(numOfForms) + 1);
    $(newForm).find(".remove-" + prefix + "-form-btn").click(function (){
        deleteForm($(newForm));
    });
}

function bindFormset(prefix) {
    $(".add-" + prefix + "-form-btn").click(function (){
        addform(prefix)
    });
    $(".remove-" + prefix + "-form-btn").click(function (){
        deleteForm($(this).closest("." + prefix + "-form"));
    });
}