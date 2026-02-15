export function cssStyle() {
    const CELL_HEIGHT=28;
    const outlineColor="#D1CEC3";

    return `
    
    #date > label:nth-child(3){
        margin-left:10px;
    }

    button::hover{
        cursor:pointer;
    }

    .title{
        text-align:center;
        margin-bottom:10px;
    }

    #gantt-container{
        padding:0;
    }

    #gantt-grid-container{
        display:grid;
        grid-template-columns:150px 1fr;
        // outline:1px solid ${outlineColor};
        border-top:1px solid ${outlineColor};
        border-left:1px solid ${outlineColor};
    }

    #gantt-grid-container__time{
        display:grid;
        overflow-x:auto;
        direction:ltr;
    }

    .gantt-task-row{
        display:flex;
        align-items:center;
        //outline:0.5px solid ${outlineColor};
        text-align:center;
        height:${CELL_HEIGHT}px;
        //expand across whole grid
        grid-column:1/-1;
        width:100%;
        border-right:0.5px solid ${outlineColor};
        border-bottom:0.5px solid ${outlineColor};
    }

    .gantt-task-row button{
        border:none;
        height:${CELL_HEIGHT}px;
    }

    .gantt-task-row input{
        display:block;
        width:100%;

    }

    #gantt-grid-container__tasks button{
        color:#EF5350;
        background:none;
        border-radius:5px;
        height:20px;
        transition: all 0.2s ease;
    }

    #gantt-grid-container__tasks button:focus{
        outline:none;
        transform: scale(1.3);
    }

    #gantt-grid-container__tasks .gantt-task-row{
        padding: 4px;
    }

    .gantt-time-period{
        display:grid;
        grid-auto-flow:column;
        grid-auto-columns:minmax(30px, 1fr);
        text-align:center;
        height:${CELL_HEIGHT}px;
    }

    .gantt-time-period span{
        margin:auto;
    }

    .gantt-time-period-cell-container{
        grid-column:1/-1;
        display:grid;
        border-right:0.5px solid ${outlineColor};
        border-bottom:0.5px solid ${outlineColor};
    }

    .gantt-time-period-cell{
        position:relative;
        outline:0.5px solid ${outlineColor};//Mantiene el perio de tiempo al mismo tamano de la duracion de tarea
        --qh-bg-opacity:1;
        background-color: rgba(252, 249, 249, var(--qh-bg-opacity));
    }

    .day{
        --qh-text-opacity: 1;
        color: rgb(5 190 80 / var(--qh-text-opacity));
        border-right:0.5px solid ${outlineColor};
    }

    .months{
        border-right:0.5px solid ${outlineColor};
    }

    .numday{
        border-right:0.5px solid ${outlineColor};
        border-bottom:0.5px solid ${outlineColor};
    }

    #settings{
        font-size: 14px;
        padding-bottom: 0.5rem;
    }

    .task-duration{
        position: absolute;
        height: ${CELL_HEIGHT}px;
        z-index: 1;
        background: linear-gradient(90deg, rgba(100, 180, 230,1) 0%, rgba(21,86,207, 1) 100%);
        border-radius: 5px;
        box-shadow: 3px 3px 3px rgba(0,0,0,0.05);
        cursor: move;
    }

    .task-duration:focus{
        outline: 2px solid rgba(0, 57, 166,1);
    }

    .dragging{
        opacity: 0.5;
    }

    #add-forms-container{
        display: flex;
        align-items:center;
        flex-wrap: wrap;
        padding: 1rem 0;
        justify-content: space-around;
    }

    #add-forms-container form > *{
        display: flex;
        align-items: center;
    }

    #add-forms-container input{
        height: ${CELL_HEIGHT}px;
    }

    #add-task, #add-task-duration{
        margin-right: 10px;
        margin-bottom: 10px;
    }

    #add-forms-container button{
        transition: all 0.3s ease;
    }

    .tracker-period{
        padding: 0;
    }

    .tracker-period p{
        margin-bottom: 8px;
    }

    .inner-form-container{
        // display: flex;
        // flex-direction: row;
        // // justify-content: space-between;
        // // align-items: center;
    }

    `;
}