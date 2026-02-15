// gantt-chart.js
import { 
    createHtmlContentFragment,
    createHtmlElementFragment
} from "./html-content.js";

import {
    monthDiff,
    dayDiff,
    getDaysInMonth,
    getDayOfWeek,
    createFormattedDateFromStr,
    createFormattedDateFromDate
} from "./utils.js";

export function GanttChart(
    ganttChartElement,
    tasks,
    taskDurations,
    month,
    year,
    link=null,
) {
    const months=[
        "Ene",
        "Feb",
        "Mar",
        "Abr",
        "May",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Oct",
        "Nov",
        "Dic"
    ];

    const contentFragment=createHtmlContentFragment();
    let taskDurationElDragged;

    let monthOptionsHTMLStrArr=[];
    for (let i = 0; i < months.length; i++) {
        monthOptionsHTMLStrArr.push(`<option value="${i}">${months[i]}</option>`)
    }
    
    const years=[];
    for (let i = 2025; i < 2050; i++) {
        years.push(`<option value="${i}">${i}</option>`)
    }

    const fromSelectYear=contentFragment.querySelector("#from-select-year");
    const fromSelectMonth=contentFragment.querySelector("#from-select-month");
    const toSelectYear=contentFragment.querySelector("#to-select-year");
    const toSelectMonth=contentFragment.querySelector("#to-select-month");
    const selectedTask=contentFragment.querySelector("#selected-task");
    const parentSelectedTask=selectedTask.parentElement;
    const popoverContainer=contentFragment.querySelector(".popover-container")
    const buttonSendDeleteTask=contentFragment.querySelector(".delete-task");
    const buttonCancelDeleteTask=contentFragment.querySelector(".delete-cancel");

    fromSelectMonth.innerHTML=`${monthOptionsHTMLStrArr.join("")}`;
    fromSelectYear.innerHTML=`${years.join("")}`;
    toSelectMonth.innerHTML=`${monthOptionsHTMLStrArr.join("")}`;
    toSelectYear.innerHTML=`${years.join("")}`;

    selectedTask.value=0;

    // if(month>=12){
    //     const newMonth=month%12;
    //     fromSelectMonth.value=month-1;
    //     fromSelectYear.value=year;
    //     toSelectMonth.value=newMonth;
    //     toSelectYear.value=year+1;
    // } else{
    //     fromSelectMonth.value=month-1;
    //     fromSelectYear.value=year;
    //     toSelectMonth.value=month;
    //     toSelectYear.value=year;
    // }
    fromSelectMonth.value=month-1;
    fromSelectYear.value=year;
    toSelectMonth.value=month-1;
    toSelectYear.value=year;

    const containerTasks=contentFragment.querySelector("#gantt-grid-container__tasks");
    const containerTimePeriods=contentFragment.querySelector("#gantt-grid-container__time");
    // const addTaskForm=contentFragment.querySelector("#add-task");
    const addTaskDurationForm=document.querySelector("#add-task-duration");
    // const addTaskDurationForm=contentFragment.querySelector("#add-task-duration");
    // const taskSelect=document.querySelector("#select_id_vehiculo");
    // const taskSelect=addTaskDurationForm.querySelector("#select-task");

    function createGrid() {
        const startMonth=new Date(parseInt(fromSelectYear.value),parseInt(fromSelectMonth.value));
        const endMonth=new Date(parseInt(toSelectYear.value),parseInt(toSelectMonth.value));
        const numMonths=monthDiff(startMonth,endMonth)+1;

        containerTasks.innerHTML="";
        containerTimePeriods.innerHTML=" ";

        createTaskRows();
        createMonthsRow(startMonth,numMonths);
        createDaysOfTheWeekRow(startMonth,numMonths);
        createDaysRow(startMonth,numMonths);
        createTaskRowsTimePeriods(startMonth,numMonths);
        addTaskDurations();
    }

    createGrid();

    ganttChartElement.appendChild(contentFragment);

    function createTaskRows() {
        const emptyRow=document.createElement("div");
        emptyRow.className="gantt-task-row task-none";
        // los primero 3 filas son vacias
        for (let i = 0; i < 3; i++) {
            containerTasks.appendChild(emptyRow.cloneNode(true));
        }

        let taskOptionsHTMLStrArr=[];

        tasks.forEach((task) => {
            const taskRowEl=document.createElement("div");
            taskRowEl.id=task.id;
            taskRowEl.className="gantt-task-row";

            const taskRowElInput=document.createElement("p");
            taskRowEl.appendChild(taskRowElInput);
            taskRowElInput.innerHTML=task.name;
            // taskRowElInput.value=task.name;

            //actualizar nombre de tarea
            // taskRowElInput.addEventListener("change",updateTask);

            taskOptionsHTMLStrArr.push(`<option value="${task.id}">${task.name}</option>`);

            // agregar boton de eliminar
            // const taskRowElDelBtn=document.createElement("button");
            // // const imgElement=createHtmlElementFragment();
            // // taskRowElDelBtn.appendChild(imgElement);
            // taskRowElDelBtn.innerHTML="x";
            // taskRowElDelBtn.addEventListener("click",deleteTask);
            // taskRowEl.appendChild(taskRowElDelBtn);

            containerTasks.appendChild(taskRowEl);
        });

        // taskSelect.innerHTML=`${taskOptionsHTMLStrArr.join("")}`;
    }

    function createMonthsRow(startMonth,numMonths) {
        containerTimePeriods.style.gridTemplateColumns=`repeat(${numMonths},1fr)`;

        let month=new Date(startMonth);

        for (let i = 0; i < numMonths; i++) {
            const timePeriodEl=document.createElement("div");
            timePeriodEl.className="gantt-time-period months";
            // para centrear texto verticalmente
            const timePeriodElSpan=document.createElement("span");
            timePeriodElSpan.className="text-body-1 text-blue-100";
            timePeriodElSpan.innerHTML=months[month.getMonth()]+" "+month.getFullYear();
            timePeriodEl.appendChild(timePeriodElSpan);
            containerTimePeriods.appendChild(timePeriodEl);
            month.setMonth(month.getMonth()+1);
        }
    }

    function createDaysRow(startMonth,numMonths) {
        let month=new Date(startMonth);

        for (let i = 0; i < numMonths; i++) {
            const timePeriodEl=document.createElement("div");
            timePeriodEl.className="gantt-time-period numday";
            containerTimePeriods.appendChild(timePeriodEl);

            //Agregar dias en el hijo
            const numDays=getDaysInMonth(month.getFullYear(),month.getMonth()+1);

            for (let i = 1; i <= numDays; i++) {
                let dayEl=document.createElement("div");
                dayEl.className="gantt-time-period";
                const dayElSpan=document.createElement("span");
                dayElSpan.innerHTML=i;
                dayEl.appendChild(dayElSpan);
                timePeriodEl.appendChild(dayEl);
                
            }
            
            month.setMonth(month.getMonth()+1);
        }
    }
    
    function createDaysOfTheWeekRow(startMonth,numMonths) {
        let month=new Date(startMonth);

        for (let i = 0; i < numMonths; i++) {
            const timePeriodEl=document.createElement("div");
            timePeriodEl.className="gantt-time-period day";
            containerTimePeriods.appendChild(timePeriodEl);
    
            //Agregar dias de la semana como hijo
            const currentYear=month.getFullYear();
            const currentMonth=month.getMonth()+1;
            const numDays=getDaysInMonth(currentYear,currentMonth);
    
            for (let i = 1; i <= numDays; i++) {
                let dayEl=document.createElement("div");
                dayEl.className="gantt-time-period";
                const daysOfTheWeek=getDayOfWeek(currentYear,currentMonth-1,i-1);
                const dayElSpan=document.createElement("span");
                dayElSpan.innerHTML=daysOfTheWeek;
                dayEl.appendChild(dayElSpan);
                timePeriodEl.appendChild(dayEl);
                
            }
            
            month.setMonth(month.getMonth()+1);
        }
    }
    
    function createTaskRowsTimePeriods(startMonth,numMonths) {
        const dayElContainer=document.createElement("div");
        dayElContainer.className="gantt-time-period-cell-container";
        dayElContainer.style.gridTemplateColumns=`repeat(${numMonths}, 1fr)`;

        containerTimePeriods.appendChild(dayElContainer);
        
        tasks.forEach((task)=>{
            let month=new Date(startMonth);
        
            for (let i = 0; i < numMonths; i++) {
                const timePeriodEl=document.createElement("div");
                timePeriodEl.className="gantt-time-period";
                dayElContainer.appendChild(timePeriodEl);
        
                //Agregar dias de la semana como hijo
                const currentYear=month.getFullYear();
                const currentMonth=month.getMonth()+1;
                const numDays=getDaysInMonth(currentYear,currentMonth);
        
                for (let i = 1; i <= numDays; i++) {
                    let dayEl=document.createElement("div");
                    dayEl.className="gantt-time-period-cell";

                    // color de celda de fin de semana diferentemente
                    const dayOfTheWeek=getDayOfWeek(currentYear,currentMonth-1,i-1);
                    if(dayOfTheWeek==="D"){
                        dayEl.style.backgroundColor="#f5f5dc";
                    }

                    // agregar atributos tarea y fecha
                    const formattedDate=createFormattedDateFromStr(currentYear,currentMonth,i);

                    dayEl.dataset.task=task.id;
                    dayEl.dataset.date=formattedDate;

                    // para arrastrar y eliminar
                    dayEl.ondrop=onTaskDurationDrop;
                    timePeriodEl.appendChild(dayEl);
                    
                }
                
                month.setMonth(month.getMonth()+1);
            }
        });
    }

    function addTaskDurations() {
        taskDurations.forEach((taskDuration)=>{
            const dateStr=createFormattedDateFromDate(taskDuration.start);

            // Encontrar posicion inicial gantt-period-cell
            const startCell=containerTimePeriods.querySelector(
                `div[data-task="${taskDuration.task}"][data-date="${dateStr}"]`
            );

            if(startCell){
                // la barra de taskDuration es un hijo de la posicion fecha inicial de la tarea especifica
                createTaskDurationEl(taskDuration,startCell);
            }
        });
    }

    function createTaskDurationEl(taskDuration,startCell) {
        const dayElContainer=containerTimePeriods.querySelector(
            ".gantt-time-period-cell-container"
        );
        const taskDurationEl=document.createElement("div");
        taskDurationEl.classList.add("task-duration");
        taskDurationEl.id=taskDuration.id;

        const days=dayDiff(taskDuration.start,taskDuration.end);
        taskDurationEl.style.width=`calc(${days}*100%)`;

        // arrastrar y eliminar
        taskDurationEl.draggable="true";

        taskDurationEl.addEventListener("dragstart",(e)=>{
            taskDurationEl.classList.add("dragging");
            // determina el elemento taskDuration ha sido arrastrado
            taskDurationElDragged=e.target;
        });

        taskDurationEl.addEventListener("dragend",()=>{
            taskDurationEl.classList.remove("dragging");
        });

        dayElContainer.addEventListener("dragover",(e)=>{
            e.preventDefault();
        });

        // agregar event listener para eliminar taskDuration
        taskDurationEl.tabIndex=0;
        taskDurationEl.addEventListener("keydown",(e)=>{
            if(e.key==="Delete" || e.key==='Backspace'){
                popoverContainer.classList.toggle('hidden');
                selectedTask.innerHTML=`¿Estás seguro de que deseas eliminar la actividad Nº ${+selectTask(e)}?\nEsta acción no se puede deshacer.`;
                buttonSendDeleteTask.href=link+selectTask(e);
            }
        });

        // agregar en posicion inicial
        startCell.appendChild(taskDurationEl);

        return days;
    }

    function onTaskDurationDrop(e) {
        const targetCell=e.target;

        // prevenir agregar en otra TaskDuration
        if(targetCell.hasAttribute("draggale")) return;

        // encontrar la tarea
        const taskDuration=taskDurations.filter(
            (taskDuration)=>taskDuration.id===taskDurationElDragged.id
        )[0];

        const dataTask=targetCell.getAttribute("data-task");
        const dataDate=targetCell.getAttribute("data-date");

        // eliminar antigua posicion del DOM
        taskDurationElDragged.remove();
        //Agregar nuea posicion al DOM
        const daysDuration=createTaskDurationEl(taskDuration,targetCell);

        // obtener valores de nueva tarea
        // obtener inicio, calcular fin
        const newTask=parseInt(dataTask);
        const newStartDate=new Date(dataDate);
        let newEndDate=new Date(dataDate);
        newEndDate.setDate(newEndDate.getDate()+daysDuration-1);

        //actualizar taskDuration
        taskDuration.task=newTask;
        taskDuration.start=newStartDate;
        taskDuration.end=newEndDate;

        const newTaskDurations=taskDurations.filter(
            (taskDuration)=>taskDuration.id!==taskDurationElDragged.id
        );

        newTaskDurations.push(taskDuration);
        //actualizar original / hacer una solicitud API para actualizar data en backend
        
        taskDurations=newTaskDurations;
    }

    function deleteTaskDuration(e) {
        const taskDurationToDelete=e.target;
        // eliminar del DOM
        taskDurationToDelete.remove();

        //Actualizar
        const newTaskDurations=taskDurations.filter(
            (taskDuration)=>taskDuration.id!==taskDurationToDelete.id
        );
        // actualizar original / hacer solicitud API
        taskDurations=newTaskDurations;

        return taskDurationToDelete.id;
    }

    function selectTask(e){
        const taskDurationSelect=e.target;
        return taskDurationSelect.id;
    }

    function handleAddTaskDurationForm(e) {
        e.preventDefault();
        const task=parseInt(e.target.elements["id_vehiculo"].value);
        const start=e.target.elements["fecha_inicio"].value;
        const end=e.target.elements["fecha_final"].value;
        const startDate=new Date(start);
        const endDate=new Date(end);

        const timeStamp=Date.now();
        const taskDuration={
            id:`${timeStamp}`,
            start:startDate,
            end:endDate,
            task:task,
        };
        //agregar 
        taskDurations.push(taskDuration);
        
        // encontrar la posicion inicial de gantt-time-period-cell
        const startCell=containerTimePeriods.querySelector(
            `div[data-task="${taskDuration.task}"][data-date="${start}"]`
        );
        console.log(startCell,taskDurations,task);

        if(startCell){
            createTaskDurationEl(taskDuration,startCell);
        }

        // var request= new XMLHttpRequest();
        // request.open("POST","/cronograma_vehiculos/",true);
        // request.send();
        // request.response;

        // createGrid();// Actualizado
    }

    function handleAddTaskForm(e) {
        e.preventDefault();

        const newTaskName=e.target.elements[0].value;
        //encontrar la tarea mas larga agregar 1 para nueva tarea
        const maxIdVal=tasks.reduce(function (a,b) {
            return Math.max(a,b.id);
        },-Infinity);
        //crear nueva tarea
        tasks.push({id:maxIdVal+1,name:newTaskName});
        // volver a crear grid
        createGrid();
    }

    function updateTask(e) {
        const {id}=e.target.parentNode;
        const {value}=e.target.parentNode.firstChild;
        const idNum=parseInt(id);
        let newTasks=tasks.filter((task)=>task.id!==idNum);
        newTasks.push({id:idNum,name:value});

        newTasks=newTasks.sort((a,b)=>a.id-b.id);

        // para actualizar API
        tasks=newTasks;

        //actualizar tareas seleccionadas
        let newTaskOptionsHTMLStrArr=[];
        tasks.forEach((task)=>{
            newTaskOptionsHTMLStrArr.push(`<option value="${task.id}">${task.name}</option>`);
            // taskSelect.innerHTML=`${newTaskOptionsHTMLStrArr.join("")}`;
        });
    }

    function deleteTask(e) {
        const id=parseInt(e.target.parentNode.id);
        // filtrar tarea de afuera para eliminar
        const newTasks=tasks.filter((task)=>task.id!==id);

        tasks=newTasks;

        //eliminar alguna taskDuration asociado con la tarea
        const newTaskDurations=taskDurations.filter(
            (taskDuration)=>taskDuration.task!==id
        );

        taskDurations=newTaskDurations;

        createGrid();
    }

    

    // Salir de popover
    buttonCancelDeleteTask.addEventListener("click",()=>{
        popoverContainer.classList.toggle('hidden');
    })

    // volver a crear grid si year o month son cambiados
    fromSelectYear.addEventListener("change",createGrid);
    fromSelectMonth.addEventListener("change",createGrid);
    toSelectYear.addEventListener("change",createGrid);
    toSelectMonth.addEventListener("change",createGrid);

    // addTaskDurationForm.addEventListener("submit",handleAddTaskDurationForm);
    // addTaskForm.addEventListener("submit",handleAddTaskForm);
}