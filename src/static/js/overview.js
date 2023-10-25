window.onload = () => {
  addEventListenersToDynamicElements();
};
$("#add_subject_form").click(function () {
  let clone = $("#base_subject_form").clone();
  clone.removeClass("d-none");
  clone.addClass("subject_form");
  clone.attr("id", "subject_form");
  clone.find(".subject_main_part")[0].remove();
  $("#subject_forms").append(clone);

  addEventListenersToDynamicElements();
});
$("#delete_employee_button").click(function (element) {
  $.ajax({
    type: "DELETE",
    headers: {
      "X-CSRFToken": $(element.target).parent().parent().attr("csrf"),
    },
    async: false,
    data: {
      id: parseInt(
        $(element.target).parent().parent().parent().parent().attr("person_id")
      ),
    },
    url: "persons/delete_person",
    success: function (response) {},
    error: function (response) {},
  });
  location.reload(true);
});
function add_subject_holding_type_button_on_click(element) {
  const form = element.target.parentElement.parentElement.parentElement;
  if ($(form).find("#id_subject_study_level").val() === null) {
    alert("Уровень обучения не может быть пустым");
    return;
  }
  const subjectMainPart = $("#base_subject_form")
    .find(".subject_main_part")
    .clone()[0];
  const type_select = $(subjectMainPart).find("#id_holding_type");
  const name = $(form).find("#id_subject_name").val();
  const study_level = $(form).find("#id_subject_study_level").val();
  $.ajax({
    async: false,
    data: { name: name, study_level: study_level },
    url: "subjects/get_subject_holding_type_by_study_level_name",
    success: function (response) {
      const responseData = response.data;
      type_select.prop("disabled", false);
      for (let item of responseData[0]) {
        type_select.append($(`<option value="${item}">${item} </option>`));
      }
    },
    error: function (response) {
      console.log(response.responseJSON.errors);
    },
  });
  form.append(subjectMainPart);
  addEventListenersToDynamicElements();
}
function add_subject_cipher_and_direction_button_on_click(element) {
  const form = element.target.parentElement;
  if ($(form.parentElement).find("#id_holding_type").val() === null) {
    alert("Тип занятия не может быть пустым");
    return;
  }

  const select = $(`
  <div class="row mt-3 align-items-center">
  <div class="col-md-auto">
  <select 
  id="subject_cipher_and_direction_select" 
  name="subject_cipher_and_direction"
  class=" subject_cipher_and_direction_select form-select form-select">   
  <option disabled selected> 
  </option>
  </select>
    </div>
  <div class="col-md-auto">
    <button type="button" class="btn btn-danger delete_select">-</button>

  </div>
  
`)[0];
  const name = $(form.parentElement.parentElement)
    .find("#id_subject_name")
    .val();
  const study_level = $(form.parentElement.parentElement)
    .find("#id_subject_study_level")
    .val();
  const holding_type = $(form.parentElement.parentElement)
    .find("#id_holding_type")
    .val();
  $.ajax({
    async: false,
    data: { name: name, study_level: study_level, holding_type: holding_type },
    url: "subjects/get_subject_ciphers_and_directions_by_name_level_holding",

    success: function (response) {
      const responseData = response.data;
      for (let item of responseData[0]) {
        $($(select).find("select")[0]).append(
          $(`<option value="${item}">${item} </option>`)
        );
      }
    },
    error: function (response) {
      console.log(response.responseJSON.errors);
    },
  });
  form.append(select);
  addEventListenersToDynamicElements();
}
function add_subject_group_button_on_click(element) {
  const form = element.target.parentElement;
  if ($(form.parentElement).find("#id_holding_type").val() === null) {
    alert("Тип занятия не может быть пустым");
    return;
  }
  if (
    $(form.parentElement)
      .find("#add_subject_cipher_and_direction")
      .parent()
      .find("select").length === 0
  ) {
    alert("Выберите направления");
    return;
  }
  for (let item of $(form.parentElement)
    .find("#add_subject_cipher_and_direction")
    .parent()
    .find("select")) {
    if ($(item).val() === null) {
      alert("Направление не может быть пустым");
      return;
    }
  }
  const select = $(`
  <div class="row mt-3 align-items-center">
  <div class="col-md-auto">
  <select 
  id="subject_group_select" 
  name="subject_group" 
  class="subject_group_select form-select form-select">   

  <option disabled selected> 

  </option>

  </select>
  </div>
  <div class="col-md-auto">
    <button type="button" class="btn btn-danger delete_select">-</button>

  </div>
  `)[0];
  const name = $(form.parentElement.parentElement)
    .find("#id_subject_name")
    .val();

  const study_level = $(form.parentElement.parentElement)
    .find("#id_subject_study_level")
    .val();
  const holding_type = $(form.parentElement.parentElement)
    .find("#id_holding_type")
    .val();
  const ciphers_and_directions = [];

  for (let select of $(form.parentElement.parentElement)
    .find("#add_subject_cipher_and_direction")
    .parent()
    .find("select")) {
    ciphers_and_directions.push($(select).val());
  }

  $.ajax({
    async: false,
    data: {
      name: name,
      study_level: study_level,
      holding_type: holding_type,
      ciphers_and_directions: ciphers_and_directions,
    },
    url: "subjects/get_subject_groups_by_name_level_holding_cipher_direction",
    success: function (response) {
      const responseData = response.data;

      for (let item of responseData) {
        $($(select).find("select")).append(
          $(`<option value="${item}">${item} </option>`)
        );
      }
    },
    error: function (response) {
      console.log(response.responseJSON.errors);
    },
  });
  form.append(select);
  addEventListenersToDynamicElements();
}
function subject_name_on_select(element) {
  const form = element.target.parentElement.parentElement.parentElement;
  $(form).find(".subject_main_part").remove();

  const level_select = $(form).find("#id_subject_study_level");
  level_select.empty();
  level_select.append($(`<option disabled selected></option>`));
  $.ajax({
    async: false,
    data: { name: $(element.target).val() },
    url: "subjects/get_subject_study_level_by_name",
    success: function (response) {
      const responseData = response.data;
      level_select.prop("disabled", false);
      for (let item of responseData) {
        level_select.append($(`<option value="${item}">${item} </option>`));
      }
    },
    error: function (response) {
      console.log(response.responseJSON.errors);
    },
  });
}
function holding_type_on_select(element) {
  const form = element.target.parentElement.parentElement;

  $(form)
    .find("#add_subject_cipher_and_direction")
    .parent()
    .find("select")
    .parent()
    .parent()
    .remove();
  $(form)
    .find("#add_subject_group")
    .parent()
    .find("select")
    .parent()
    .parent()
    .remove();
}
function delete_select_button_on_click(element) {
  if (
    $(element.target.parentElement.parentElement.parentElement).find(
      "#add_subject_cipher_and_direction"
    ).length === 1
  ) {
    $(element.target.parentElement.parentElement.parentElement.parentElement)
      .find("#add_subject_group")
      .parent()
      .find("select")
      .parent()
      .parent()
      .remove();
  }

  $(element.target.parentElement.parentElement).remove();
  addEventListenersToDynamicElements();
}
function delete_subject_button_on_click(element) {
  $(element.target.parentElement.parentElement.parentElement).remove();
}
function save_employee_form_button_on_click(element) {
  const form = $(element).parent().parent();

  const data = {
    name: form.find("#full_name").val(),
    birth_date: form.find("#birth_date").val(),
    phone_number: form.find("#phone_number").val(),
    degree: form.find("#degree").val(),
    academic_title: form.find("#academic_title").val(),
    position: form.find("#position").val(),

    rate: form.find("#rate").val(),
  };

  if ((data.birth_date === "") | (data.birth_date == null)) {
    data.birth_date = null;
  }
  for (let item of [data.position, data.rate, data.name]) {
    if ((item === "") | (item == null)) {
      return;
    }
  }
  rate = parseFloat(data.rate);
  if (rate <= 0 || rate > 1) {
    alert("Ставка должна быть в пределах (0,1]");
    return;
  }
  data.rate = rate;
  data["subjects"] = [];
  try {
    for (let item of form.find("#subject_forms").find(".subject_form")) {
      item = $(item);
      const name = item.find("#id_subject_name").val();
      const study_level = item.find("#id_subject_study_level").val();

      for (let subject_main_part of item.find(".subject_main_part")) {
        subject_main_part = $(subject_main_part);

        const holding_type = subject_main_part.find("#id_holding_type").val();
        for (let group_sem of subject_main_part.find(".subject_group_select")) {
          group_sem = $(group_sem);
          const semester = group_sem
            .val()
            .split(" | ")[1]
            .replace(" Семестр", "");
          const group = group_sem.val().split(" | ")[0];
          if (
            (semester == null) |
            (semester == "") |
            (group == null) |
            (group == "")
          ) {
            return;
          }
          data["subjects"].push({
            name: name,
            study_level: study_level,
            holding_type: holding_type,
            groups: group,
            semester: semester,
          });
        }
      }
    }
  } catch (error) {
    alert(error);
    return;
  }

  $.ajax({
    type: "POST",
    headers: { "X-CSRFToken": form.parent().attr("csrf") },
    async: false,
    data: JSON.stringify(data),
    url: "persons/save_person",
    success: function (response) {},
    error: function (response) {},
  });
  const modal = form.parent().parent().parent();
  modal.trigger("click.dismiss.bs.modal");
  location.reload(true);
}
function close_employee_form_button_on_click(element) {
  $(element.target.parentElement.parentElement.parentElement).remove();
}
function add_subjects_to_filled_form(main_form, subjects) {
  function create_base_form(form) {
    let clone = $("#base_subject_form").clone();
    clone.removeClass("d-none");
    clone.addClass("subject_form");
    clone.attr("id", "subject_form");
    clone.find(".subject_main_part")[0].remove();
    form.find("#subject_forms").append(clone);
    addEventListenersToDynamicElements();
    return clone;
  }
  function fill_study_level(form, select, value, name) {
    $(form).find(".subject_main_part").remove();
    const level_select = $(form).find("#id_subject_study_level");
    level_select.empty();
    level_select.append($(`<option disabled selected></option>`));
    $.ajax({
      async: false,
      data: { name: name },
      url: "subjects/get_subject_study_level_by_name",
      success: function (response) {
        const responseData = response.data;
        level_select.prop("disabled", false);
        for (let item of responseData) {
          level_select.append($(`<option value="${item}">${item} </option>`));
        }
      },
      error: function (response) {
        console.log(response.responseJSON.errors);
      },
    });

    select.val(value);
  }
  function add_holding_type(form, name, study_level, type) {
    const subjectMainPart = $("#base_subject_form")
      .find(".subject_main_part")
      .clone()[0];
    const type_select = $(subjectMainPart).find("#id_holding_type");
    $.ajax({
      async: false,
      data: { name: name, study_level: study_level },
      url: "subjects/get_subject_holding_type_by_study_level_name",
      success: function (response) {
        const responseData = response.data;
        type_select.prop("disabled", false);
        for (let item of responseData[0]) {
          type_select.append($(`<option value="${item}">${item} </option>`));
        }
      },
      error: function (response) {
        console.log(response.responseJSON.errors);
      },
    });
    form.append(subjectMainPart);
    addEventListenersToDynamicElements();
    type_select.val(type);
    return subjectMainPart;
  }
  function fill_ciphers_and_directions(
    form,
    name,
    study_level,
    type,
    cipher_and_direction
  ) {
    const select = $(`
    <div class="row mt-3 align-items-center">
    <div class="col-md-auto">
    <select 
    id="subject_cipher_and_direction_select" 
    name="subject_cipher_and_direction"
    class=" subject_cipher_and_direction_select form-select form-select">   
    <option disabled selected> 
    </option>
    </select>
      </div>
    <div class="col-md-auto">
      <button type="button" class="btn btn-danger delete_select">-</button>
  
    </div>
    
  `)[0];

    $.ajax({
      async: false,
      data: {
        name: name,
        study_level: study_level,
        holding_type: type,
      },
      url: "subjects/get_subject_ciphers_and_directions_by_name_level_holding",

      success: function (response) {
        const responseData = response.data;

        for (let item of responseData[0]) {
          $($(select).find("select")[0]).append(
            $(`<option value="${item}">${item} </option>`)
          );
        }
      },
      error: function (response) {
        console.log(response.responseJSON.errors);
      },
    });
    form.append(select);
    $($(select).find("select")[0]).val(cipher_and_direction);
    addEventListenersToDynamicElements();
  }
  function fill_groups(
    form,
    name,
    study_level,
    type,
    ciphers_and_directions,
    group
  ) {
    const select = $(`
  <div class="row mt-3 align-items-center">
  <div class="col-md-auto">
  <select 
  id="subject_group_select" 
  name="subject_group" 
  class="subject_group_select form-select form-select">   

  <option disabled selected> 

  </option>

  </select>
  </div>
  <div class="col-md-auto">
    <button type="button" class="btn btn-danger delete_select">-</button>

  </div>
  `)[0];

    for (let select of form
      .parent()
      .parent()
      .find("#add_subject_cipher_and_direction")
      .parent()
      .find("select")) {
      ciphers_and_directions.push($(select).val());
    }
    $.ajax({
      async: false,
      data: {
        name: name,
        study_level: study_level,
        holding_type: type,
        ciphers_and_directions: ciphers_and_directions,
      },
      url: "subjects/get_subject_groups_by_name_level_holding_cipher_direction",
      success: function (response) {
        const responseData = response.data;

        for (let item of responseData) {
          $($(select).find("select")).append(
            $(`<option value="${item}">${item} </option>`)
          );
        }
      },
      error: function (response) {
        console.log(response.responseJSON.errors);
      },
    });
    form.append(select);
    $($(select).find("select")).val(group);
    addEventListenersToDynamicElements();
  }
  Object.entries(subjects).forEach(([key, value]) => {
    const form = create_base_form(main_form);
    form.find("#id_subject_name").val(key.split(" | ")[0]);
    const study_level = key.split(" | ")[1];
    const name = key.split(" | ")[0];
    fill_study_level(
      form,
      form.find("#id_subject_study_level"),
      study_level,
      name
    );
    Object.entries(value).forEach(([holding_type, data]) => {
      const main_part = add_holding_type(form, name, study_level, holding_type);

      for (let cipher_and_direction of data["cipher_and_direction"]) {
        fill_ciphers_and_directions(
          $(main_part).find(".subject_ciphers_and_directions_container")[0],
          name,
          study_level,
          holding_type,
          cipher_and_direction
        );
      }
      for (let group of data["groups"]) {
        fill_groups(
          $(main_part).find("#add_subject_group").parent(),
          name,
          study_level,
          holding_type,
          data["cipher_and_direction"],
          group
        );
      }
    });
  });
}
function fill_employee_form() {
  const form = $("#edit_employee_content");

  $.ajax({
    async: false,
    data: { id: parseInt(form.parent().parent().attr("person_id")) },
    url: "employees/get_employee",
    success: function (response) {
      const responseData = response.data;
      form.find("#full_name").val(responseData["full_name"]);
      form.find("#birth_date").val(responseData["birth_date"]);
      form.find("#phone_number").val(responseData["phone_number"]);
      form.find("#degree").val(responseData["degree"]);
      form.find("#academic_title").val(responseData["academic_title"]);
      form.find("#rate").val(responseData["rate"]);
      form.find("#position").val(responseData["position"]);
      add_subjects_to_filled_form(form, responseData["subjects"]);
    },
    error: function (response) {
      console.log(response.responseJSON.errors);
    },
  });
}
function save_edit_employee_form_button_on_click(element) {
  const form = $(element).parent().parent();
  const data = {
    id: parseInt(form.parent().parent().parent().attr("person_id")),
    name: form.find("#full_name").val(),
    birth_date: form.find("#birth_date").val(),
    phone_number: form.find("#phone_number").val(),
    degree: form.find("#degree").val(),
    academic_title: form.find("#academic_title").val(),
    position: form.find("#position").val(),

    rate: form.find("#rate").val(),
  };

  for (let item of [data.position, data.rate, data.name, data.id]) {
    if ((item === "") | (item == null)) {
      return;
    }
  }
  rate = parseFloat(data.rate);
  if (rate <= 0 || rate > 1) {
    alert("Ставка должна быть в пределах (0,1]");
    return;
  }
  data.rate = rate;
  data["subjects"] = [];
  try {
    for (let item of form.find("#subject_forms").find(".subject_form")) {
      item = $(item);
      const name = item.find("#id_subject_name").val();
      const study_level = item.find("#id_subject_study_level").val();

      for (let subject_main_part of item.find(".subject_main_part")) {
        subject_main_part = $(subject_main_part);
        const holding_type = subject_main_part.find("#id_holding_type").val();
        for (let group_sem of subject_main_part.find(".subject_group_select")) {
          group_sem = $(group_sem);
          const semester = group_sem
            .val()
            .split(" | ")[1]
            .replace(" Семестр", "");
          const group = group_sem.val().split(" | ")[0];
          if (
            (semester == null) |
            (semester == "") |
            (group == null) |
            (group == "")
          ) {
            return;
          }
          data["subjects"].push({
            name: name,
            study_level: study_level,
            holding_type: holding_type,
            groups: group,
            semester: semester,
          });
        }
      }
    }
  } catch (error) {
    alert(error);
    return;
  }
  console.log(data);
  $.ajax({
    type: "POST",
    headers: { "X-CSRFToken": form.parent().attr("csrf") },
    async: false,
    data: JSON.stringify(data),
    url: "persons/edit_person",
    success: function (response) {},
    error: function (response) {},
  });
  const modal = form.parent().parent().parent();
  modal.trigger("click.dismiss.bs.modal");
  location.reload(true);
}
function addEventListenersToDynamicElements() {
  const add_subject_holding_type_buttons = $(".add_subject_holding_type");
  for (let button of add_subject_holding_type_buttons) {
    button.removeEventListener(
      "click",
      add_subject_holding_type_button_on_click,
      true
    );
    button.addEventListener("click", add_subject_holding_type_button_on_click);
  }

  const add_subject_cipher_and_direction_buttons = $(
    ".add_subject_cipher_and_direction"
  );
  for (let button of add_subject_cipher_and_direction_buttons) {
    button.removeEventListener(
      "click",
      add_subject_cipher_and_direction_button_on_click,
      true
    );
    button.addEventListener(
      "click",
      add_subject_cipher_and_direction_button_on_click
    );
  }

  const add_subject_group_buttons = $(".add_subject_group");
  for (let button of add_subject_group_buttons) {
    button.removeEventListener(
      "click",
      add_subject_group_button_on_click,
      true
    );
    button.addEventListener("click", add_subject_group_button_on_click);
  }

  const subject_name_selects = $(".subject_name_select");
  for (let select of subject_name_selects) {
    select.removeEventListener("change", subject_name_on_select, true);
    select.addEventListener("change", subject_name_on_select);
  }

  const holding_type_selects = $(".holding_type_select");
  for (let select of holding_type_selects) {
    select.removeEventListener("change", holding_type_on_select, true);
    select.addEventListener("change", holding_type_on_select);
  }
  const delete_select_buttons = $(".delete_select");
  for (let button of delete_select_buttons) {
    button.removeEventListener("click", delete_select_button_on_click, true);
    button.addEventListener("click", delete_select_button_on_click);
  }
  const delete_subject_buttons = $(".delete_subject");
  for (let button of delete_subject_buttons) {
    button.removeEventListener("click", delete_subject_button_on_click, true);
    button.addEventListener("click", delete_subject_button_on_click);
  }
  const save_employee_form_buttons = $(".save_employee_form");
  for (let button of save_employee_form_buttons) {
    button.removeEventListener(
      "click",
      save_employee_form_button_on_click,
      true
    );
    button.addEventListener("click", save_employee_form_button_on_click);
  }
  const close_employee_form_buttons = $(".close_employee_form");
  for (let button of close_employee_form_buttons) {
    button.removeEventListener(
      "click",
      close_employee_form_button_on_click,
      true
    );
    button.addEventListener("click", close_employee_form_button_on_click);
  }

  const save_edit_employee_form_buttons = $(".save_edit_employee_form");
  for (let button of save_edit_employee_form_buttons) {
    button.removeEventListener(
      "click",
      save_edit_employee_form_button_on_click,
      true
    );
    button.addEventListener("click", save_edit_employee_form_button_on_click);
  }
}
$(document).ready(function () {
  if ($("#edit_employee_content").length) fill_employee_form();
});
function phoneMask(elem) {
  var num = $(elem).val().replace(/\D/g, "");
  $(elem).val(
    "+" +
      num.substring(0, 1).replace("8", "7") +
      "(" +
      num.substring(1, 4) +
      ")" +
      num.substring(4, 7) +
      "-" +
      num.substring(7, 11)
  );
}
