
let select_2_args = {
        width: '250px',
        ajax: {
            url: document.getElementById('ajax-url').textContent,
            data: function (params) {
                var query = {
                    search: params.term,
                    format: 'json'
                };
                return query;
            }
        }
    };

 $('.on-field-players .heavyselect2widget').select2(select_2_args);

function select(row) {
    $(row).find('.heavyselect2widget').select2(select_2_args);
}

$('.member').formset(
    {
        formTemplate: '#id_empty_form',
        addCssClass: 'btn btn-secondary btn-sm',
        deleteText: 'Remove player',
        addText: 'Add a substitute',
        deleteContainerClass: 'delete-row',
        added: function (row) {
            select(row);
        }
    }
);

function toggle_registered(button) {
    let toggle_column = $(button).parent().parent();
    let first_name_column = toggle_column.siblings()[2];
    let last_name_column = toggle_column.siblings()[3];
    let member_column = toggle_column.siblings()[1];

    if ($(member_column).is(":hidden")) {
        $(member_column).show();
        $(first_name_column).hide();
        $(last_name_column).hide();
    } else {
        $(member_column).hide();
        $(first_name_column).show();
        $(last_name_column).show();
    }
}