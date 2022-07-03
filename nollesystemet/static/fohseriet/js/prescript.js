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

function getRegistrations({
        successFunction,
        failFunction,
        searchTerm = "",
        showNonConfirmed = "",
        showAttended = "",
        showPaid = "",
        happeningId = ""
    } ) {

    const searchTerms = [
        "search=" + searchTerm,
        "show_nonconfirmed=" + showNonConfirmed,
        "show_attended=" + showAttended,
        "show_paid=" + showPaid,
        "happening_id=" + happeningId
    ];

    const url = "/fohseriet/api/registrations?" + searchTerms.join("&");

    $.ajax({
        type: "GET",
        url: url,
        success: successFunction,
        cache: false
    })
    .fail(failFunction);
}

function updateRegistration({ id, paid, attended } = { } ) {
    var data = {};
    if( paid !== undefined ) {
        data["paid"] = paid;
    }
    if( attended !== undefined ) {
        data["attended"] = attended;
    }

    $.ajax({
        type: "POST",
        url: "/fohseriet/api/registrations/" + id,
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        cache: false
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        alert( "POST-request failed. Data probably not saved. Reload page." );
    });
}

function confirmRegistration( id ) {
    $.ajax({
        type: "POST",
        url: "/fohseriet/api/registrations/" + id + "/confirm",
        data: JSON.stringify({}),
        contentType: "application/json; charset=utf-8",
        cache: false
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        alert( "Misslyckades med att skicka bekräftelse. Ladda om sidan." );
    });
}
