$(document).ready(function(){
	(function(){

        $(".detail_button").on("click", function(){
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