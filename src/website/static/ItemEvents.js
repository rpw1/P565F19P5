let arrAppointment;
let arrWorkout;
let arrMeal;

$(function () {
        
    $('#description').inputmask('Regex', {
        regex: "(?:[\\w\\d]+(\\s)*){1,5}",
        clearIncomplete: true
    });

    $('#description2').inputmask('Regex', {
        regex: "(?:[\\w\\d]+(\\s)*){1,5}",
        clearIncomplete: true
    });

    $("#start_time").inputmask("hh:mm", {
        placeholder: "hh:mm (24h)",
        alias: "datetime",
        clearIncomplete: true,
        oncomplete: function(){
            $("#end_time").focus();
    }});

    $("#start_sleep").inputmask("hh:mm", {
        placeholder: "hh:mm (24h)",
        alias: "datetime",
        clearIncomplete: true,
        oncomplete: function(){
            $("#end_sleep").focus();
    }});

    $("#end_time").inputmask("hh:mm", {
        placeholder: "hh:mm (24h)",
        alias: "datetime",
        clearIncomplete: true,
        oncomplete: function(){
            compare();
            $("#submit_appointment").focus();
    }});

    $("#end_sleep").inputmask("hh:mm", {
        placeholder: "hh:mm (24h)",
        alias: "datetime",
        clearIncomplete: true,
        oncomplete: function(){
            compare();
            $("#submit_sleep").focus();
    }});

    $(".date-input").inputmask("dd/mm/yyyy", {
        placeholder: "dd/mm/yyyy",
        alias: "datetime",
        clearIncomplete: true
    });

    $("#sleep_date").inputmask("mm/dd/yyyy", {
        placeholder: "mm/dd/yyyy",
        alias: "datetime",
        clearIncomplete: true
    });

    $('#title').inputmask('Regex', {
        max_length: 10,
        regex: "(?:[\\w\\d]+(\\s)*){1,5}",
        clearIncomplete: true
    });

    $("#difficulty").inputmask('Regex', {
        max_length: 1,
        regex: "^([1-5])",
        clearIncomplete: true,
    });

    $("#duration").inputmask('Regex', {
        max_length: 3,
        regex: "^([0-9]){1,3}",
        clearIncomplete: true,
    });

    $("#calories_burned").inputmask('Regex', {
        max_length: 4,
        regex: "^([0-9]){1,4}",
        clearIncomplete: true,
    });

    $('#training_type').inputmask('Regex', {
        max_length: 10,
        regex: "(?:[\\w\\d]+(\\s)*){1,5}",
        clearIncomplete: true,
       });

    $('[data-toggle="popover"]').popover();

    $("#total_calories").inputmask('Regex', {
        max_length: 4,
        regex: "^([0-9]){1,4}",
        clearIncomplete: true,
    });

    print(false, true);

});

let today = new Date();
let currentMonth = today.getMonth();
let currentYear = today.getFullYear();

let months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

showCalendar(currentMonth, currentYear);


function showCalendar(month, year) {
    let firstDay = (new Date(year, month)).getDay();
    let daysInMonth = new Date(year, month+1, 0).getDate();

    let tbl = document.getElementById("days");

    tbl.innerHTML = "";

    $("#month").text(months[month]);
    $("#month").data("val", month);
    $("#year").text(year);

    let date = 1;

    for (let i = 0; i < 6; i++) {
        let row = document.createElement("tr");
        row.className = `week week_${i}`;

        for (let j = 0; j < 7; j++) {
            if (i === 0 && j < firstDay) {
                let cell = document.createElement("td");
                let cellText = document.createTextNode("");
                cell.classList.add("inactive");
                cell.classList.add("disabled");
                cell.classList.add("bg-secondary");
                cell.setAttribute('data-day', date);
                cell.appendChild(cellText);
                row.appendChild(cell);
            } else if (date > daysInMonth) {
                break;
            } else {
                let cell = document.createElement("td");
                let cellText = document.createTextNode(date);
                if (date === today.getDate() && year === today.getFullYear() && month === today.getMonth()) {
                    $(cell).addClass("text-white active bg-primary today text-center font-weight-bold");
                    $(cell).attr('data-day', date);
                } else if (date < today.getDate() && year <= today.getFullYear() && month <= today.getMonth()){
                    $(cell).addClass("inactive disabled text-white bg-light text-muted text-center font-weight-light");
                    $(cell).attr('data-day', date);
                    $(cell).attr('disabled', 'disabled');
                } else if (date >= today.getDate() && year >= today.getFullYear() && month >= today.getMonth()) {
                    $(cell).addClass("active text-dark bg-white text-center font-weight-bold");
                    $(cell).attr('data-day', date);
                } else {
                    $(cell).addClass("text-center text-secondary");
                }
                cell.appendChild(cellText);
                row.appendChild(cell);
                date++;
            }
        }
        tbl.appendChild(row);
    }

}

$("#days td.active").on("click", function () {
    $('#date').val($(this).text() + "/" + ($('#month').data('val') + 1) + "/" + $('#year').text());
    if (is_empty() == true) {
        $("#submit_appointment").prop('disabled', true);
    } else {
        $("#submit_appointment").prop('disabled', false);
    }
    if ($("#description").val() == null || $("#description").val() == '') {
        $("#description").focus();
    } else {
        $("#submit_appointment").focus();
    }
});

$("#days td.active").on("click", function () {
    if (is_emptyWorkout() == true) {
        $("#submit_workout").prop('disabled', true);
    } else {
        $("#submit_workout").prop('disabled', false);
    }
    if ($("#description2").val() == null || $("#description2").val() == '') {
        $("#description2").focus();
    } else {
        $("#submit_workout").focus();
    }
});

$("#days td.active").on("click", function () {
    if (is_emptyWorkout() == true) {
        $("#submit_meal").prop('disabled', true);
    } else {
        $("#submit_meal").prop('disabled', false);
    }
    if ($("#calories_burned").val() == null || $("#calories_burned").val() == '') {
        $("#calories_burned").focus();
    } else {
        $("#submit_meal").focus();
    }
});


$("#days td.inactive").on("click", function () {
    iziToast.error({
        title: 'Error',
        message: "You can make appointments just today and forward",
        overlay: true,
        zindex: 999,
        position: 'center',
        timeout: 3000,
    });
});



$("#end_time, #start_time").focusout(function () {
    compare();
});

$("#end_time, #start_time, #date").keyup(function () {
    if (is_empty() == true) {
        $("#submit_appointment").prop('disabled', true);
    } else {
        $("#submit_appointment").prop('disabled', false);
    }
});

$("#difficulty, #title, #duration, #training_type").keyup(function () {
    if (is_emptyWorkout()) {
        $("#submit_workout").prop('disabled', true);
    } else {
        $("#submit_workout").prop('disabled', false);
    }
});


$("#total_calories, #entree, #sides, #drink").keyup(function () {
    if (is_emptyMeal()) {
        $("#submit_meal").prop('disabled', true);
    } else {
        $("#submit_meal").prop('disabled', false);
    }
});

$("#sleep_date, #start_sleep, #end_sleep").keyup(function () {
    if (is_emptySleep()) {
        $("#submit_sleep").prop('disabled', true);
    } else {
        $("#submit_sleep").prop('disabled', false);
    }
});

function clear_input() {
    $("#date").val('');
    $("#description").val('');
    $("#start_time").val('');
    $("#end_time").val('');
    $("#submit_appointment").prop('disabled', true);
}

function clear_workout(){
    $("#title").val('');
    $("#description2").val('');
    $("#difficulty").val('');
    $("#duration").val('');
    $("#training_type").val('');
    $("#content_id").val('');
    $("#submit_workout").prop('disabled', true);
}

function clear_meal() {
    $("#entree").val('');
    $("#sides").val('');
    $("#drink").val('');
    $("#total_calories").val('');
    $("#submit_meal").prop('disabled', true);
}

function clear_sleep() {
    $("#date").val('');
    $("#start_sleep").val('');
    $("#end_sleep").val('');
    $("#submit_sleep").prop('disabled', true);
}

function is_empty() {
    if (
        ($("#date").val() == null || $("#date").val() == '') ||
        ($("#start_time").val() == null || $("#start_time").val() == '') ||
        ($("#end_time").val() == null || $("#end_time").val() == '')
    ) {
        return true;
    }
    return false;
}

function is_emptyWorkout() {
    if (
        ($("#title").val() == null || $("#title").val() == '') ||
        ($("#difficulty").val() == null || $("#difficulty").val() == '') ||
        ($("#duration").val() == null || $("#duration").val() == '') ||
        ($("#training_type").val() == null || $("#training_type").val() == '')
    ) {
        return true;
    }
    return false;
}

function is_emptySleep() {
    if (
        (($("#sleep_date").val() == null || $("#sleep_date").val() == '') &&
        ($("#start_sleep").val() == null || $("#start_sleep").val() == '') &&
        ($("#end_sleep").val() == null || $("#end_sleep").val() == ''))
    ) {
        return true;
    }
    return false;
}

function is_emptyMeal() {
    if (
        (($("#entree").val() == null || $("#entree").val() == '') &&
        ($("#sides").val() == null || $("#sides").val() == '') &&
        ($("#drink").val() == null || $("#drink").val() == '')) ||
        ($("#total_calories").val() == null || $("#total_calories").val() == '')
    ) {
        return true;
    }
    return false;
}

function compare() {
    var startTime = Date.parse(get_Date($("#start_time").val()));
    var endTime = Date.parse(get_Date( $("#end_time").val()));

    if (startTime > endTime) {
        $("#submit_appointment").prop('disabled', true);
        clear_input();
        iziToast.warning({
            title: 'Caution',
            message: "Start Time is greater than end time",
            overlay: true,
            zindex: 999,
            position: 'center',
            timeout: 2000,
        });
    }
    if (startTime == endTime) {
        $("#submit_appointment").prop('disabled', true);
        clear_input();
        iziToast.warning({
            title: 'Caution',
            message: "Start Time equals end time",
            overlay: true,
            zindex: 999,
            position: 'center',
            timeout: 2000,
        });
    }
}

function is_past_date() {
    var today = new Date();
    var arrDate = GetDateInput();
    var selected_date = new Date(arrDate[2], arrDate[1]-1, arrDate[0], 0, 0, 0, 0);
    if (selected_date < today) {
        return true;
    }
    return false;
}

function GetDateInput() {
    var date = $("#date").val();
    return date.split("/");
}

function is_overlap(sTime, eTime) {
    if (sTime == undefined || eTime == undefined) {
        sTime = $("#start_time").val();
        eTime = $("#end_time").val();
    }
    if (+get_Date(sTime) < +get_Date(eTime)) {
        var timeList = localStorage.getItem("tbAppointment");
        if (timeList == null || timeList == "[null]"){
            return false
        } else {
            timeList = JSON.parse(timeList);
        }

        for (let i = 0; i < timeList.length; i++) {
            const element = timeList[i];
            if (element.date == $("#date").val()) {
                if (
                    sTime > element.start_time && sTime < element.end_time ||
                    eTime > element.start_time && eTime < element.end_time ||
                    sTime < element.start_time && eTime >= element.end_time ||
                    sTime <= element.start_time && eTime > element.end_time ||
                    sTime == element.start_time && eTime == element.end_time

                ) {
                    return true;
                }
            }
        }
        return false;
    } else {
        return false;
    }
}

function get_Date(time, arrDate = false) {
    if (arrDate == false) {
        var arrDate = GetDateInput();
    }
    var date = new Date(arrDate[2], arrDate[1]-1, arrDate[0], 0, 0, 0, 0);
    var _t = time.split(":");
    date.setHours(_t[0], _t[1], 0, 0);
    return date;
}

function print(clear = false, init = false, edit = false) {
    if (clear != false){
        $("#appointment_list > tbody").html("");
        return true;
    };
    var data = localStorage.getItem("tbAppointment");
    data = JSON.parse(data);
    if (data[0] !== null) {
        $("#appointment_list > tbody").html("");
        $(`.week td.active`).removeClass('badge1');
        $(`.week td.active`).removeAttr( "data-badge" );
        let date = [];
        if (data.length !== 0) {
            for (let i = 0; i < data.length; i++) {
                const element = data[i];
                $("#appointment_list > tbody").append(
                    `
                    <tr>
                        <td class="text-center align-middle">${element.date}</td>
                        <td class="text-center align-middle">${element.description}</td>
                        <td class="text-center align-middle">${element.start_time}</td>
                        <td class="text-center align-middle">${element.end_time}</td>
                        <td class="text-center align-middle">
                            <button class="btn btn-primary btn-sm " onclick="edit_appointment(${element.id})"><i class="fas fa-pencil-alt"></i></button>
                            <button class="btn btn-danger btn-sm " onclick="delete_appointment(${element.id})"><i class="fas fa-trash"></i></button>
                        </td>
                    </tr>
                    `
                );
                let currDate = element.date.split("/");
                date.push(currDate[0]);
            }
            date = [...new Set(date)];
            date.forEach(element => {
                let cell = document.querySelector(`.week > td.active[data-day='${element}']`);
                put_badges_new(cell);
            });
        } else {
            let element = document.querySelector(`.week > td.active[data-badge]`);
            if (element !== null) {
                put_badges_new(element);
            }
        }
    }
}

function put_badges_new(cell) {
    var data = localStorage.getItem("tbAppointment");
    data = JSON.parse(data);
    if (data == null) {return}
    if (data[0] !== null) {
        let counter = 0;
        for (let i = 0; i < data.length; i++) {
            const element = data[i];
            if (cell.getAttribute("data-day") == element.date.slice(0,2)) {
                counter++;
            }
        }

        if (counter >= 1) {
            cell.classList.add("badge1");
            cell.setAttribute('data-badge', counter);
        }
        if (counter <= 0) {
            cell.classList.remove("badge1");
            cell.removeAttribute('data-badge');
        }
    }
}

