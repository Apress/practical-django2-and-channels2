$(function () {
  $('.btn-number').click(function (e) {
    e.preventDefault();
    fieldName = $(this).attr('data-field');
    type = $(this).attr('data-type');
    var input = $("input[name='" + fieldName + "']");
    var currentVal = parseInt(input.val());
    if (type == 'minus') {
      if (currentVal > input.attr('min')) {
        input
          .val(currentVal - 1)
          .change();
      }
      if (parseInt(input.val()) == input.attr('min')) {
        $(this).attr('disabled', true);
      }
    } else if (type == 'plus') {
      if (currentVal < input.attr('max')) {
        input
          .val(currentVal + 1)
          .change();
      }
      if (parseInt(input.val()) == input.attr('max')) {
        $(this).attr('disabled', true);
      }
    }
  });
});