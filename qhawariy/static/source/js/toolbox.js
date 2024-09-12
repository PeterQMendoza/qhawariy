document.addEventListener('DOMContentLoaded',()=>{
    // Activacion de tab
    const element=document.querySelectorAll('.tab-presupuesto-item');
    const tab=document.querySelector('.tab-presupuesto');
    const panel=document.querySelectorAll('.panel');
    const aux=[]
    
    element.forEach(e=>{
        aux.push(e.innerText);
    });

    element.forEach(ele=>{
        tab.addEventListener('click',(e)=>{
            let index=aux.lastIndexOf(ele.innerText);
            if(ele.contains(e.target))
            {
                if(!ele.classList.contains('active-tab'))
                {
                    
                    ele.classList.add('active-tab');
                    panel[index].style.display="";
                }
            }
            else
            {
                if(ele.classList.contains('active-tab'))
                {
                    ele.classList.remove('active-tab');
                    panel[index].style.display="none";
                }
            }
        });
    });

    // DIBUJO EN CANVAS
    // CHART PIE
    //
    Chart.defaults.font.size = 10;
    Chart.defaults.font.family='Montserrat';

    const can=document.getElementById("myChart");
    const g=document.querySelectorAll('.gastos');
    const t=document.querySelectorAll('.names');
    const c=document.querySelectorAll('.colors');
    const gastos=[]
    const titles=[]
    const colors=[]

    
    g.forEach(el=>{gastos.push(parseFloat(el.innerHTML))});
    t.forEach(el=>{titles.push(el.innerHTML)});
    c.forEach(el=>{colors.push(el.innerHTML)});

    //Setup
    const dataset=[];
    for (let i = 0; i < gastos.length; i++) {
        dataset.push({
            label: titles[i]
        });
    }
    const data={
        labels:titles,
        datasets: [{
            label:'',
            data:gastos,
            backgroundColor:colors,
            hoverOffset: 4,
            cutout:'80%',
            spacing:10
        }]
    };

    // footer and label
    const INGRESO_TOTAL=parseFloat(document.querySelector('.ingTotal').innerHTML);
    const ahorro='Ahorro';
    const ah=parseFloat(document.querySelector('.ahoTotal').innerHTML);
    const footer = (tooltipItems) => {
        let percent=0;
        let strAh='';
        let sum=0;
        let it=false;
        let value=0;
        tooltipItems.forEach(function(item) {
            item.dataset.data.forEach(ele=>{
                sum=sum+ele;
            });
            value=item.parsed;
            if(item.label===ahorro)
            {
                it=true;
            }
        });
        percent=(it)?((ah*100)/INGRESO_TOTAL):((value*100)/(sum-ah));
        strAh=(it)?(' -> Ingresos'):(' -> Gastos')
        return Math.round(percent)+' %'+strAh;
    };

    const label = (tooltipItems) => {
        let label=tooltipItems.dataset.label||'';
    
        if(label)
        {
            label += ':';
        }

        if (tooltipItems.parsed !== null) {
            label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'PEN' }).format(tooltipItems.parsed);
        }
        return label;
    };
    // Config
    const config={
        type:'doughnut',
        data:data,
        options: {
            responsive: true,
            plugins: {
                legend:{
                    display:false,
                },
                tooltip: {
                    callbacks: {
                        label: label,
                        footer:footer,
                    },
                    position:'average',
                }
            }
        }
        
    };

    const chart=new Chart(can,config);

    // CHART BAR
    
    const chart_bar=document.getElementById("myChartBar");

    const data_by = [
        { month: 1, count: 10, count2: 21, count3: 2},
        { month: 2, count: 20, count2: 31, count3: 3},
        { month: 3, count: 15, count2: 41, count3: 4},
        { month: 4, count: 25, count2: 52, count3: 5},
        { month: 5, count: 22, count2: 62, count3: 6},
        { month: 6, count: 30, count2: 72, count3: 7},
        { month: 7, count: 28, count2: 82, count3: 8},
        { month: 8, count: 10, count2: 21, count3: 2},
        { month: 9, count: 20, count2: 31, count3: 3},
        { month: 10, count: 15, count2: 41, count3: 4},
        { month: 11, count: 25, count2: 52, count3: 5},
        { month: 12, count: 22, count2: 62, count3: 6},
        { month: 13, count: 30, count2: 72, count3: 7},
        { month: 14, count: 28, count2: 82, count3: 8},
      ];

    const labels_b=data_by.map(row => row.year);
    const data_b={
        labels:labels_b,
        datasets:[
        {
            label:"Ingresos",
            data:data_by.map(row=>row.count),
        },
        {
            label:'Gastos',
            data:data_by.map(row=>row.count2),
        },
        {
            label:'Ahorro',
            data:data_by.map(row=>row.count3),
        }]
    };

    //config
    const config_b={
        type:'bar',
        data:data_b,
        options:{
            plugins:{
                title:{
                    display:true,
                    text: 'Comparacion mensual'
                },
            },
            responsive:true,
            scales:{
                x:{
                    stacked:true,
                },
                y:{
                    stacked:true,
                }
            }
        }
    };

    const cb=new Chart(chart_bar,config_b);
    
    // MODAL PARA AVISOS
    class Modal
    {
        constructor(e_view,btn_active,btn_close=null,t_modal,text_modal,form)
        {
            this.e_view=document.querySelector(e_view);
            this.btn_active=document.querySelector(btn_active);
            let aux=(btn_close!=null)?(document.querySelector(btn_close)):null;
            this.btn_close=aux;
            this.t_modal=t_modal;
            this.text_modal=document.querySelector(text_modal);
            this.form=document.querySelector(form);
            this.is_hidden=false;

        }

        // methods
        hide()
        {
            this.e_view.classList.add('hidden');
            this.form.classList.add('hidden');
            this.hidden=true;
        }

        show()
        {
            this.e_view.classList.remove('hidden');
            this.text_modal.innerHTML="Nuevo "+this.t_modal;
            this.form.classList.remove('hidden');
            this.hidden=false;
        }
    }

    mi=[
        new Modal(".h-modal",".btn-income",".btn-close-modal","ingreso",".title-modal",".form_income"),
        new Modal(".h-modal",".btn-spending",".btn-close-modal","gasto",".title-modal",".form_spending"),
        new Modal(".h-modal",".btn-saving",".btn-close-modal","ahorro",".title-modal",".form_saving")
    ]

    function activeModal(element)
    {
        let b_a=element.btn_active;
        let b_c=element.btn_close;

        window.addEventListener('click',(e)=>{
            if (b_a!=null)
            {
                if(b_a.contains(e.target))
                {
                    element.show();
                }
                if(b_c.contains(e.target))
                {
                    element.hide();
                }
            }
        });
    }

    mi.forEach(el=>activeModal(el));

    // Generar colores aleatorios y asignarlos a las barra de fecha
    function gen_colors()
    {
        // Lista de colores
        const colores_list=[
            '#6C194F','#3F2463','#431031','#162053','#1F3890','#005bc5','#7d677e','#e32d40','#09738a',
            '#005A31','#265B52','#361542','#004443','#6a0e47','#0e0b29','#5c4152','#13444d','#5d2d4e',
            '#c02948','#408156','#909320','#4c5e91','#f7345b','#b50d57','#7f6000','#b56a65','#d1024e',
            '#f5634a'
        ]

        let position=()=>{return Math.floor(Math.random()*colores_list.length)};

        return colores_list[position()];
    }
    const balls=document.querySelectorAll('.ball');
    const bars=document.querySelectorAll('.bar');
    const cards=document.querySelectorAll('.card');
    const rects=document.querySelectorAll('.rectangulo');
    let count=balls.length
    if(count===bars.length)
    {
        for(let i=0;i<bars.length;i++)
        {
            let co=gen_colors();
            balls[i].style.backgroundColor=co;
            bars[i].style.backgroundColor=co;
            cards[i].style.backgroundColor=co;
            rects[i].style.setProperty('--colrs',co);
            // cssVars({variable:'--colors',co});
        }
    }
    
});