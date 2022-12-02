function addEditButtons(el) {
    $(el).append('<div class="fa-solid fa-pen-to-square btn-warning"></div>')
    $(el).append('<div class="fa-solid fa-up-down-left-right btn-warning"></div>')
    $(el).append('<div class="fa-solid fa-trash btn-danger"></div>')

    $(el).find('.fa-pen-to-square').on('click', function() {
    setTimeout(function () {$('#syncStore').click()},100)
    setTimeout(function() {$("#editActive").click()}, 300)})

    $(el).find('.fa-trash').on('click', function() {
        setTimeout($('#syncStore').click(),100)
        setTimeout( function () {
        if (confirm('Are you sure you want to delete, you cannot recover')) {
        $("#deleteTarget").click()}}, 300)
    })
}


function dragElement(elmnt) {

  var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  $(elmnt).on('mousedown', function(e) {
    dragMouseDown(e)
  })

  function dragMouseDown(e) {
    e = e || window.event;
    e.preventDefault();
    // get the mouse cursor position at startup:
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    // call a function whenever the cursor moves:
    document.onmousemove = elementDrag;
  }

  function elementDrag(e) {
    e = e || window.event;
    e.preventDefault();
    // calculate the new cursor position:
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    // set the element's new position:
    $(elmnt).closest('.dash-graph')[0].style.top = ($(elmnt).closest('.dash-graph')[0].offsetTop - pos2) + "px";
    $(elmnt).closest('.dash-graph')[0].style.left = ($(elmnt).closest('.dash-graph')[0].offsetLeft - pos1) + "px";
  }

  function closeDragElement() {
    // stop moving when mouse button is released:
    document.onmouseup = null;
    document.onmousemove = null;
  }
}