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
                 
                 if(data.response != 404 || data.response != '404'){
                    for (var i = 0; i < data.customer_record.length; i++) {
                        customers += '<tr><td class="customerId">'+data.customer_record[i].customer_id+'</td><td class="customerName">'+data.customer_record[i].customer_name+'</td></tr>';
                    }
                    
                    $("table.customersTable tbody").html(customers);
                    
                }
                 
				
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
            $("#customerId").val(customerId);
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
				isFormValid = true;
			}
		});

		if(isFormValid ){
		  var formData = {}
			$('#createNewCustomerModel .form_input input').each(function() {
				formData[$(this).attr('name')] = $(this).val();
			});
			//$("#createCustomerModal .modal-body").html("");
		  $.ajax({
			 type: "POST",
			 url: "/v1/deployer/customers/",
			 async: false,
			 dataType:'json',
			 data: JSON.stringify(formData),
			 success: function(data)
			 {
				 if(data.response == 200){
					 $('#createNewCustomerModel').modal();
					 $("#createNewCustomerModel .modal-body .form_fields_container").hide();
                     $("#createNewCustomerModel .modal-body .sucessMsg").show();
                     $(".createNewCustomerBtn").hide();
                     $("#createNewCustomerModel .cancelButton").show();
                     $("#createNewCustomerModel .modal-body .sucessMsg").html(data.message);
					 getCustomers();
                     
                      $('.createCustomer-form').find('input:text').val('');
                      $('.createCustomer-form').find('input:email').val('');
                     location.reload(false);
				 }
				 else{
					 $('#createNewCustomerModel').modal();
					 $("#createNewCustomerModel .modal-body .form_fields_container").hide();
                     $("#createNewCustomerModel .modal-body .sucessMsg").show();
                      $(".createNewCustomerBtn").hide();
                     $("#createNewCustomerModel .cancelButton").show();
                     $("#createNewCustomerModel .modal-body .sucessMsg").html(data.error);
                     //location.reload(false);
				 }
			 },
			 error: function (jqXHR, textStatus, errorThrown)
			 {
				$('#createNewCustomerModel').modal();
				$("#createNewCustomerModel .modal-body").html("Unable to Create New Customer.");
			 }
			});
		}
	});
	
	
	$("a.kickoffBtn").click(function(){
		var cutomerId = $(".customersTable tr.row_selected td.customerId").text();
		getCustomerTask(cutomerId);
	});
	
	function getCustomerTask(cutomerId){
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
  
    function createCustomerTask(cutomerId,json_data){
		$.ajax({
			 type: "POST",
			 url: "/v1/deployer/customers/"+cutomerId+"/tasks/",
			 async: false,
			 dataType: "json",
             data:JSON.stringify(json_data),
			 success: function(data){
				//alert(data);
                 if(data.response == 200){
					 /*$('#commonModal').modal();
                     $("#commonModal .modal-header h4.modal-title").html("Create Task");
					 $("#commonModal .modal-body").html("Task Created Successfully.");*/
                     $("#task_id").val(data.task_id);
                     $(".successMessage").show();
                     $( "#mainTabContainer" ).tabs( "enable", 2 ).tabs( "select", 2 );
				 }
				 else{
					 $('#commonModal').modal();
					 $("#commonModal .modal-body").html("Unable to create task.");
				 }
			 },
			 error: function(request,status,errorThrown){
				 alert("No Data Available");
			 }
		});	
	}
    
    /*Predeployer Submit Start*/
    
    var main_rest_block = {};
		$("#submit_all").click(function(){
			var mainObject = {};
			
				var foundationObject = {};
				var restInput = {};

				foundationObject["ipmi_netmask"] = $('#IPNM').val();
				foundationObject["ipmi_gateway"] = $('#IPMGateway').val();
				foundationObject["ipmi_user"] = $('#IPMIUsernanme').val();
				foundationObject["ipmi_password"] = $('#IPMIPass').val();
				
				foundationObject["hypervisor_netmask"] = $('#HyperversionNM').val();
				foundationObject["hypervisor_gateway"] = $('#HyperversionGateway').val();
				foundationObject["hypervisor_nameserver"] = $('#HyperverNameServer').val();
				
				foundationObject["cvm_netmask"] = $('#CvmNM').val();
				foundationObject["cvm_gateway"] = $('#Cvmgateway').val();
				//foundationObject["cvmmemory"] = $('#CvmMemory').val()
				
				foundationObject["cluster_name"] = $('#cluster_name').val();
				//var cluster_external_ip = $('#externalIP').val();
				foundationObject["cluster_external_ip"] = $.trim($('#externalIP').val());
				var redundancy_factor = $('#redundancy_factor').val();
				if(redundancy_factor == "null"){
					redundancy_factor = null;
				}
				foundationObject["redundancy_factor"] = redundancy_factor;
				
				foundationObject["cvm_dns_servers"] =  $('#CVMDNSSERVER').val();
				foundationObject["cvm_ntp_servers"] = $('#CVMNTPSERVER').val();
				foundationObject["hypervisor_ntp_servers"] = $('#HYPERVERSIONCVMNTPSERVER').val();

				foundationObject["phoenix_iso"] = $('#phoenix_iso').val();
				foundationObject["hypervisor_iso"] = $('#hypervisor_iso').val();

				//foundationObject["use_foundation_ips"] = $('#foundation_ip').val();
				foundationObject["use_foundation_ips"] = false;
				foundationObject["cluster_init_successful"] = null;
				
				foundationObject['hypervisor_password'] = $('#hypervisorpass').val();
				foundationObject["hypervisor_iso"] = $('#hypervisor_iso').val();
				
				foundationObject["phoenix_iso"] = $('#phonix_iso').val();
				
				foundationObject['cluster_init_now'] = true;
				var nodes = [];
				var mainblock = {}
				var blocks = [];
    
                var hosts = [];
               

				foundationObject["ipmi_netmask"] = $('#IPNM').val();
				
                var blocklength = $(".blockContainer").length;
				$('div.blockContainer').each(function() {
                     var block_id = $(this).attr("id");
                     var nodelength = $("#"+block_id+ " .nodeContainer").length;    
                     var i = 1;
                    var j = 1;
                     $("#"+block_id+ " .nodeContainer").each(function(){
                         var node_id = $(this).attr("id");
                          var vcenterhosts = {};
                         var a = $("#"+block_id+ " #"+node_id+ " #ipmimac").val();

						var nodeObject  = {};
						//var ipmi_mac = $('#ipmimac'+i).val();
                        nodeObject['ipmi_mac'] = $("#"+block_id+ " #"+node_id+ " #ipmimac").val();
						//nodeObject['ipmi_mac'] =$('#ipmimac'+i).val();
						//var ipmi_ip = $('#ipmiip'+i).val();
						nodeObject['ipmi_ip'] =$("#"+block_id+ " #"+node_id+ " #ipmiip").val(); //$('#ipmiip'+i).val();
						//var hypervisor_ip = $('#hyperversionip'+i).val();
						nodeObject['hypervisor_ip'] = $("#"+block_id+ " #"+node_id+ " #hyperversionip").val();// $('#hyperversionip'+i).val();
						//var cvm_ip = $('#cvmip'+i).val();
                         
						nodeObject['cvm_ip'] = $("#"+block_id+ " #"+node_id+ " #cvmip").val();// $('#cvmip'+i).val();
                         
                         
                        if(j == 1 || j == "1"){
                           
                            var restbaseurl = "https://"+nodeObject['cvm_ip']+":9440/PrismGateway/services/rest/";
                             $('#restURL').val(restbaseurl);
                        } 
						//var hypervisor_hostname = $('#hyperversionhostname'+i).val();
		nodeObject['hypervisor_hostname'] =  $("#"+block_id+ " #"+node_id+ " #hyperversionhostname").val();//$('#hyperversionhostname'+i).val();
						
						
                         
                        vcenterhosts['ip'] = $("#"+block_id+ " #"+node_id+ " #hyperversionip").val();
					    vcenterhosts['user'] = $('#v_center_user').val();
					    vcenterhosts['pwd'] = $('#v_center_vm_password').val();
                        hosts.push(vcenterhosts);

						//var cvm_gb_ram = $('#cvm_gb_ram'+i).val();
						nodeObject['cvm_gb_ram'] = parseInt($('#node_ram').val());
						
						//var ipv6_address = $('#ipv6_address'+i).val();
						nodeObject['ipv6_address'] = $("#"+block_id+ " #"+node_id+ " #ipv6_address").val();//$('#ipv6_address'+i).val();
						
						//var cluster_member = $("#"+block_id+ " #"+node_id+ " #ipv6_address").val();//$('#cluster_member'+i).val();
						var cluster_member = 'true'
						// nodeObject['cluster_member'] = cluster_member;
				        if(cluster_member == 'true'){
						nodeObject['cluster_member'] = true;
                        }

                      else{
						nodeObject['cluster_member'] = false;
                        }

						//var ipmi_configure_now = $("#"+block_id+ " #"+node_id+ " #ipmi_configure_now").val();//$('#ipmi_configure_now'+i).val();
                        var ipmi_configure_now = 'false'
                        if(ipmi_configure_now == 'true'){
						nodeObject['ipmi_configure_now'] = true;
                        }

                        if(ipmi_configure_now == 'false'){
						nodeObject['ipmi_configure_now'] = false;
                        }
						//var ipv6_interface = $('#ipv6_interface'+i).val();
						//nodeObject['ipv6_interface'] = $("#"+block_id+ " #"+node_id+ " #ipv6_interface").val();//$('#ipv6_interface'+i).val();
						nodeObject['ipv6_interface'] = "";

						//var node_position = $('#node_position'+i).val();
						nodeObject['node_position'] = $("#"+block_id+ " #"+node_id+ " #nodePosition").val();//nodePosition// $('#node_position'+i).val();
						
						var image_now = $("#"+block_id+ " #"+node_id+ " #image_now").val();//$('#image_now'+i).val();
                        if(image_now == 'false'){
                            nodeObject['image_now'] = false;
                        }
                        if(image_now == 'true'){
                            nodeObject['image_now'] = true;
                        }

						var image_successful =$("#"+block_id+ " #"+node_id+ " #image_successful").val();// $('#image_successful'+i).val();
						if(image_successful == ""){
							nodeObject['image_successful'] = null;
						}
						else{
							nodeObject['image_successful'] = image_successful;

						}
						var ipmi_configured = $("#"+block_id+ " #"+node_id+ " #ipmi_configured").val();//$('#ipmi_configured'+i).val();
						//nodeObject['ipmi_configured'] = ipmi_configured;							
						 if(ipmi_configured == 'false'){
                            nodeObject['ipmi_configured'] = false;
                        }
                        if(ipmi_configured == 'true'){
                            nodeObject['ipmi_configured'] = true;
                        }
						
						nodes.push(nodeObject);
                          j = j + 1;
                    })
               
					mainblock['nodes'] = nodes;
					mainblock['model'] = "undefined";
					mainblock['block_id'] = "Block-"+i;	
                    i = i + 1;
                     });
					blocks.push(mainblock);
					foundationObject['blocks'] = blocks ;
					
					
					restInput['restInput'] = foundationObject;
					restInput['server'] = $('#foundation_server_ip').val();
					main_rest_block['foundation'] = restInput;
			
		//	if($('#prism').prop('checked')) {
				var prismObject = {};
					var authentication = {};
					var container = {};
					var storagepool = {};

					prismObject['restURL'] = $('#restURL').val();
					authentication['username'] = $('#pusername').val();
					authentication['password'] = $('#ppassword').val();
					prismObject['authentication'] = authentication;

					container['name'] = $('#container_name').val();
					prismObject['container'] = container;
					
					storagepool['name'] = $('#storagepool_name').val();
					prismObject['storagepool'] = storagepool;
					main_rest_block['prismDetails'] = prismObject;


		//	}
		//	if($('#vcenter').prop('checked')) {
			

					var vCenterObject = {};
					
					vCenterObject['host'] = $('#v_center_host').val();
					vCenterObject['user'] = $('#v_center_user').val();
					vCenterObject['password'] = $('#v_center_password').val();
					vCenterObject['port'] = $('#vcenter_port').val();
					
					vCenterObject['datacenter'] = $('#v_center_datacenter').val();
					vCenterObject['cluster'] = $('#v_center_cluster').val();
					vCenterObject['datacenter_reuse_if_exist'] = $('#v_center_datacenter_reuse').val();
					vCenterObject['cluster_reuse_if_exist'] = $('#v_center_cluster_reuse').val();
					


					vCenterObject['hosts'] = hosts;
					main_rest_block['vCenterConf'] = vCenterObject;
		//	}
		//		console.log(JSON.stringify(main_rest_block)); 
            
                var customerId = $("#customerId").val();
                createCustomerTask(customerId,main_rest_block);
		
	});
    
    /*Predeployer Submit Ends*/
    
    
    $(".startDeploymentBtn").click(function(){
        $(".pageloader").show();
		var customerId = $("#customerId").val();
        var taskId = $("#task_id").val();

        var checkValues = [];
        checked = $('input[name=deployment_type]:checked');
        if( checked.length > 0 ) {
             checkValues = checked.map(function(){
                return $(this).val();
            }).get();        
        }

        startDeployment(customerId, taskId,checkValues);
    //    startDeployment(customerId, "29",checkValues);
	});
    
    var interval = null;
    function startDeployment(customerId, taskId,checkValues){
        var post_data = {};
        post_data["customer_id"] = customerId;
        post_data["task_id"] =taskId;
        post_data["module_id"] ="foundation";

       

        if (checkValues.indexOf("foundation") > -1) {
            console.log(JSON.stringify(checkValues));
            
            	$.ajax({
                     type: "POST",
                     url: "/v1/deployer/action/",
                     async: false,
                     dataType: "json",
                     data:JSON.stringify(post_data),
                     success: function(data){
                        //alert(data);
                     },
                     error: function(request,status,errorThrown){
                         alert("No Data Available");
                     }
                });	


                $(".pageloader").fadeOut("slow");
                deployementStatus(customerId, taskId,checkValues);
                interval = setInterval(function(){
                    deployementStatus(customerId, taskId,checkValues); // this will run after every 10 seconds
                }, 10000);
            
        }
        
        
        if (checkValues.indexOf("vcenter") > -1 && checkValues.indexOf("foundation") == -1 ) {
                post_data["module_id"] ="vcenter";
                $.ajax({
                     type: "POST",
                     url: "/v1/deployer/action/",
                     async: false,
                     dataType: "json",
                     data:JSON.stringify(post_data),
                     success: function(data){
                        //alert(data);
                     },
                     error: function(request,status,errorThrown){
                         alert("No Data Available");
                     }
                });	 
               $(".pageloader").fadeOut("slow");
                deployementStatus(customerId, taskId,checkValues);
                /*interval = setInterval(function(){
                    deployementStatus(customerId, taskId,checkValues); // this will run after every 10 seconds
                }, 10000);*/

        }
        
        

        

	}
    var completeTask = false;
    
    var prismCheck = false;
    var vcenterCheck = false;
    function deployementStatus(customerId, taskId,checkValues){
        
        $.ajax({
			 type: "GET",
			 url: "/v1/deployer/customers/"+customerId+"/tasks/"+taskId+"/status/",
			 async: false,
			 dataType: "json",
             success: function(data){
                 for (var i = 0; i < data.task_status.length; i++) {
                    if(data.task_status[i].module == "foundation"){
                        $("#foundationStatus .progressPercentage").html(data.task_status[i].status);
                        if(data.task_status[i].status == "100.0%" && !completeTask){
                    
                      //  clearInterval(interval);
    
                         if (checkValues.indexOf("prism") > -1) {    
                            var post_data = {};
                            post_data["customer_id"] = customerId;
                            post_data["task_id"] =taskId;
                            post_data["module_id"] ="prism";
                            $.ajax({
                                 type: "POST",
                                 url: "/v1/deployer/action/",
                                 async: false,
                                 dataType: "json",
                                 data:JSON.stringify(post_data),
                                 success: function(data){
                                    //alert(data);
                                     completeTask = true;
                                     prismCheck = true;
                                 },
                                 error: function(request,status,errorThrown){
                                     alert("No Data Available");
                                 }
                            });	

                        }
                         if (checkValues.indexOf("vcenter") > -1) {
                            post_data["module_id"] ="vcenter";
                            $.ajax({
                                 type: "POST",
                                 url: "/v1/deployer/action/",
                                 async: false,
                                 dataType: "json",
                                 data:JSON.stringify(post_data),
                                 success: function(data){
                                    //alert(data);
                                     completeTask = true;
                                     vcenterCheck = true;
                                 },
                                 error: function(request,status,errorThrown){
                                     alert("No Data Available");
                                 }
                            });	     

                         }
                            
                            
                            $("#foundationStatus .status").removeClass("progressActiveSec").addClass("taskCompleted").append("<i class='fa fa-check-square'></i>");
                            $("#foundationStatus .statusMessage").html("Setup Completed...");
                        }else{
                            $("#foundationStatus .status").html("");
                            $("#foundationStatus .status").removeClass("taskCompleted").addClass("progressActiveSec");
                            $("#foundationStatus .statusMessage").html("Setup InProgress...");
                        }
                    }
                      if(data.task_status[i].module == "prism" && prismCheck){
                        $("#prismStatus .progressPercentage").html(data.task_status[i].status);
                        if(data.task_status[i].status == "Failed"){
                            $("#prismStatus .status").html("");
                            $("#prismStatus .status").removeClass("progressActiveSec").addClass("taskError").append("<i class='fa fa-exclamation-triangle'></i>");
                            $("#prismStatus .statusMessage").html("Setup Failed...");
                        }else if(data.task_status[i].status == "Completed"){
                            $("#prismStatus .status").html("");
                            $("#prismStatus .status").removeClass("progressActiveSec").addClass("taskCompleted").append("<i class='fa fa-check-square'></i>");
                            $("#prismStatus .statusMessage").html("Setup Completed...");
                        }else{
                            $("#prismStatus .status").html("");
                            $("#prismStatus .status").addClass("progressActiveSec");
                            $("#prismStatus .statusMessage").html("Setup InProgress...");
                        }
                    }
                     
                     if(data.task_status[i].module == "vcenter" && vcenterCheck){
                        $("#vcenterStatus .progressPercentage").html(data.task_status[i].status);
                        if(data.task_status[i].status == "Failed"){
                            $("#vcenterStatus .status").html("");
                            $("#vcenterStatus .status").removeClass("progressActiveSec").addClass("taskError").append("<i class='fa fa-exclamation-triangle'></i>");
                            $("#vcenterStatus .statusMessage").html("Setup Failed...");
                        }else if(data.task_status[i].status == "Completed"){

                            $("#vcenterStatus .status").removeClass("progressActiveSec").addClass("taskCompleted").append("<i class='fa fa-check-square'></i>");
                            $("#vcenterStatus .statusMessage").html("Setup Completed...");
                        }else{
                            $("#vcenterStatus .status").html("");
                            $("#vcenterStatus .status").addClass("progressActiveSec");
                            $("#vcenterStatus .statusMessage").html("Setup InProgress...");
                        }
                    }
                 }
			 },
			 error: function(request,status,errorThrown){
				 alert("No Data Available");
			 }
		});	
    }
    
});