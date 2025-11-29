function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

var csrftoken = getCookie('csrftoken');

$.fn.removeClassStartingWith = function (filter) {
    $(this).removeClass(function (index, className) {
        return (className.match(new RegExp("\\S*" + filter + "\\S*", 'g')) || []).join(' ')
    });
    return this;
};

Date.prototype.add_days = function(days) {
    var date = new Date(this.valueOf());
    date.setDate(date.getDate() + days);
    return date;
}

function get_dates(startDate, stopDate, includeStop=false) {
    var dateArray = new Array();
    var currentDate = startDate;
    while (currentDate < stopDate) {
        dateArray.push(new Date (currentDate));
        currentDate = currentDate.add_days(1);
    }

    if(includeStop) {
        dateArray.push(new Date(currentDate));
    }

    console.log(dateArray);
    return dateArray;
}

function date_to_YMD(date) {
    var d = date.getDate();
    var m = date.getMonth() + 1;
    var y = date.getFullYear();
    return '' + y + '-' + (m<=9 ? '0' + m : m) + '-' + (d <= 9 ? '0' + d : d);
}

function makeid(length) {
    var result           = '';
    var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < length; i++ ) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

function init_clickable_rows() {
    jQuery('tr[data-href]').off().on('click', function() {
        var url = $(this).data('href');
        window.location = url;
      });
}

function show_dynamic_modal() {
    $('#dynamic-modal').modal('show');
}

function hide_dynamic_modal() {
    $('#dynamic-modal').modal('hide');
}

function populate_dynamic_modal(type, url, data) {
    
    return $.ajax({
        type: type,
        url: url,
        data: data,
        contentType: 'json',
        dataType: 'html',
        beforeSend: function(xhr, settings) {
            if(!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    }).done(function(response) {
        $('#dynamic-modal-content').html(response);
    });

}

function init_clickable_dynamic_modals() {
    $('.show-dyn-modal').off('click').on('click', function() {
        let url = $(this).data('url');
        let parent = $(this).parent();
        if(parent.hasClass('no-link')) {
            parent.parent().off('click');
        }

        populate_dynamic_modal('GET', url, {}).done(function(resp) {
            show_dynamic_modal();
            init_clickable_dynamic_modals();
        });
    })
}

function init_delete_buttons() {
    $('.delete').off('click').on('click', function() {
        let url = $(this).data('url');

        populate_dynamic_modal('GET', url, {}).done(function(resp) {
            show_dynamic_modal();
        });

    });
}

function init_dropify_element(element, url='', required=false, clear_checkbox_id='') {
    if(url != '') {
        $(element).data('default-file', url);
    }

    if(required) {
        $(element).data('showRemove', false);
        $(element).dropify();
    } else {
        let dropify_element = $(element).dropify();
        let clear_checkbox = $(`#${clear_checkbox_id}`);

        dropify_element.on('dropify.beforeClear', function(event, element) {
            clear_checkbox.prop('checked', true);
        });

        dropify_element.on('change', function() {
            clear_checkbox.prop('checked', false);
        })

    }

}

function init_tooltips() {
    $('[data-toggle="tooltip"]').tooltip({html: true});
}

function is_element_empty( el ){
    return !$.trim(el.html())
}

function init_single_url_menu() {
    $('.nav-item[data-single-url] > a').off('click').on('click', function(e) {
        e.preventDefault();
        let url = $(this).attr('href');
        window.location.href = url;
        let closest_pane = $(this).closest('.main-icon-menu-pane.tab-pane');
        if(is_element_empty(closest_pane)) {
            $(body).addClass('enlarge-menu');
        }
    });

    let active_pane = $('.main-icon-menu-pane.tab-pane.active');
    if(is_element_empty(active_pane)) {
        $(body).addClass('enlarge-menu');
    }
}

function init_everything() {
    init_clickable_rows();
    init_delete_buttons();
    init_clickable_dynamic_modals();
    init_tooltips();
    init_single_url_menu();
}

jQuery(document).ready(function() {
    init_everything();
});