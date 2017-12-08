$(document).ready(function(){
	(function(){
        onclick="javascript: window.location='amazon/follow/detail/{{ follow_product['site'] }}/{{ follow_product['asin'] }}'"

        $(".detail_button").on("click", function(){
            button = $(this);
            site = button.attr("data-site");
            asin = button.attr("data-asin");

            link = 'amazon/follow/detail/' + site + '/' + asin;
            window.location.href=link;
        });

        $(".delete_button").on("click", function(){
            button = $(this);

            $.ajax({
                "url": "/amazon/follow/delete",
                "type": "post",
                "data": {
                    "_xsrf": $.cookie("_xsrf"),
                    "site": button.attr("data-site"),
                    "asin": button.attr("data-asin")
                },
                "dataType": "json",
                "success": function(data){
                    button.closest('tr').remove();
                }
            });

            return false;
        })

	})();
});