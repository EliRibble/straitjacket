function setup() {
    var editor = ace.edit('editor');
    editor.setTheme('ace/theme/monokai');
    editor.getSession().setMode('ace/mode/javascript');

    $.ajax({
        url: '/info',
        success: onGetLanguageInfo,
    });
}

function onGetLanguageInfo(data, textStatus, jqXHR) {
    var $languages = $('#language');
    $.each(data.languages, function(language_name, info) {
        $languages.append(
            $('<option></option>').val(language_name).html(info.visible_name)
        );
    });
}

$(setup);
