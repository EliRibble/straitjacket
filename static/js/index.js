function setup() {
    $.ajax({
        url: '/info',
        success: onGetLanguageInfo,
    });

    editor = ace.edit('editor');
    editor.setTheme('ace/theme/monokai');
    editor.getSession().setMode('ace/mode/javascript');

    $('#execute').click(onExecuteClick);
    disableButton();
}

function disableButton() {
    var $button = $('#execute');
    $button.attr('disabled', 'disabled');
    $button.addClass('disabled');
}

function enableButton() {
    var $button = $('#execute');
    $button.removeAttr('disabled');
    $button.removeClass('disabled');
}

function onGetLanguageInfo(data, textStatus, jqXHR) {
    var $languages = $('#language');
    $.each(data.languages, function(language_name, info) {
        $languages.append(
            $('<option></option>').val(language_name).html(info.visible_name)
        );
    });
    enableButton();
}

function onExecuteClick() {
    disableButton();
    var source = editor.getValue();
    var language = $('#language').val();
    $.ajax({
        type: 'POST',
        url: '/execute',
        success: onExecutionComplete,
        data: {
            language: language,
            source: source
        }
    });
}

function onExecutionComplete(data, textStatus, jqXHR) {
    $('#status').html(data.status);
    $('#results_accordion').show();
    if( 'compilation' in data ) {
        $('.compilation').show();
        $('#compilation-command').html(data.compilation.command);
        $('#compilation-stdout').html(data.compilation.stdout);
        $('#compilation-stderr').html(data.compilation.stderr);
        $('#compilation-returncode').html(data.compilation.returncode);
    } else {
        $('.compilation').hide();
    }
    if( data.runs.length > 0 ) {
        $('.stdout').show();
        $('.stderr').show();
        $('.returncode').show();
        $('#stdout').html(data.runs[0].stdout);
        $('#stderr').html(data.runs[0].stderr);
        if( data.runs[0] != 0 ) {
            $('#status').html($('#status').html() + ' (' + data.runs[0].returncode + ')');
        }
    } else {
        $('.stdout').hide();
        $('.stderr').hide();
        $('.returncode').hide();
    }

    enableButton();
}
$(setup);
