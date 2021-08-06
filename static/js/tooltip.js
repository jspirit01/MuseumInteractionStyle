 $('.mytooltip').on({
   mouseenter: function() {
        let type = $(this).data('type');
        let position = $(this).data('position');
        let img = $(this).data('img');
        let tooltip = $(this).data('tooltip-text');
        $(this).find('.tooltip-content').remove()
       if(type == 'pink'){
           $(this).append(`
             <span class="tooltip-content ${position}">
                  <img src="${img}" alt="">
                  <span class="tooltip-text">${tooltip}</span>
              </span>
        `)
       }else if(type == 'yellow'){
           $(this).append(`
             <span class="tooltip-content ${position}">
                  <span class="tooltip-text">${tooltip}</span>
              </span>
        `)
       }else if(type == 'green'){
           $(this).append(`
             <span class="tooltip-content ${position}">
                   <img src="${img}" alt="">
              </span>
        `)
       }
  }, mouseleave: function() {
       $(this).find('.tooltip-content').remove()
  }
});