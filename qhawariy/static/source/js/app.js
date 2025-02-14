
// CLASES QUE SON UTILIZADOS EN LA APPLICACION WEB QHAWARIY
class ButtonToggle
    {
      constructor(btn,element,type_toggle="elementToggle")
      {
        this.btn=btn;
        this.element=element;
        this.type_toggle=type_toggle
        this.icon={
          open:'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="12px" height="7px" version="1.1" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 5.562 3.029" xmlns:xlink="http://www.w3.org/1999/xlink"><path fill="#707070" fill-rule="nonzero" d="M0.529 0.089c-0.124,-0.12 -0.321,-0.118 -0.441,0.006 -0.12,0.123 -0.117,0.32 0.006,0.44l2.48 2.404 0.218 -0.223 -0.218 0.225c0.124,0.12 0.322,0.116 0.442,-0.007 0.003,-0.004 0.006,-0.007 0.01,-0.011l2.442 -2.388c0.123,-0.12 0.126,-0.317 0.006,-0.44 -0.12,-0.124 -0.317,-0.127 -0.44,-0.007l-2.243 2.194 -2.262 -2.193 0 0z"/></svg>',
          closed:'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="12px" height="7px" version="1.1" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 5.562 3.029" xmlns:xlink="http://www.w3.org/1999/xlink"> <path fill="#707070" fill-rule="nonzero" d="M0.529 2.94c-0.124,0.12 -0.321,0.118 -0.441,-0.006 -0.12,-0.123 -0.117,-0.32 0.006,-0.44l2.48 -2.405 0.218 0.223 -0.218 -0.224c0.124,-0.12 0.322,-0.116 0.442,0.007 0.003,0.004 0.006,0.007 0.01,0.011l2.442 2.388c0.123,0.12 0.126,0.317 0.006,0.44 -0.12,0.124 -0.317,0.127 -0.44,0.007l-2.243 -2.194 -2.262 2.193 0 0z"/></svg>'
        };
        this.eyeIcon={
          open:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-[20px] w-[20px]"><path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/><path fill-rule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM17.25 12a5.25 5.25 0 11-10.5 0 5.25 5.25 0 0110.5 0z" clip-rule="evenodd"/></svg>',
          closed:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-[20px] w-[20px]"><path d="M3.53 2.47a.75.75 0 00-1.06 1.06l18 18a.75.75 0 101.06-1.06l-18-18zM22.676 12.553a11.249 11.249 0 01-2.631 4.31l-3.099-3.099a5.25 5.25 0 00-6.71-6.71L7.759 4.577a11.217 11.217 0 014.242-.827c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113z" /><path d="M15.75 12c0 .18-.013.357-.037.53l-4.244-4.243A3.75 3.75 0 0115.75 12zM12.53 15.713l-4.243-4.244a3.75 3.75 0 004.243 4.243z" /><path d="M6.75 12c0-.619.107-1.213.304-1.764l-3.1-3.1a11.25 11.25 0 00-2.63 4.31c-.12.362-.12.752 0 1.114 1.489 4.467 5.704 7.69 10.675 7.69 1.5 0 2.933-.294 4.242-.827l-2.477-2.477A5.25 5.25 0 016.75 12z" /></svg>'
        }
      }

      active()
      {
        if(this.type_toggle==='elementToggle'){
          this.btn.addEventListener('click',(e)=>{
            if(this.element.classList.contains('hidden'))
            {
              this.btn.innerHTML=this.icon.closed;
            }
            else
            {
              this.btn.innerHTML=this.icon.open;
            }
            this.element.classList.toggle("hidden");
          });
        }
        if(this.type_toggle==='passwordToggle'){
          this.btn.addEventListener('click',(e)=>{
            this.btn.classList.toggle("open");
            var isEyeOpen=this.btn.classList.contains("open");

            if(isEyeOpen){
              this.btn.innerHTML=this.eyeIcon.closed;
            }else{
              this.btn.innerHTML=this.eyeIcon.open;
            }

            if(isEyeOpen){
              this.element.type="text";
            }else{
              this.element.type="password";
            }
          });
        }
      }
    }

// ELEMENTOS BARRA DE NAVEGACION
class ElementNavBar
{
    constructor(clnElement,clnButton,clnBc=null){
        this.clnElement=document.querySelector(clnElement);
        this.clnButton=document.querySelector(clnButton);
        let aux;
        if(clnBc!=null)
        {
            aux=document.querySelector(clnBc);
        }
        else
        {
            aux=null;
        }
        this.clnBC=aux;
    }
}

document.addEventListener('DOMContentLoaded',()=>{

    // Agregando los elementos a la lista
    elements=[
        new ElementNavBar(".menu-user",".btn-user"),
        new ElementNavBar(".menu-element",".btn-menu"),
        new ElementNavBar(".modal-notificacion",".icon-close-m")
    ]

    // Activando el evento click a cada elemento
    function active(element){
        let ele=element.clnElement;
        let btn=element.clnButton;
        let ic=element.clnBC;

        window.addEventListener('click',(e)=>{
            if(btn!=null){
                if(btn.contains(e.target))
                {
                    if(ele.classList.contains('hidden'))
                    {
                        ele.classList.remove('hidden');
                        if(ic != null)
                        {
                            document.getElementById("buscar").focus();
                        }
                    }
                    else
                    {
                        ele.classList.add('hidden');
                    }
                }
                else
                {
                    // Cuando clickea fuera del icono
                    if(!ele.classList.contains('hidden'))
                    {
                        if(ic === null)
                        {
                            ele.classList.add('hidden');
                        }
                        else
                        {
                            if(ic.contains(e.target))
                            {
                                ele.classList.add('hidden');
                            }
                        }
                    }
                }
            }
        });
    }
    
    elements.forEach(element=>active(element));

    // TOOLTIP DE INGRESOS
    const iq=document.querySelectorAll(".icon-question-o");
    const tooltip=document.querySelectorAll(".tooltip");

    for (let i = 0; i < iq.length; i++) {
        const element = iq[i];
        const tt=tooltip[i];
        element.onmouseover=element.onmouseout=handler;
        function handler(event) {
            if (event.type=='mouseover') {
                tt.style.display="";
            }
            if (event.type=='mouseout') {
                tt.style.display="none";
            }
        }
    }

    // validate number only dni
    const ele=document.querySelector('.only-number');
    if(ele != null){
        ele.addEventListener('onkeydown',function (e) {
            if(isNaN(this.value+""+String.fromCharCode(e.charCode)))
            {
                return false;
            }
        });
    
        ele.addEventListener('onpaste',function(e){
            e.preventDefault();
        });

    }

    // Activar politica de cookies
    const aviso=document.querySelector(".cookie-control");
    const modal=document.querySelector('.cookie-control-modal');
    const btn_aceptar=document.querySelector(".btn-aceptar");
    const btn_config=document.querySelector(".btn-modal-active");
    const btn_modal_close=document.querySelector(".cookie-control-modal-close");

    btn_aceptar.addEventListener('click',()=>{
        if(!aviso.classList.contains("hidden"))
        {
            aviso.classList.add("hidden");
        }
    });

    btn_modal_close.addEventListener('click',()=>{
        if(!modal.classList.contains("hidden"))
        {
            modal.classList.add("hidden");
        }
    });

    btn_config.addEventListener('click',()=>{
        if(modal.classList.contains('hidden'))
        {
            modal.classList.remove("hidden");
        }
    });

    class Popover{
        constructor(button,content){
            this.button=document.querySelector(button);
            this.content=document.querySelector(content);

            this.init();
        }

        init(){
            this.button.addEventListener('click',()=>{
                this.toggle();
            });

            document.addEventListener('click',(event)=>{
                if(!this.button.contains(event.target) && !this.content.contains(event.target)){
                    this.hide();
                }
            });
        }

        toggle(){
            if(this.content.style.display==='block'){
                this.hide();
            } else {
                this.show();
            }
        }

        show(){
            this.content.style.display='block';
        }

        hide(){
            this.content.style='none';
        }
    }

});