let arrAppointment;
let arrWorkout;

$(function () {
    if (typeof (Storage) !== "undefined") {
        arrAppointment = localStorage.getItem("tbAppointment");
        arrWorkout = localStorage.getItem("tbWorkout");
        arrAppointment = JSON.parse(arrAppointment);
        arrWorkout = JSON.parse(arrWorkout);
        $("#btn_clear_storage").prop('disabled', false);
        $(`#btn_clear_storage`).show();
        $("#btn_clear_storageWorkout").prop('disabled', false);
        $(`#btn_clear_storageWorkout`).show();
        if (arrAppointment == null || arrAppointment == "[null]"){
            $("#btn_clear_storage").prop('disabled', true);
            $(`#btn_clear_storage`).hide();
            arrAppointment = [];
            arrAppointment.push(JSON.parse(localStorage.getItem('tbAppointment')));
            localStorage.setItem('tbAppointment', JSON.stringify(arrAppointment));
        }
        if(arrWorkout == null || arrWorkout == "[null]"){
            $("#btn_clear_storageWorkout").prop('disabled', true);
            $(`#btn_clear_storageWorkout`).hide();
            arrWorkout = [];
            arrWorkout.push(JSON.parse(localStorage.getItem('tbWorkout')));
            localStorage.setItem('tbWorkout', JSON.stringify(arrWorkout));
        }
    } 
        

    $('#description').inputmask('Regex', {
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

    $("#end_time").inputmask("hh:mm", {
        placeholder: "hh:mm (24h)",
        alias: "datetime",
        clearIncomplete: true,
        oncomplete: function(){
            compare();
            $("#submit").focus();
    }});

    $(".date-input").inputmask("dd/mm/yyyy", {
        placeholder: "dd/mm/yyyy",
        alias: "datetime",
        clearIncomplete: true
    });

    $("#difficulty").inputmask('Regex', {
        max_length: 1,
        regex: "^([1-5])",
        clearIncomplete: true,
        oncomplete: function(){
            $("#submit_workout").focus();
    }});

    $('[data-toggle="popover"]').popover();

    print(false, true);

});

let today = new Date();
let currentMonth = today.getMonth();
let currentYear = today.getFullYear();

let months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

showCalendar(currentMonth, currentYear);


function showCalendar(month, year) {
    let firstDay = (new Date(year, month)).getDay();
    //let daysInMonth = 32 - new Date(year, month, 32).getDate();
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
                    put_badges_new(cell);
                } else if (date < today.getDate() && year <= today.getFullYear() && month <= today.getMonth()){
                    $(cell).addClass("inactive disabled text-white bg-light text-muted text-center font-weight-light");
                    $(cell).attr('data-day', date);
                    $(cell).attr('disabled', 'disabled');
                } else if (date >= today.getDate() && year >= today.getFullYear() && month >= today.getMonth()) {
                    $(cell).addClass("active text-dark bg-white text-center font-weight-bold");
                    $(cell).attr('data-day', date);
                    put_badges_new(cell);
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
        $("#submit").prop('disabled', true);
    } else {
        $("#submit").prop('disabled', false);
    }
    if ($("#description").val() == null || $("#description").val() == '') {
        $("#description").focus();
    } else {
        $("#submit").focus();
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

function make_appointment() {
    if (is_empty() == false) {
        is_past_date();
        compare();
        if (is_overlap() == false) {
            var appointment = {
                id: $("#date").inputmask('unmaskedvalue')+$("#start_time").inputmask('unmaskedvalue')+$("#end_time").inputmask('unmaskedvalue'),
                date: $("#date").val(),
                description: $("#description").val(),
                start_time: $("#start_time").val(),
                end_time: $("#end_time").val(),
            };

            SaveDataToLocalStorage(appointment);
            $("#btn_clear_storage").prop('disabled', false);
            $(`#btn_clear_storage`).show();
            print();

            clear_input();
            iziToast.success({
                title: 'Success',
                message: 'Appointment created',
            });
        } else {
            clear_input();
            iziToast.error({
                title: 'Error',
                message: "This appointment is overlaping another one",
                overlay: true,
                zindex: 999,
                position: 'center',
                timeout: 3000,
            });
        }
    } else {
        iziToast.error({
            title: 'Error',
            message: "All input fields are needed in order to make an appointment",
            overlay: true,
            zindex: 999,
            position: 'center',
            timeout: 3000,
        });
    }
}

function make_custom_workout() {
    if (true) {
        // is_past_date();
        // compare();
        if (true) {
            var workout = {
                title: $("#title").val(),
                description2: $("#description2").val(),
                difficulty: $("#difficulty").val(),
                duration: $("#duration").val(),
                training_type: $("#training_type").val(),
            };

            SaveDataToLocalStorageWorkout(workout);
            $("#btn_clear_storageWorkout").prop('disabled', false);
            $(`#btn_clear_storageWorkout`).show();
            print();

            clear_workout();
            iziToast.success({
                title: 'Success',
                message: 'Workout created',
            });
        } else {
            clear_workout();
            iziToast.error({
                title: 'Error',
                message: "This workout is overlapping another one",
                overlay: true,
                zindex: 999,
                position: 'center',
                timeout: 3000,
            });
        }
    } else {
        iziToast.error({
            title: 'Error',
            message: "All input fields are needed in order to make a workout",
            overlay: true,
            zindex: 999,
            position: 'center',
            timeout: 3000,
        });
    }
}

$("#end_time, #start_time").focusout(function () {
    compare();
});

$("#end_time, #start_time, #date").keyup(function () {
    if (is_empty() == true) {
        $("#submit").prop('disabled', true);
    } else {
        $("#submit").prop('disabled', false);
    }
});

$("#difficulty").keyup(function () {
    if ($("#difficulty").val() == null || $("#difficulty").val() == '') {
        $("#submit_workout").prop('disabled', true);
    } else {
        $("#submit_workout").prop('disabled', false);
    }
});

$("#difficulty").inputmask('Regex', {
    max_length: 1,
    regex: "^([1-5])",
    clearIncomplete: true,
    oncomplete: function(){
        $("#submit").focus();
}});

function clear_input() {
    $("#date").val('');
    $("#description").val('');
    $("#start_time").val('');
    $("#end_time").val('');
    $("#submit").prop('disabled', true);
}

function clear_workout(){
    $("#title").val('');
    $("#description2").val('');
    $("difficulty").val('');
    $("#duration").val('');
    $("#training_type").val('');
    $("#submit").prop('disabled', true);
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

function compare() {
    var startTime = Date.parse(get_Date($("#start_time").val()));
    var endTime = Date.parse(get_Date( $("#end_time").val()));

    if (startTime > endTime) {
        $("#submit").prop('disabled', true);
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
        $("#submit").prop('disabled', true);
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

function printWorkout(clear = false, init = false, edit = false) {
    if (clear != false){
        $("#workout_list > tbody").html("");
        return true;
    };
    var data2 = localStorage.getItem("tbWorkout");
    data2 = JSON.parse(data2);
    if (data2[0] !== null) {
        $("#workout_list > tbody").html("");
        $(`.week td.active`).removeClass('badge1');
        $(`.week td.active`).removeAttr( "data-badge" );
        let date = [];
        if (data2.length !== 0) {
            for (let i = 0; i < data2.length; i++) {
                const element = data2[i];
                $("#workout_list > tbody").append(
                    `
                    <tr>
                        <td class="text-center align-middle">${element.title}</td>
                        <td class="text-center align-middle">${element.description2}</td>
                        <td class="text-center align-middle">${element.difficulty}</td>
                        <td class="text-center align-middle">${element.duration}</td>
                        <td class="text-center align-middle">${element.training_type}</td>
                        <td class="text-center align-middle">
                            <button class="btn btn-primary btn-sm " onclick="edit_workout(${element.id})"><i class="fas fa-pencil-alt"></i></button>
                            <button class="btn btn-danger btn-sm " onclick="delete_workout(${element.id})"><i class="fas fa-trash"></i></button>
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
                put_badges_newWorkout(cell);
            });
        } else {
            let element = document.querySelector(`.week > td.active[data-badge]`);
            if (element !== null) {
                put_badges_newWorkout(element);
            }
        }
    }
}

function SaveDataToLocalStorage(data)
{
    var a = [];
    a = JSON.parse(localStorage.getItem('tbAppointment'));

    var a = a.filter(function (el) {
        return el != null;
    });

    a.push(data);
    a.sort(function (sTime1, sTime2) {
        let temp3 = parseInt(sTime1.date.slice(0,2))
        let temp4 = parseInt(sTime2.date.slice(0,2))
        let temp1 = Date.parse(get_Date(sTime1.start_time));
        let temp2 = Date.parse(get_Date(sTime2.start_time));


        if (temp3 > temp4) return 1;
        if (temp3 < temp4) return -1;
        if (temp1 > temp2) return 1;
        if (temp1 < temp2) return -1;
    });
    localStorage.setItem('tbAppointment', JSON.stringify(a));
}

function SaveDataToLocalStorageWorkout(data2)
{
    var a = [];
    a = JSON.parse(localStorage.getItem('tbWorkout'));

    var a = a.filter(function (el) {
        return el != null;
    });

    a.push(data2);
    a.sort(function (sTime1, sTime2) {
        let temp3 = parseInt(sTime1.date.slice(0,2))
        let temp4 = parseInt(sTime2.date.slice(0,2))
        let temp1 = Date.parse(get_Date(sTime1.start_time));
        let temp2 = Date.parse(get_Date(sTime2.start_time));


        if (temp3 > temp4) return 1;
        if (temp3 < temp4) return -1;
        if (temp1 > temp2) return 1;
        if (temp1 < temp2) return -1;
    });
    localStorage.setItem('tbWorkout', JSON.stringify(a));
}

function clear_storage(){
    localStorage.clear();
    var arrAppointment = [];
    arrAppointment.push(JSON.parse(localStorage.getItem('tbAppointment')));
    localStorage.setItem('tbAppointment', JSON.stringify(arrAppointment));
    $("#btn_clear_storage").prop('disabled', true);
    $(`#btn_clear_storage`).hide();
    $(`.week td.active`).removeClass('badge1');
    $(`.week td.active`).removeAttr( "data-badge" );
    print(true);
    iziToast.success({
        title: 'Success',
        message: 'All appointments deleted',
    });
}

function clear_storageWorkout(){
    localStorage.clear();
    var arrWorkout = [];
    arrWorkout.push(JSON.parse(localStorage.getItem('tbWorkout')));
    localStorage.setItem('tbWorkout', JSON.stringify(arrWorkout));
    $("#btn_clear_storageWorkout").prop('disabled', true);
    $(`#btn_clear_storageWorkout`).hide();
    
    print(true);
    iziToast.success({
        title: 'Success',
        message: 'All Workouts deleted',
    });
}

function edit_appointment(id){
    var data = localStorage.getItem("tbAppointment");
    data = JSON.parse(data);
    if (data[0] !== null) {
        for (let i = 0; i < data.length; i++) {
            const element = data[i];
            if (element.id == id) {
                $("#date").val(element.date);
                $("#description").val(element.description);
                $("#start_time").val(element.start_time);
                $("#end_time").val(element.end_time);
                $("#submit").prop('disabled', false);
                delete_appointment(id);
            }
        }
    }
};

function edit_workout(id){
    var data = localStorage.getItem("tbWorkout");
    data = JSON.parse(data);
    if (data[0] !== null) {
        for (let i = 0; i < data.length; i++) {
            const element = data[i];
            if (element.id == id) {
                $("#title").val(element.title);
                $("#description2").val(element.description2);
                $("#difficulty").val(element.difficulty);
                $("#duration").val(element.duration);
                $("#training_type").val(element.training_type);
                $("#submit").prop('disabled', false);
                delete_appointment(id);
            }
        }
    }
};

function delete_appointment(id){
    var data = localStorage.getItem("tbAppointment");
    data = JSON.parse(data);
    if (data[0] !== null) {
        for (let i = 0; i < data.length; i++) {
            const element = data[i];
            if (element == null) {
                data.splice(i, 1);
            }
            if (element.id == id) {
                data.splice(i, 1);
            }
        }
        data = data.filter(function (el) {
            return el != null;
        });

        localStorage.setItem('tbAppointment', JSON.stringify(data));
        print(false, false, true);
        iziToast.success({
            title: 'Success',
            message: 'Appointment deleted',
        });

    }
};

function delete_workout(id){
    var data2 = localStorage.getItem("tbWorkout");
    data2 = JSON.parse(data2);
    if (data2[0] !== null) {
        for (let i = 0; i < data2.length; i++) {
            const element = data2[i];
            if (element == null) {
                data2.splice(i, 1);
            }
            if (element.id == id) {
                data2.splice(i, 1);
            }
        }
        data2 = data2.filter(function (el) {
            return el != null;
        });

        localStorage.setItem('tbWorkout', JSON.stringify(data2));
        print(false, false, true);
        iziToast.success({
            title: 'Success',
            message: 'Workout deleted',
        });

    }
};


function put_badges_new(cell) {
    var data = localStorage.getItem("tbAppointment");
    data = JSON.parse(data);
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

function put_badges_newWorkout(cell) {
    var data2 = localStorage.getItem("tbWorkout");
    data2 = JSON.parse(data2);
    if (data2[0] !== null) {
        let counter = 0;
        for (let i = 0; i < data2.length; i++) {
            const element = data2[i];
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
function sort_database(data){
    return data.sort(function (sTime1, sTime2) {
        let temp3 = parseInt(sTime1.date.slice(0,1))
        let temp4 = parseInt(sTime2.date.slice(0,1))
        let temp1 = Date.parse(get_Date(sTime1.start_time));
        let temp2 = Date.parse(get_Date(sTime2.start_time));


        if (temp3 > temp4) return 1;
        if (temp3 < temp4) return -1;
        if (temp1 > temp2) return -1;
        if (temp1 < temp2) return 1;
    });
}