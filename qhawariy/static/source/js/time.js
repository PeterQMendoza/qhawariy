document.addEventListener('DOMContentLoaded',()=>{

    const text=document.querySelector('.timer_print');
    
    window.onload = displayClock();
    function displayClock(){
        const d = new Date();
        var sync = d.getMilliseconds();
        var syncedTimeout = 1000 - sync;

        const tz=Intl.DateTimeFormat().resolvedOptions().timeZone
        const opciones = { timeZone: tz, timestyle:"short" };
        
        var display = d.toLocaleTimeString("es-PE",opciones);
        text.innerHTML = display;
        
        setTimeout(displayClock, syncedTimeout); 
    }
});