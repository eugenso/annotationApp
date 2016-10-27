var startTime;
var totalPause = 0;
var pause;

var labels = Array.prototype.slice.call(document.getElementsByName("labels"));
var textBuffer = "";


window.onload = function(){
    var proposals = Array.prototype.slice.call(document.getElementsByName("proposals"));
    if (proposals){
        proposals = proposals.map(function(div){
            return div.innerHTML;
        });
        labels.map(function(label){
            if(proposals.indexOf(label.value)>=0){
                label.checked = true;
            }
        });
    }

    if(labels){
        var trigger = function(l){
            if (l.type == 'radio'){
                if(!l.checked){
                    l.checked = true;
                }
            }else{
                if (l.checked){
                    l.checked = false;
                } else {
                    l.checked = true;
                }
            }
        };
        document.addEventListener("keyup", function(e){
            doc = document.getElementById("document");
            if(e && doc){
                switch(e.keyCode){
                case 48:
                    if(labels.length > 0){trigger(labels[labels.length-1]);}
                    break;
                case 49:
                    if(labels.length > 0){trigger(labels[0]);}
                    break;
                case 50:
                    if(labels.length > 1){trigger(labels[1]);}
                    break;
                case 51:
                    if(labels.length > 2){trigger(labels[2]);}
                    break;
                case 52:
                    if(labels.length > 3){trigger(labels[3]);}
                    break;
                case 53:
                    if(labels.length > 4){trigger(labels[4]);}
                    break;
                case 54:
                    if(labels.length > 5){trigger(labels[5]);}
                    break;
                case 55:
                    if(labels.length > 6){trigger(labels[6]);}
                    break;
                case 56:
                    if(labels.length > 7){trigger(labels[7]);}
                    break;
                case 57:
                    if(labels.length > 8){trigger(labels[8]);}
                    break;
                case 13:
                    if (!labels.reduce(function(r, l){return r || l.checked;},
                                       false)){
                        alert('Please select at least one label.');
                    }else if (doc.innerHTML == "YOU HAVE NO MORE DOCUMENTS LEFT TO ANNOTATE. THANK YOU FOR YOUR PARTICIPATION!"){
                        alert('There are no more documents to annotate.');
                    }else{
                        var form = document.forms[0]
                        if(form.id == "annotation-form"){
                            var duration = new Date() - startTime - totalPause;
                            document.getElementById("duration").value = duration.toString();
                            form.submit();
                        }
                    }
                    break;
                }}}, false);}
    startTime = new Date();
};

function measureUserTime() {
    if (!labels.reduce(function(r, l){return r || l.checked;}, false)){
        alert('Please select at least one label.');
        return false;
    }else{
        var duration = new Date() - startTime - totalPause;
        document.getElementById("duration").value = duration.toString();
    }
}


var btnPause = document.getElementById("btnPause");
if (btnPause !== null) {
    btnPause.onclick = function() {
        var doc = document.getElementById("document");
        if (btnPause.innerHTML == "Pause"){
            labels.map(function(label){
                label.disabled = true;
            });
            document.getElementById("btnSubmit").disabled = true;
            textBuffer = doc.innerHTML;
            doc.innerHTML = "";

            btnPause.innerHTML = "Resume";
            pause = new Date();
        } else {
            labels.map(function(label){
                label.disabled = false;
            });
            document.getElementById("btnSubmit").disabled = false;
            doc.innerHTML = textBuffer;
            textBuffer = "";

            btnPause.innerHTML = "Pause";
            totalPause += (new Date() - pause);
        }
    };
}
