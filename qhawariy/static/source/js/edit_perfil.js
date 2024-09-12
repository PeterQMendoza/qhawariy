document.addEventListener('DOMContentLoaded',()=>{
    // Editar Datos del Perfil de Usuario
    let arr=[]
    const div_el=document.querySelectorAll('.div-hidden')
    const btn_click=document.querySelectorAll('.btn-click');

    class ButtonEditar
    {
        constructor(btn,div)
        {
            this.btn=btn;
            this.div=div;
            this.icon={
                open:'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="12px" height="7px" version="1.1" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 5.562 3.029" xmlns:xlink="http://www.w3.org/1999/xlink"><path fill="#707070" fill-rule="nonzero" d="M0.529 0.089c-0.124,-0.12 -0.321,-0.118 -0.441,0.006 -0.12,0.123 -0.117,0.32 0.006,0.44l2.48 2.404 0.218 -0.223 -0.218 0.225c0.124,0.12 0.322,0.116 0.442,-0.007 0.003,-0.004 0.006,-0.007 0.01,-0.011l2.442 -2.388c0.123,-0.12 0.126,-0.317 0.006,-0.44 -0.12,-0.124 -0.317,-0.127 -0.44,-0.007l-2.243 2.194 -2.262 -2.193 0 0z"/></svg>',
                closed:'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="12px" height="7px" version="1.1" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 5.562 3.029" xmlns:xlink="http://www.w3.org/1999/xlink"> <path fill="#707070" fill-rule="nonzero" d="M0.529 2.94c-0.124,0.12 -0.321,0.118 -0.441,-0.006 -0.12,-0.123 -0.117,-0.32 0.006,-0.44l2.48 -2.405 0.218 0.223 -0.218 -0.224c0.124,-0.12 0.322,-0.116 0.442,0.007 0.003,0.004 0.006,0.007 0.01,0.011l2.442 2.388c0.123,0.12 0.126,0.317 0.006,0.44 -0.12,0.124 -0.317,0.127 -0.44,0.007l-2.243 -2.194 -2.262 2.193 0 0z"/></svg>'
              };
        }

        active()
        {
            this.btn.addEventListener('click',(e)=>{
                if(this.div.classList.contains('hidden'))
                {
                    this.btn.innerHTML='Ocultar';
                }
                else
                {
                    this.btn.innerHTML='Editar';
                }
                this.div.classList.toogle('hidden');
            });
        }
    }

    arr=[
        new ButtonEditar(btn_click[0],div_el[0]),
        new ButtonEditar(btn_click[1],div_el[1]),
        new ButtonEditar(btn_click[2],div_el[2]),
        new ButtonEditar(btn_click[3],div_el[3]),
    ]

    arr.forEach(ele=>{
        ele.active();
    })
});