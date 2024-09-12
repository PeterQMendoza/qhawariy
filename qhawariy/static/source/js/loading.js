document.addEventListener('DOMContentLoaded',()=>{
    
    var seqs=document.querySelectorAll('.seq');
    // var chas=document.querySelectorAll('.chas');
    var tree=document.querySelectorAll('.seq-tree');
    // const element = document.getElementById("some-element-you-want-to-animate");
    let start, previousTimeStamp;
    let done = false;

    const shortLine = document.querySelector('.line')

    function step(timeStamp) {
        if (start === undefined) {
            start = timeStamp;
        }
        const elapsed = timeStamp - start;

        if (previousTimeStamp !== timeStamp) {
            // Math.min() is used here to make sure the element stops at exactly 60
            count = Math.min(0.11 * elapsed, 42000);

            pos=350+Math.max(-0.010*elapsed,-600);
            pos1=250+Math.max(-0.012*elapsed,-600);
            pos2=480+Math.max(-0.01*elapsed,-820);
            pos3=500+Math.max(-0.012*elapsed,-800);
            
            // shortLine.style.transform=`x1(${x1}deg)`;
            // shortLine.style.transform=`x1(${y1}deg)`;
            shortLine.setAttribute(`x2`,`${-150+0.046*count}`);
            // shortLine.setAttribute(`y2`,`${count}`);

            seqs[0].style.transform = `rotate(${count}deg)`;
            seqs[1].style.transform = `rotate(${count}deg)`;

            tree[0].style.transform = `translateX(${pos}px)`;
            tree[1].style.transform = `translateX(${pos1}px)`;
            tree[2].style.transform = `translateX(${pos2}px)`;
            tree[3].style.transform = `translateX(${pos3}px)`;
            if (count === 6000) done = true;
        }

        if (elapsed < 62000) {
            // Stop the animation after 2 seconds
            previousTimeStamp = timeStamp;
            if (!done) {
            window.requestAnimationFrame(step);
            }
        }
    }

    window.requestAnimationFrame(step);

});