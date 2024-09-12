document.addEventListener('DOMContentLoaded',()=>{
    // Para enfocar scroll
    const sect=document.querySelectorAll('.section-count');
    const sect_padre=document.querySelector('.section-padre');
    const ch=sect_padre.clientHeight
    const csh=sect_padre.scrollHeight
    sect_padre.scrollTop=csh-ch;
    // var current_section=sect.length;
    // // const scrollButton=document.querySelector('#submit');
    // const s='section'+current_section;
    // const section=document.getElementById(s);
    // if(section){
    //     const sectionTop = section.offsetTop;
    //     sect_padre.scrollTo({
    //         top: sectionTop,
    //         left:0,
    //         behavior:'smooth'
    //     });
    //     console.log(sectionTop);
    // }
    // console.log(csh-ch);
});