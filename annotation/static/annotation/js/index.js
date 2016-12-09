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
    var sessionDiv = document.getElementById("sessionDiv");
    if (sessionDiv){
        var raw = sessionDiv.getAttribute("value").split('@');
        var numOfDoc = raw[1];
        // update input tag
        document.getElementById("sessionStart").setAttribute(
            "value", raw[0] +'@'+ (parseInt(numOfDoc)+1).toString());
        var prefix = "";
        if (numOfDoc == 1){
            prefix = numOfDoc.toString() +' Document / ';
        } else {
            prefix = numOfDoc.toString() +' Documents / ';
        }
        displayClock(prefix);
    } else {
        document.getElementById("sessionStart").setAttribute(
            "value", new Date().toUTCString()+'@1');
    }
};

function checkTime(i) {
    if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
    return i;
}

function displayClock(prefix){
    startDate = new Date(document.getElementById("sessionDiv").getAttribute("value").split('@')[0]);
    var current = new Date();
    var passed = new Date(current - startDate);
    var h = passed.getHours()-1;
    var m = passed.getMinutes();
    var s = passed.getSeconds();
    m = checkTime(m);
    s = checkTime(s);
    document.getElementById("sessionDiv").innerHTML = prefix + h + ":" + m + ":" + s;
    var t = setTimeout(function(){displayClock(prefix);}, 500);
}

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
        var sessionDiv = document.getElementById("sessionDiv");
        if (btnPause.innerHTML == "Pause"){
            labels.map(function(label){
                label.disabled = true;
            });
            document.getElementById("btnSubmit").disabled = true;
            textBuffer = doc.innerHTML;
            doc.innerHTML = "";

            if(sessionDiv){
                sessionDiv.hidden = true;
            }

            btnPause.innerHTML = "Resume";
            pause = new Date();
        } else {
            labels.map(function(label){
                label.disabled = false;
            });
            document.getElementById("btnSubmit").disabled = false;
            doc.innerHTML = textBuffer;
            textBuffer = "";

            // var sessionStart = document.getElementById("sessionStart");
            // var raw = sessionStart.getAttribute("value").split('@');
            // var numOfDoc = raw[1];
            // var oldStartDate = new Date(raw[0]);
            // var diff = pause - oldStartDate;
            // var newStartDate = new Date();
            // newStartDate.setTime(oldStartDate.getTime()+diff)
            // var newValue = newStartDate.toUTCString() + '@' + numOfDoc;
            // sessionStart.setAttribute("value", newValue);
            // document.getElementById("sessionDiv").setAttribute("value", newValue);

            if(sessionDiv){
                sessionDiv.hidden = false;
            }

            btnPause.innerHTML = "Pause";
            totalPause += (new Date() - pause);
        }
    };
}
