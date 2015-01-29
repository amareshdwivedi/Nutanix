// JavaScript Document		
jQuery(document).ready(function() {
	getCustomers();
	
	function getCustomers(){
		$.ajax({
			 type: "GET",
			 url: "/v1/deployer/customers/",
			 async: false,
			 dataType: "json",
			 success: function(data){
				var customers='';
				for (var i = 0; i < data.customer_record.length; i++) {
					customers += '<tr><td class="customerId">'+data.customer_record[i].customer_id+'</td><td class="customerName">'+data.customer_record[i].customer_name+'</td></tr>';
				}
				$("table.customersTable tbody").html(customers);
			 },
			 error: function(request,status,errorThrown){
				 alert("No Data Available");
			 }
		});	
	}
	
	function getCutomerDetails(customerId){
		$.ajax({
		 type: "GET",
		 url: "/v1/deployer/customers/"+customerId+"/",
		 async: false,
		 dataType: "json",
		 success: function(data){
			 $(".customerDetails").show();
			 $(".customerDetails h3 span").html(data.customer_record[0].customer_name);
			 var customerDetail='';
				for (var i = 0; i < data.customer_history.length; i++) {
					customerDetail += '<tr><td class="id">'+data.customer_history[i].id+'</td><td class="status">'+data.customer_history[i].status+'</td><td class="task">'+data.customer_history[i].task+'</td><td class="date_created">'+data.customer_history[i].date_created+'</td></tr>';
				}
				$("table.customersDetailsTable tbody").html(customerDetail);
		 },
		 error: function(request,status,errorThrown){
			 alert("No Data Available");
		 }
		});
	}
	
	$(".customersTable tbody").on('click','tr',function(){
			$(".customersTable tbody tr").removeClass("row_selected");
			$(this).addClass("row_selected");
			var customerId = $(this).find('td.customerId').html();
			getCutomerDetails(customerId);
	});
	
	$(".createNewCustomerBtn").click(function(){
		var isFormValid = true;
		$(".createCustomer-form .form_input input").each(function(index, value){
			if ($.trim($(value).val()).length == 0){
				$(value).parent().addClass("error");
				$(".errorMsg").show();
				$(".errorMsg").html("Please fill in all the required fields (highlighted in red)");
				isFormValid = false;
			} else {
				$(value).parent().removeClass("error");
				$(".errorMsg").hide();
				$(".errorMsg").html("");
			}
		});

		if(isFormValid ){
		  var formData = {}
			$('#createNewCustomer .form_input input').each(function() {
				formData[$(this).attr('name')] = $(this).val();
			});
			$("#createCustomerModal .modal-body").html("");
		  $.ajax({
			 type: "POST",
			 url: "/v1/deployer/customers/",
			 async: false,
			 dataType:'json',
			 data: JSON.stringify(formData),
			 success: function(data)
			 {
				 if(data.response == 200){
					 $('#createCustomerModal').modal();
					 $("#createCustomerModal .modal-body").html(data.message);
					 getCustomers();
				 }
				 else{
					 $('#createCustomerModal').modal();
					 $("#createCustomerModal .modal-body").html(data.error);
				 }
			 },
			 error: function (jqXHR, textStatus, errorThrown)
			 {
				$('#createCustomerModal').modal();
				$("#createCustomerModal .modal-body").html("Unable to Create New Customer.");
			 }
			});
		}
	});
	
	
	$("a.kickoffBtn").click(function(){
		var cutomerId = $(".customersTable tr.row_selected td.customerId").text();
		alert(cutomerId);
		getCustomerTask(cutomerId);
	});
	
	function getCustomerTask(cutomerId){
		alert(cutomerId);
		$.ajax({
			 type: "GET",
			 url: "/v1/deployer/customers/"+cutomerId+"/tasks/",
			 async: false,
			 dataType: "json",
			 success: function(data){
				//alert(data);
			 },
			 error: function(request,status,errorThrown){
				 alert("No Data Available");
			 }
		});	
	}
	
});