import { cssStyle } from "./style.js";

export function createHtmlContentFragment() {
    const content=`
    <style>
        ${cssStyle()}
    </style>
    <div id="gantt-container">
        <div class="flex items-center justify-end sm:justify-center">
            <div class="tracker-period sm:w-full">
                <p class="text-h6 text-center">Mostra periodo</p>
                <div class="grid grid-cols-2 sm:grid-cols-1 sm:gap-y-0 gap-6" id="settings">
                    <fieldset id="select-from" class="items-center grid grid-cols-4-2-2 gap-4 sm:gap-y-0">
                        <legend class="col-span-4 order-1">Desde</legend>
                        <label class="text-right order-2" for="from-select-month">Mes</label>
                        <select class="order-3 rounded-xxs w-full border text-black-100 text-sm px-4 py-3 border-gray-209" name="from-select-month" id="from-select-month"></select>
                        <label class="text-right order-4" for="from-select-year">Año</label>
                        <select class="order-5 rounded-xxs w-full border text-black-100 text-sm px-4 py-3 border-gray-209" name="from-select-year" id="from-select-year"></select>
                    </fieldset>
                    <fieldset id="select-to" class="items-center grid grid-cols-4-2-2 gap-4 sm:gap-y-0 ">
                        <legend class="col-span-4">Hasta</legend>
                        <label class="text-right" for="to-select-month">Mes</label>
                        <select class="rounded-xxs border w-full text-black-100 text-sm px-4 py-3 border-gray-209" name="to-select-month" id="to-select-month"></select>
                        <label class="text-right" for="to-select-year">Año</label>
                        <select class="rounded-xxs border w-full text-black-100 text-sm px-4 py-3 border-gray-209" name="to-select-year" id="to-select-year"></select>
                    </fieldset>
                </div>
            </div>
        </div>
        <div class="cursor-pointer" id="gantt-grid-container">
            <div id="gantt-grid-container__tasks"></div>
            <div id="gantt-grid-container__time"></div>
        </div>
    </div>
    <div class="hidden popover-container fixed all-screen black-opacity">
        <div class="popover-content center-drawer flex flex-col items-center justify-center">
            <p class="text-align-left text-body2 mb-4" id="selected-task" name="selected-task"></p>
            <div class="mt-3">
                <a href="" class="delete-task btn btn--base bg-red-600 rounded text-white">
                    <p class="ml-2 text-xs">Eliminar</p>
                </a>
                <a href="#" class="delete-cancel btn btn--base btn-green-600 rounded ml-2">
                    <p class="ml-2 text-xs">Cancelar</p>
                </a>
            </div>
        </div>
    </div>
    `;
    // 
    const contentFragment=document.createRange().createContextualFragment(content);
    return contentFragment;
}

export function createHtmlElementFragment() {
    const imgClose=`<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="20px" height="20px" version="1.1" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd"
    viewBox="0 0 0.344 0.344"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xodm="http://www.corel.com/coreldraw/odm/2003" type="image/svg+xml">
        <g id="Capa_x0020_1">
            <metadata id="CorelCorpID_0Corel-Layer"/>
            <path fill="#878C8F" fill-rule="nonzero" d="M0.297 0.01l-0.125 0.125 -0.126 -0.125c-0.004,-0.006 -0.012,-0.01 -0.02,-0.01 -0.014,0 -0.026,0.012 -0.026,0.026 0,0.008 0.004,0.016 0.01,0.02l0.125 0.126 -0.125 0.125c-0.006,0.005 -0.01,0.012 -0.01,0.021 0,0.014 0.012,0.026 0.026,0.026 0.008,0 0.016,-0.004 0.02,-0.01l0.126 -0.126 0.125 0.126c0.005,0.006 0.012,0.01 0.021,0.01 0.014,0 0.026,-0.012 0.026,-0.026 0,-0.009 -0.004,-0.016 -0.01,-0.021l-0.126 -0.125 0.126 -0.126c0.006,-0.004 0.01,-0.012 0.01,-0.02 0,-0.014 -0.012,-0.026 -0.026,-0.026 -0.009,0 -0.016,0.004 -0.021,0.01z"/>
        </g>
    </svg>`;
    const imgElement=document.createRange().createContextualFragment(imgClose)
    return imgElement;
}