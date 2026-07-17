function celebrate(){

for(let i=0;i<200;i++){

let c=document.createElement("div");

c.className="confetti";

c.style.left=Math.random()*100+"vw";

c.style.animationDelay=Math.random()+"s";

document.body.appendChild(c);

}

}