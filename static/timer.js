let time = 300;

function updateTimer(){

let minutes = Math.floor(time/60);

let seconds = time%60;

document.getElementById("timer").innerHTML =
String(minutes).padStart(2,'0')+
":"+
String(seconds).padStart(2,'0');

if(time<=0){

alert("⏰ Time's Up!");

window.location="/restart";

}

time--;

}

setInterval(updateTimer,1000);