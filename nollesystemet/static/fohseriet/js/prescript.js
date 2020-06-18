function deleteForm(prefix, form){
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
}

function bindFormset(prefix) {
    $(".add-" + prefix).click(function (){
        addform(prefix)
    });
    $(".remove-" + prefix).click(function (){
        deleteForm(prefix, $(this).closest("." + prefix + "-form"))
    });
}

function addFormWithSubFormset(parentPrefix, childPrefix) {
    let totalFormsElement = $('#id_' + parentPrefix + '-TOTAL_FORMS');
    var numOfForms = totalFormsElement.val();
    var emptyFormElement = $("." + parentPrefix + "-form.emptyform");

    var temp = emptyFormElement.wrap('<p/>').parent().html().replace(/__prefix__/g, numOfForms);
    var newFormHTML = temp.replace(/__parent_num__/g, numOfForms);

    emptyFormElement.unwrap();

    var newForm = $.parseHTML(newFormHTML);
    $(newForm).removeAttr("style");
    $(newForm).removeClass("emptyform");

    emptyFormElement.before(newForm);

    totalFormsElement.val(parseInt(numOfForms) + 1);

    bindFormset(numOfForms + "-" + childPrefix);
}

function bindNestedFormset(parentPrefix, childPrefix) {
    $(".remove-" + parentPrefix).click(function (){
        deleteForm(parentPrefix, $(this).closest("." + parentPrefix + "-form"));
    });
    $(".add-" + parentPrefix).click(function (){
        addFormWithSubFormset(parentPrefix, childPrefix);
    });
}