function establecer_posiciones(pesos) {
    var distancias=[]
    let elemento=document.querySelector(".timeline-racetrack")
    let pes=pesos/* debe existir n-2 elemento los extremos son de posicion fija */
    let longitud=elemento.getBoundingClientRect().width;
    let suma_pesos=0
    let pesos_texto=document.querySelectorAll(".timeline-text");
    /* Calculo de distancias */
    pes.forEach(elemento=>{suma_pesos+=elemento});
    pes.forEach(elemento => {
        distancias.push(Math.round(elemento*(longitud/suma_pesos)))
    });
    
    /* Establecer posiciones para cada item */
    let items=document.querySelectorAll(".timeline-item");
    let pos_inicial=document.body.getBoundingClientRect().left;
    
    if (items.length==distancias.length+1) {
        var aux=pos_inicial+32;
        for (let i = 0; i < items.length; i++) {
            items[i].style.left=aux+"px";
            if(i==distancias.length+1){
                aux=aux+0;
            }else{
                aux=aux+distancias[i]-1.5;
            }
        }
    }

    if (pesos_texto.length==distancias.length) {
        var aux=pos_inicial+19;
        for (let i = 0; i < distancias.length; i++) {
            aux=aux+Math.round(distancias[i]/2);
            pesos_texto[i].style.left=aux+"px";
            pesos_texto[i].innerHTML=pesos[i]+" "+"min.";
            aux=aux+Math.round(distancias[i]/2)-1.8;
        }
    }
    
}