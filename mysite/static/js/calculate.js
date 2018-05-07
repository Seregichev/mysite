
function hideAlert(form_id, alert_html_class, hide_first_time, hide_second_time){
    var hide_delay = hide_first_time;  // starting timeout before first message is hidden
    var hide_next = hide_second_time;   // time in mS to wait before hiding next message

    $(form_id + " " + alert_html_class).slideDown().each( function(index,el) {
        window.setTimeout( function(){
            $(el).slideUp();  // hide the message
        }, hide_delay + hide_next*index);
    });

}

function LoadButton(form_id, button_html_class, reset_time){
    var $btn = $(form_id + " " + button_html_class).button('loading');

    if (reset_time){
         window.setTimeout(function () {
        $btn.button('reset');
        }, reset_time);
    }

}

function UpdateHtmlFromAjax(form, form_id, submit_button_html_class, alert_html_class) {
    var data = {};
    var $form = form;
    LoadButton(form_id, submit_button_html_class);

    data = $form.serialize();
    $.ajax({
      type: $form.attr('method'),
      url: $form.attr('action'),
      data: data
    }).done(function(receive) {

        console.log('Have a nice day');
      $(form_id).html($(receive).find(form_id).html());
      hideAlert(form_id, alert_html_class, 5000, 800);
      LoadButton(form_id, submit_button_html_class, 1000);

    }).fail(function() {
        $(form_id).prepend("<div class='alert alert-error alert-danger' role='alert'><a href='#' class='close' data-dismiss='alert' aria-label='close'>&times;</a>Нет соединения с сервером, повторите попытку.</div>");
        LoadButton(form_id, submit_button_html_class, 1000);

    });
}

 function CheckCalcControlFieldInCalculation(id) {
        var data = {};

        data.calc_control_voltage=$(id + ' #id_calc_control_voltage').val();
        data.calc_control_type=$(id + ' #id_calc_control_type').val();

        if (data.calc_control_voltage > 0  & data.calc_control_type != ''){

            data.calc_control_manufacturer=$(id + ' #id_calc_control_manufacturer').val();
            data.calc_control_series=$(id + ' #id_calc_control_series').val();
            data.calc_control_cpu=$(id + ' #id_calc_control_cpu').val();

            data.calc_control_time_delay=$(id + ' #id_calc_control_time_delay').val();
            data.calc_control_discret_input=$(id + ' #id_calc_control_discret_input').val();
            data.calc_control_discret_output=$(id + ' #id_calc_control_discret_output').val();
            data.calc_control_fast_discret_input=$(id + ' #id_calc_control_fast_discret_input').val();
            data.calc_control_fast_discret_output=$(id + ' #id_calc_control_fast_discret_output').val();
            data.calc_control_analog_0_10V_input=$(id + ' #id_calc_control_analog_0_10V_input').val();
            data.calc_control_analog_0_10V_output=$(id + ' #id_calc_control_analog_0_10V_output').val();
            data.calc_control_analog_0_20mA_input=$(id + ' #id_calc_control_analog_0_20mA_input').val();
            data.calc_control_analog_0_20mA_output=$(id + ' #id_calc_control_analog_0_20mA_output').val();
            data.calc_control_analog_rtd_input=$(id + ' #id_calc_control_analog_rtd_input').val();
            data.calc_control_profinet=$(id + ' #id_calc_control_profinet').val();
            data.calc_control_profibus=$(id + ' #id_calc_control_profibus').val();
            data.calc_control_modbus_tcp=$(id + ' #id_calc_control_modbus_tcp').val();
            data.calc_control_modbus_rtu=$(id + ' #id_calc_control_modbus_rtu').val();

            data.calc_control_manufacturer_relays=$(id + ' #id_calc_control_manufacturer_relays').val();
            data.calc_control_series_relays=$(id + ' #id_calc_control_series_relays').val();

            data.calc_control_manufacturer_terminals=$(id + ' #id_calc_control_manufacturer_terminals').val();
            data.calc_control_type_terminals=$(id + ' #id_calc_control_type_terminals').val();

            var csrf_token = $('.calc_form [name="csrfmiddlewaretoken"]').val();
            data["csrfmiddlewaretoken"] = csrf_token;

            var url = "/check_calc_control_fields/";
            $.ajax({
                url: url,
                type: 'POST',
                data: data,
                cache: true,
                success:function (receive) {
                    console.log(receive);
// {#                     Функция обновления выпадающего списка по id согласно полученному из receive_dict#}
                    function Update_SelectField(receive_dict,get_val_from_id, id) {
                        var selected ='';
                        $(id).html('<option value="" selected="selected">-----</option>');
                        $.each(receive_dict, function (k, v) {
                            if (get_val_from_id == v){selected = 'selected="selected"';} else {selected = '';}
                            $(id).append('<option value="'+ v +'"'+ selected +'>'+ v +'</option>');
                        });
                    }
// {#                     Функция доступности Integer field по id согласно полученному bool переменной#}
                    function Disabling_IntegerField(if_variable, id) {
                        if (if_variable){$( id ).prop( "disabled", false );}
                            else{$( id ).prop( "disabled", true );$( id ).val( "" );
                        }
                    }

                    Update_SelectField(receive.manufacturers, data.calc_control_manufacturer, id + ' #id_calc_control_manufacturer');
                    Update_SelectField(receive.series, data.calc_control_series, id + ' #id_calc_control_series');
                    Update_SelectField(receive.cpu, data.calc_control_cpu, id + ' #id_calc_control_cpu');

                    Disabling_IntegerField(receive.time_delay, id + ' #id_calc_control_time_delay');
                    Disabling_IntegerField(receive.discret_input, id + ' #id_calc_control_discret_input');
                    Disabling_IntegerField(receive.discret_output, id + ' #id_calc_control_discret_output');
                    Disabling_IntegerField(receive.fast_discret_input, id + ' #id_calc_control_fast_discret_input');
                    Disabling_IntegerField(receive.fast_discret_output, id + ' #id_calc_control_fast_discret_output');
                    Disabling_IntegerField(receive.analog_0_10V_input, id + ' #id_calc_control_analog_0_10V_input');
                    Disabling_IntegerField(receive.analog_0_10V_output, id + ' #id_calc_control_analog_0_10V_output');
                    Disabling_IntegerField(receive.analog_0_20mA_input, id + ' #id_calc_control_analog_0_20mA_input');
                    Disabling_IntegerField(receive.analog_0_20mA_output, id + ' #id_calc_control_analog_0_20mA_output');
                    Disabling_IntegerField(receive.analog_rtd_input, id + ' #id_calc_control_analog_rtd_input');
                    Disabling_IntegerField(receive.profinet, id + ' #id_calc_control_profinet');
                    Disabling_IntegerField(receive.profibus, id + ' #id_calc_control_profibus');
                    Disabling_IntegerField(receive.modbus_tcp, id + ' #id_calc_control_modbus_tcp');
                    Disabling_IntegerField(receive.modbus_rtu, id + ' #id_calc_control_modbus_rtu');

                    Update_SelectField(receive.terminal_manufacturers, data.calc_control_manufacturer_terminals, id + ' #id_calc_control_manufacturer_terminals');


                    id = $( id ).closest( "form" ).attr('id');
                    if (receive.general_checking){
                        $( '#'+id +' #calc_submit_button' ).prop( "disabled", false );
                    }else{
                        $( '#'+id +' #calc_submit_button' ).prop( "disabled", true );
                    }
                },
                error: function () {
                    console.log("ERROR ajax POST")

                }
            })
        }
    }


    function CheckCalcDriveFieldInCalculation(id) {
        var data = {};

        data.calc_drive_voltage=$(id + ' #id_calc_drive_voltage').val();
        data.calc_drive_power=$(id + ' #id_calc_drive_power').val();
        data.calc_drive_type=$(id + ' #id_calc_drive_type').val();

        if (data.calc_drive_voltage > 0 & data.calc_drive_power > 0 & data.calc_drive_type != ''){

            data.calc_drive_manufacturer=$(id + ' #id_calc_drive_manufacturer').val();
            data.calc_drive_series=$(id + ' #id_calc_drive_series').val();

            data.calc_drive_discret_input=$(id + ' #id_calc_drive_discret_input').val();
            data.calc_drive_discret_output=$(id + ' #id_calc_drive_discret_output').val();
            data.calc_drive_analog_input=$(id + ' #id_calc_drive_analog_input').val();
            data.calc_drive_analog_output=$(id + ' #id_calc_drive_analog_output').val();
            data.calc_drive_profinet=$(id + ' #id_calc_drive_profinet').val();
            data.calc_drive_profibus=$(id + ' #id_calc_drive_profibus').val();
            data.calc_drive_rs485=$(id + ' #id_calc_drive_rs485').val();

            data.calc_drive_manufacturer_terminals=$(id + ' #id_calc_drive_manufacturer_terminals').val();
            data.calc_drive_type_terminals=$(id + ' #id_calc_drive_type_terminals').val();

            var csrf_token = $('.calc_form [name="csrfmiddlewaretoken"]').val();
            data["csrfmiddlewaretoken"] = csrf_token;

            var url = "/check_calc_drive_fields/";
            $.ajax({
                url: url,
                type: 'POST',
                data: data,
                cache: true,
                success:function (receive) {
                    console.log(receive);
                    // {# Функция обновления выпадающего списка по id согласно полученному receive_dict #}
                    function Disabling_SelectField(receive_dict,get_val_from_id, id) {
                        var selected ='';
                        $(id).html('<option value="" selected="selected">-----</option>');
                        $.each(receive_dict, function (k, v) {
                            if (get_val_from_id == v){selected = 'selected="selected"';} else {selected = '';}
                            $(id).append('<option value="'+ v +'"'+ selected +'>'+ v +'</option>');
                        });
                    }
                    // {# Функция доступности chebox field по id согласно полученному bool переменной #}
                    function Disabling_IntegerField(if_variable, id) {
                        if (if_variable){$( id ).prop( "disabled", false );}
                            else{$( id ).prop( "disabled", true );$( id ).val( "" );
                        }
                    }

                    Disabling_SelectField(receive.manufacturers, data.calc_drive_manufacturer, id + ' #id_calc_drive_manufacturer');
                    Disabling_SelectField(receive.series, data.calc_drive_series, id + ' #id_calc_drive_series');


                    Disabling_IntegerField(receive.discret_input, id + ' #id_calc_drive_discret_input');
                    Disabling_IntegerField(receive.discret_output, id + ' #id_calc_drive_discret_output');
                    Disabling_IntegerField(receive.analog_input, id + ' #id_calc_drive_analog_input');
                    Disabling_IntegerField(receive.analog_output, id + ' #id_calc_drive_analog_output');
                    Disabling_IntegerField(receive.profinet, id + ' #id_calc_drive_profinet');
                    Disabling_IntegerField(receive.profibus, id + ' #id_calc_drive_profibus');
                    Disabling_IntegerField(receive.rs485, id + ' #id_calc_drive_rs485');

                    Disabling_SelectField(receive.terminal_manufacturers, data.calc_drive_manufacturer_terminals, id + ' #id_calc_drive_manufacturer_terminals');


                    var id ='';
                    id = $( id ).closest( "form" ).attr('id');
                    if (receive.general_checking){
                        $( '#'+id +' #calc_submit_button' ).prop( "disabled", false );
                    }else{
                        $( '#'+id +' #calc_submit_button' ).prop( "disabled", true );
                    }
                },
                error: function () {
                    console.log("ERROR ajax POST")

                }
            })
        }
    }
