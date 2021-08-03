function addEventPath() {
    // Get the collection
    var inputs = document.getElementsByTagName('input');
    console.log(inputs.length)
    // Adds the event listener to all the inputs
    for (let inp of inputs) {
        inp.addEventListener('change', function () {
            // Get the previous label
            if (inp.files && inp.files.length > 1) {
                var label = inp.previousElementSibling;
                console.log(label)
                label.innerHTML = inp.value;
            }
        })
    }
}

addEventPath()