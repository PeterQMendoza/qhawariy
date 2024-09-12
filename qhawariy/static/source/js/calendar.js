document.addEventListener('DOMContentLoaded',()=>{
    var actual=new Date();

    // Obtener el elemento HTML
    var calen=document.querySelector(".calendar");
    var title=document.querySelector(".calendar-title");
    var btn_next=document.querySelector(".calendar-btn-next");
    var btn_back=document.querySelector(".calendar-btn-back");

    class Calendar
    {
        constructor(year,month){
            this.year=year;
            this.month=month;
            this.actual=new Date(year,month-1,1);
            this.ultimo=new Date(year,month,0);
            this.primer_dia_semana=(this.actual.getDay()==0)?7:this.actual.getDay();
            this.ultimo_dia_mes=this.ultimo.getDate();
            this.dia=0;
            this.dia_actual=0;
            this.ultima_celda=this.primer_dia_semana+this.ultimo_dia_mes;
            this.next_month=0;
            this.next_year=0;
            this.prev_month=0;
            this.prev_year=0;
            this.resultado='';
            this.dias_semana=['L','M','M','J','V','S','D'];
            this.meses=Array("Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Setiembre","Octubre","Noviembre","Diciembre");

            // agregamos los dias de la semana
            this.dias_semana.forEach(d=>{
                this.resultado+='<div class="h-7 w-7 t:h-6 t:w-6 flex items-center justify-center bg-blue-100"><p class="text-white">'+d+'</p></div>';
            })

            // creamos 42 celdas de 6 columnas y de 7 dias
            for(var i=1;i<=42;i++){
                if(i==this.primer_dia_semana){
                    this.dia=1;
                }
                if (i<this.primer_dia_semana || i>=this.ultima_celda) {
                    // Celda vacia
                    this.resultado+='<div class="h-7 w-7 t:h-6 t:w-6 flex items-center bg-gray-250 justify-center border-cream-100 border-b border-l"><p class="text-black-100"></p></div>';
                }else{
                    // Mostrar el dia
                    if(this.dia==actual.getDate() && month==actual.getMonth()+1 && year==actual.getFullYear()){
                        this.resultado+='<div class="h-7 w-7 t:h-6 t:w-6 flex justify-center items-center bg-gray-128 border-cream-100 border-b border-l"><p class="text-white">'+this.dia+'</p></div>';
                    }else{
                        this.resultado+='<div class="h-7 w-7 t:h-6 t:w-6 flex justify-center items-center bg-gray-250 border-cream-100 border-b border-l"><p class="text-black-100">'+this.dia+'</p></div>';
                    }
                    this.dia++;
                }
                if(i%7==0){
                    if(this.dia>this.ultimo_dia_mes){
                        break;
                    }
                }
            }
        }

        get calcular_siguiente_fecha(){
            this.next_month=this.month+1;
            this.next_year=this.year;

            if(this.month+1>12){
                this.next_month=1;
                this.next_year=this.year+1;
            }
        }

        get calcular_anterior_fecha(){
            this.prev_month=this.month-1;
            this.prev_year=this.year;
            if(this.month-1<1){
                this.prev_month=12;
                this.prev_year=this.year-1;
            }
        }

        get obtener_mes_actual(){
            return this.meses[this.month-1]+' de '+this.year;
        }
    }

    var cal=new Calendar(actual.getFullYear(),actual.getMonth()+1);
    calen.innerHTML=cal.resultado;
    title.innerHTML=cal.obtener_mes_actual;
   
    btn_back.addEventListener('click',()=>{
        cal.calcular_anterior_fecha;
        var cal_prev=new Calendar(cal.prev_year,cal.prev_month)
        calen.innerHTML=cal_prev.resultado;
        title.innerHTML=cal_prev.obtener_mes_actual;
        cal=cal_prev;
    })

    btn_next.addEventListener('click',()=>{
        cal.calcular_siguiente_fecha;
        var cal_next=new Calendar(cal.next_year,cal.next_month)
        calen.innerHTML=cal_next.resultado;
        title.innerHTML=cal_next.obtener_mes_actual;
        cal=cal_next;
    })
});