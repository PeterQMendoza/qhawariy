document.addEventListener('DOMContentLoaded',()=>{
    const grid=document.querySelector('.grid');
    const gl=document.getElementById('generations');
    const width=37;
    const size=10;
    const directions=[+1,-1,+width,-width,+width-1,-width-1,width+1,-width+1];
    const cells=[];
    const newCells=[];
    const btnPause=document.querySelector('.button-pause');
    const textPause=document.querySelector('.text-pause');
    const iconMedia=document.querySelector('.icon-media');

    // Size of the grid in px
    // grid.style.width=size*width+'px';
    // grid.style.height=size*width+'px';

    //CREATE CELLS
    // State of cells
    // 0-> dead cell
    // 1-> live cell

    class cell
    {
        constructor(startIndex){
            this.state=0;
            this.startIndex=startIndex;
            this.currentIndex=startIndex;
        }

        // Setter
        set dead(x){
            if(x===0)this.state=x;
        }

        set alive(x){
            if(x===1)this.state=x;
        }

        // Method
        isAlive(){
            return (this.state===1)?true:false
        }
        getCoord(){
            return [Math.floor(this.currentIndex/width),this.currentIndex%width];
        }
    }
    
    function fillCells(a){
        for (let i = 0; i < width*width; i++) {
            a.push(new cell(i));
        }
    }
    fillCells(cells);
    fillCells(newCells);
    
    // Count Neighbor per cell
    const neighbor=(c)=>{
        let total=0;
        for (let i = 0; i < directions.length; i++) {
            let aux=0;
            aux=c+directions[i];
            if(aux>=0 && aux<width*width){
                if(c%width===0){
                    if(directions[i]!=-1 &&
                        directions[i]!=width-1 &&
                        directions[i]!=-width-1){
                            if(cells[aux].isAlive()){
                                total++;
                            }
                    }
                }
                else if(c%width===(width-1)){
                    if(directions[i]!=+1 &&
                        directions[i]!=width+1 &&
                        directions[i]!=-width+1){
                            if(cells[aux].isAlive()){
                                total++;
                            }
                        }
                }
                else if(cells[aux].isAlive()){
                    total++;
                }
            }
        }
        return total;
    }
    
    // // PATRON   sapo
    // const a=Math.floor((2*width/3)+(width/2)*width);
    // cells[a+1-width].alive=1;
    // cells[a+2-width].alive=1;
    // cells[a+3-width].alive=1;
    // cells[a].alive=1;
    // cells[a+1].alive=1;
    // cells[a+2].alive=1;

    // GALAXIA DE KOK
    const k=Math.floor((width/2)*width);
    // esquina superior derecha
    cells[k-18*width+8].alive=1;
    cells[k-17*width+8].alive=1;
    cells[k-17*width+10].alive=1;
    cells[k-16*width+8].alive=1;
    cells[k-16*width+9].alive=1;

    cells[k-13*width+8].alive=1;
    cells[k-13*width+10].alive=1;
    cells[k-12*width+8].alive=1;
    cells[k-12*width+9].alive=1;
    cells[k-11*width+9].alive=1;
    
    cells[k-11*width+16].alive=1;
    cells[k-10*width+14].alive=1;
    cells[k-10*width+15].alive=1;
    cells[k-9*width+15].alive=1;
    cells[k-9*width+16].alive=1;
    
    // esquina superior izquierda
    cells[k-16*width-9].alive=1;
    cells[k-16*width-11].alive=1;
    cells[k-15*width-9].alive=1;
    cells[k-15*width-10].alive=1;
    cells[k-14*width-10].alive=1;
    
    cells[k-10*width-17].alive=1;
    cells[k-9*width-16].alive=1;
    cells[k-8*width-16].alive=1;
    cells[k-8*width-17].alive=1;
    cells[k-8*width-18].alive=1;
    
    cells[k-10*width-13].alive=1;
    cells[k-9*width-12].alive=1;
    cells[k-9*width-11].alive=1;
    cells[k-8*width-13].alive=1;
    cells[k-8*width-12].alive=1;

    // Esquina inferior derecha
    cells[k+8*width+18].alive=1;
    cells[k+8*width+17].alive=1;
    cells[k+8*width+16].alive=1;
    cells[k+9*width+16].alive=1;
    cells[k+10*width+17].alive=1;
    
    cells[k+8*width+13].alive=1;
    cells[k+8*width+12].alive=1;
    cells[k+9*width+12].alive=1;
    cells[k+9*width+11].alive=1;
    cells[k+10*width+13].alive=1;
    
    cells[k+14*width+10].alive=1;
    cells[k+15*width+10].alive=1;
    cells[k+15*width+9].alive=1;
    cells[k+16*width+9].alive=1;
    cells[k+16*width+11].alive=1;
    
    // Esquina inferior izquierda
    cells[k+18*width-8].alive=1;
    cells[k+17*width-8].alive=1;
    cells[k+17*width-10].alive=1;
    cells[k+16*width-8].alive=1;
    cells[k+16*width-9].alive=1;
    
    cells[k+13*width-8].alive=1;
    cells[k+13*width-10].alive=1;
    cells[k+12*width-9].alive=1;
    cells[k+12*width-8].alive=1;
    cells[k+11*width-9].alive=1;
    
    cells[k+11*width-16].alive=1;
    cells[k+10*width-14].alive=1;
    cells[k+10*width-15].alive=1;
    cells[k+9*width-15].alive=1;
    cells[k+9*width-16].alive=1;

    // PATRON PULSAR
    // const p=Math.floor((1*width/3)+(width/2)*width);
    // cells[p].alive=1;
    // cells[p+1].alive=1;
    // cells[p+2].alive=1;

    // cells[p+2*width-2].alive=1;
    // cells[p+3*width-2].alive=1;
    // cells[p+4*width-2].alive=1;

    // cells[p+2*width+3].alive=1;
    // cells[p+3*width+3].alive=1;
    // cells[p+4*width+3].alive=1;

    // cells[p+5*width].alive=1;
    // cells[p+1+5*width].alive=1;
    // cells[p+2+5*width].alive=1;

    // // 2
    // cells[p+7*width].alive=1;
    // cells[p+1+7*width].alive=1;
    // cells[p+2+7*width].alive=1;

    // cells[p+8*width-2].alive=1;
    // cells[p+9*width-2].alive=1;
    // cells[p+10*width-2].alive=1;

    // cells[p+8*width+3].alive=1;
    // cells[p+9*width+3].alive=1;
    // cells[p+10*width+3].alive=1;

    // cells[p+12*width].alive=1;
    // cells[p+1+12*width].alive=1;
    // cells[p+2+12*width].alive=1;

    // // 3
    // cells[p+6].alive=1;
    // cells[p+7].alive=1;
    // cells[p+8].alive=1;

    // cells[p+2*width+5].alive=1;
    // cells[p+3*width+5].alive=1;
    // cells[p+4*width+5].alive=1;

    // cells[p+2*width+10].alive=1;
    // cells[p+3*width+10].alive=1;
    // cells[p+4*width+10].alive=1;

    // cells[p+5*width+6].alive=1;
    // cells[p+5*width+7].alive=1;
    // cells[p+5*width+8].alive=1;

    // // 4
    // cells[p+7*width+6].alive=1;
    // cells[p+7*width+7].alive=1;
    // cells[p+7*width+8].alive=1;

    // cells[p+8*width+5].alive=1;
    // cells[p+9*width+5].alive=1;
    // cells[p+10*width+5].alive=1;

    // cells[p+8*width+10].alive=1;
    // cells[p+9*width+10].alive=1;
    // cells[p+10*width+10].alive=1;

    // cells[p+12*width+6].alive=1;
    // cells[p+12*width+7].alive=1;
    // cells[p+12*width+8].alive=1;

    // // PISTOLA DE GOSPER
    // //WIDTH =64 A MAS
    // const b=Math.floor((width/2)+(width/2)*width/4)
    // // square1
    // cells[b-16].alive=1;
    // cells[b-16+width].alive=1;
    // cells[b-17].alive=1;
    // cells[b-17+width].alive=1;
    // // C
    // cells[b-5-2*width].alive=1;
    // cells[b-4-2*width].alive=1;
    // cells[b-6-width].alive=1;
    // cells[b-7].alive=1;
    // cells[b-7+width].alive=1;
    // cells[b-7+2*width].alive=1;
    // cells[b-6+3*width].alive=1;
    // cells[b-5+4*width].alive=1;
    // cells[b-4+4*width].alive=1;
    // //->
    // cells[b-2-width].alive=1;
    // cells[b-3+width].alive=1;
    // cells[b-1].alive=1;
    // cells[b-1+width].alive=1;
    // cells[b+width].alive=1;
    // cells[b-1+2*width].alive=1;
    // cells[b-2+3*width].alive=1;
    // //rectangle
    // cells[b+7-4*width].alive=1;
    // cells[b+7-3*width].alive=1;
    // cells[b+5-3*width].alive=1;
    // cells[b+3-2*width].alive=1;
    // cells[b+4-2*width].alive=1;
    // cells[b+3-width].alive=1;
    // cells[b+4-width].alive=1;
    // cells[b+3].alive=1;
    // cells[b+4].alive=1;
    // cells[b+5+width].alive=1;
    // cells[b+7+width].alive=1;
    // cells[b+7+2*width].alive=1;
    // //square2
    // cells[b+17-2*width].alive=1;
    // cells[b+18-2*width].alive=1;
    // cells[b+17-width].alive=1;
    // cells[b+18-width].alive=1;

    // RULES OF THE GAME
    // Then cell is alive
    function giveRulesLive(cell){
        let ne=neighbor(cell);
        // If a cell has two and three neighbors
        // then this cell continue will alive
        if(ne===2 || ne===3){
            newCells[cell].alive=1;
        }
        // If cell has more than three neighbor
        // then this cell will dead
        if(ne>3){
            newCells[cell].dead=0;
        }
        // If cell has less than two neighbor
        // than this cell dead
        if(ne<2){
            newCells[cell].dead=0;
        }
    }

    // Then cell is dead or cell will not born yet
    function giveRulesDead(cell){
        // If a empty cell and exists three neigbors
        // then it will born a new cell
        let ne=neighbor(cell)
        if(ne===3){
            newCells[cell].alive=1;
        }
    }

    function start() {
        for (let i = 0; i < cells.length; i++) {      
            
            if(cells[i].isAlive()){
                giveRulesLive(i);
            }
            else{
                giveRulesDead(i);
            }
        }

        cells.forEach(n => {
            n.dead=0;
        });

        for (let i = 0; i < cells.length; i++) {
            cells[i].state=newCells[i].state;
        }
    }

    
    // CREATE WHITEBOARD
    const squares=[];
    let countGen=0;
    function createWhiteboard(){
        if(squares.length===0){
            for(let i=0;i<cells.length;i++){
                const square=document.createElement('div');
                grid.appendChild(square);
                squares.push(square);
                if(cells[i].isAlive()){
                    squares[i].classList.add('live-cell');
                    squares[i].style.width=size+'px';
                    squares[i].style.height=size+'px';
                }
                else{
                    squares[i].classList.add('dead-cell');
                    squares[i].style.width=size+'px';
                    squares[i].style.height=size+'px';
                }
            }
        }
        else {
            for(let i=0;i<cells.length;i++){
                if(cells[i].isAlive()){
                    squares[i].classList.remove('live-cell','dead-cell');
                    // squares[i].style.width=size+'px';
                    // squares[i].style.height=size+'px';
                    squares[i].classList.add('live-cell');
                }
                else{
                    squares[i].classList.remove('live-cell','dead-cell');
                    // squares[i].style.width=size+'px';
                    // squares[i].style.height=size+'px';
                    squares[i].classList.add('dead-cell');
                }
            }
        }
        
        start();

        countGen++;
        gl.innerHTML=countGen; 

        newCells.forEach(n => {
            n.dead=0;
        });
    }

    // play    
    let currentTimeout;
    let isPlayed=false;
    function play() {
        textPause.innerHTML='Continuar';
        iconMedia.classList.remove('play');
        iconMedia.classList.add('pause')
        clearInterval(currentTimeout);
        currentTimeout=setInterval(createWhiteboard,200);
        isPlayed=true;
    }
    function pause() {
        textPause.innerHTML='Pausado';
        iconMedia.classList.remove('pause');
        iconMedia.classList.add('play')
        clearInterval(currentTimeout);
        isPlayed=false;
    }

    btnPause.addEventListener('click',(e)=>{
        if(btnPause.contains(e.target)){
            if(!isPlayed){
                play();
            }
            else{
                pause();
            }
        }
    });
    play();
    
});