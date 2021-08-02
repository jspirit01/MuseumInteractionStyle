 $('.logo').on('click',function(e){
    e.preventDefault();
    const result=confirm('메인으로 가시겠습니까?')
    if(result){
      location.href='/'
        localStorage.clear()
    }
  })

  $('.link-next').on('click',function(e){
    e.preventDefault();
    const paging = $('.paging').text();
    if(paging !== '4/4'){$.ajax({
        type: 'POST',
        async: false,                                  <!--[GET / POST] 둘중 하나 선택-->
        url: '/next_paging',
        data: {'paging': paging},
        dataType: 'json',
        success: function (result) {
            localStorage.setItem("cast", JSON.stringify(result))
            location.href=result['target_html']
        },
        error: function (xtr, status, error) {alert(xtr + ":" + status + ":" + error);}
      });
    }
    else{
      const result=confirm('이 태스크가 마지막 태스크입니다. 초기 화면으로 돌아가시겠습니까?')
      if(result) {
        location.href = '/'
      }
    }
  })

  $('.link-prev').on('click',function(e){
    e.preventDefault();
    const paging = $('.paging').text();
    if(paging !== '1/4'){$.ajax({
        type: 'POST',
        async: false,                                  <!--[GET / POST] 둘중 하나 선택-->
        url: '/prev_paging',
        data: {'paging': paging},
        dataType: 'json',
        success: function (result) {
            localStorage.setItem("cast", JSON.stringify(result))
            location.href=result['target_html']
        },
        error: function (xtr, status, error) {alert(xtr + ":" + status + ":" + error);}
      });
    }
    else{
      alert('이미 첫번째 태스크입니다.')
    }
  })

 const loadpaging = function(result){

    $('.description-list').empty();
    $('.paging').text(result['paging']);
    $('#img-id').attr("src", result['img_url']);
    $('.title').text(result['title']);
    for(var i=0; i<result['li'].length; i++){
      const li_item = result['li'][i].replaceAll("-", "");
       $('.description-list').append(`
      <li> ${li_item}</li>
    `)
    }
    $('.text-area').text(result['text-area']);
    }

 $(document).ready(function () {
     const result = JSON.parse(localStorage.getItem("cast"));
    $("#dynamic-description").load(result['dynamic_html'], function () {
         //페이지 별로 다른 메뉴 css 적용도 가능
         $('.title').text(result['title']);
        $('#img-id').attr("src", result['img_url']);
     });
     loadpaging(result)
    })
