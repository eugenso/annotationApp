// window.onload = function(){
//     var labels = Array.prototype.slice.call(document.getElementsByName("labels"));
//     var proposals = Array.prototype.slice.call(document.getElementsByName("proposals"));
//     proposals = proposals.map(function(div){
//         return div.innerHTML;
//     });
//     labels.map(function(label){
//         if(proposals.indexOf(label.value)>=0){
//             label.checked = true;
//         }
//     });
//     startTime = new Date();
// };

// $('textarea#trainDocument').focus(function() {
//     $(this).val('');
// });


function validateTrainForm(button){
    if(!document.forms["training-form"].elements["trainDocument"].value){
        alert("Please enter a document text.")
        return false;
    }
    if (!labels.reduce(function(r, l){return r || l.checked;}, false) &&
        button.value == "Train"){
        alert('Please select at least one label.');
        return false;
    }
}
