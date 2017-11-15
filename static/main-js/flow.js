function deleteOperation(){
    $('#content').flowchart('deleteSelected');
}

function showProperties(){
    var id = $('#content').flowchart('getSelectedOperatorId');
    alert(id);
}

$(document).ready(function(){
    $('#content').flowchart({
        onOperatorSelect: function (operatorId) {
            if(metadata[operatorId]['type'] == 'input'){
                showConfigFile(operatorId);
            }else if(metadata[operatorId]['type'] == 'process:delete'){
                showDeleteQuery(operatorId);
            }else if(metadata[operatorId]['type'] == 'process:filter'){
                showFilterQuery(operatorId);
            }else if(metadata[operatorId]['type'] == 'process:join'){
                showJoinQuery(operatorId);
            }else if(metadata[operatorId]['type'] == 'process:append'){
                showAppendData(operatorId);
            }else if(metadata[operatorId]['type'] == 'process:cfilter'){
                showColumnFilter(operatorId);
            }else if(metadata[operatorId]['type'] == 'process:aggregate'){
                showAggregate(operatorId);
            }
            return true;
        },
        onLinkCreate: function (linkId, linkData) {
            if(metadata[linkData['toOperator']]['type'] == 'process:delete' || metadata[linkData['toOperator']]['type'] == 'process:filter'){
                $.ajax({
                    type: "POST",
                    contentType: "application/json; charset=utf-8",
                    url: "/api/query/metadata",
                    data: JSON.stringify({'data': metadata[linkData['fromOperator']]['shape']}),
                    success: function (res) {
                        metadata[linkData['toOperator']]['query_metadata'] = res;
                        metadata[linkData['fromOperator']]['link'].push(linkData['toOperator']);
                        metadata[linkData['toOperator']]['shape'] = metadata[linkData['fromOperator']]['shape'];
                    },
                    dataType: "json"
                });
            }else if(metadata[linkData['toOperator']]['type'] == 'process:join' || metadata[linkData['toOperator']]['type'] == 'process:append'){
              metadata[linkData['toOperator']]['input_metadata'].push({
                'operator': linkData['fromOperator'],
                'shape': metadata[linkData['fromOperator']]['shape'],
                'link_id': linkId
              });
              metadata[linkData['fromOperator']]['link'].push(linkData['toOperator']);
              metadata[linkData['toOperator']]['shape'] = metadata[linkData['fromOperator']]['shape'];
            }else if(metadata[linkData['toOperator']]['type'] == 'process:cfilter' || metadata[linkData['toOperator']]['type'] == 'process:aggregate'){
                metadata[linkData['toOperator']]['input_shape'] = metadata[linkData['fromOperator']]['shape']; 
            }
            return true;
        },
        onLinkDelete: function (linkId, forced) {
            var data = $("#content").flowchart('getData');
            var link = data['links'][linkId];
            var index = metadata[link['fromOperator']]['link'].indexOf(link['toOperator']);
            metadata[link['fromOperator']]['link'].splice(index, 1);
            if(metadata[link['toOperator']]['type'] == 'process:delete' || metadata[link['toOperator']]['type'] == 'process:filter'){
                metadata[link['toOperator']]['query_metadata'] = [];
            }else if(metadata[link['toOperator']]['type'] == 'process:join' || metadata[link['toOperator']]['type'] == 'process:append'){
                var target = -1;
                metadata[link['toOperator']]['input_metadata'].forEach(function(item, index){
                  if(item['link_id'] == linkId){
                    target = index;
                  }
                });
                link['toOperator']['input_metadata'].splice(target, 1);
                if(metadata[link['toOperator']]['type'] == 'process:join'){
                    link['toOperator']['metadata'] = {};
                }
            }else if(metadata[link['toOperator']]['type'] == 'process:cfilter'){
                metadata[link['toOperator']]['input_shape'] = {};
            }
            metadata[link['toOperator']]['shape'] = {};
            return true;
        }
    });

    $("#addFile").click(function(){
        $("#addFileModal").modal();
    });

    $('html').keyup(function(e){
        if(e.keyCode == 46) {
            deleteOperation();
        }
    });
    $("#columns-group-by").select2();
});


var operatorI = 0;
var metadata = {};
var host = "http://127.0.0.1:5000";

function addFile(filename){
    var operatorId = 'created_operator_' + operatorI;
    var operatorData = {
        top: 60,
        left: 500,
        properties: {
            title: filename,
            outputs: {
                output_1: {
                    label: 'Output',
                }
            }
        }
    };

    operatorI++;

    $('#content').flowchart('createOperator', operatorId, operatorData);
    return operatorId;
}

function addOperatorSingleInput(operatorName){
    var operatorId = 'created_operator_' + operatorI;
    var operatorData = {
        top: 60,
        left: 500,
        properties: {
            title: operatorName,
            outputs: {
                output_1: {
                    label: 'Output',
                }
            },
            inputs: {
                input_1: {
                    label: 'Input',
                }
            }
        }
    };

    operatorI++;

    $('#content').flowchart('createOperator', operatorId, operatorData);
    return operatorId;
}

function addModel(modelName){
    var operatorId = 'created_operator_' + operatorI;
    var operatorData = {
        top: 60,
        left: 500,
        properties: {
            title:  modelName,
            outputs: {

            },
            inputs: {
                input_1: {
                    label: 'Input',
                }
            }
        }
    };

    operatorI++;

    $('#content').flowchart('createOperator', operatorId, operatorData);

    }

function addOperatorTwoInput(operatorName){
    var operatorId = 'created_operator_' + operatorI;
    var operatorData = {
        top: 60,
        left: 500,
        properties: {
            title:  operatorName,
            outputs: {
                output_1: {
                    label: 'Output',
                }
            },
            inputs: {
                input_1: {
                    label: 'Input',
                },
                input_2: {
                    label: 'Input'
                }
            }
        }
    };

    operatorI++;

    $('#content').flowchart('createOperator', operatorId, operatorData);
    return operatorId;
    }

function addFileProcedure(){
    var fileid = $("#file").val();
    var filename = $("#file :selected").text();
    var id = addFile(filename);
    var data_shape = {};
    $.get("/api/file/metadata/" + fileid, {}, function(res){
        data_shape = res;
        var data = {
            id_operation: id,
            type: 'input',
            name: filename,
            file_id: fileid,
            shape: data_shape,
            link: []
        };
        metadata[id] = data;
        $('#addFileModal').modal('hide');
        $("#file-output-feet").val(1);
    });
}

function deleteProcedure(){
    var id = addOperatorSingleInput('Delete Module');
    var data = {
        id_operation: id,
        type: 'process:delete',
        name: 'delete',
        query: {},
        query_metadata: [],
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function filterProcedure(){
    var id = addOperatorSingleInput('Filter Module');
    var data = {
        id_operation: id,
        type: 'process:filter',
        name: 'filter',
        query: {},
        query_metadata: [],
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function joinProcedure(){
    var id = addOperatorTwoInput('Join Module');
    var data = {
        id_operation: id,
        type: 'process:join',
        name: 'join',
        metadata: {},
        input_metadata: [],
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function appendProcedure(){
    var id = addOperatorTwoInput('Append Module');
    var data = {
        id_operation: id,
        type: 'process:append',
        name: 'append',
        input_metadata: [],
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function columnFilterProcedure(){
    var id = addOperatorSingleInput('Column Filter Module');
    var data = {
        id_operation: id,
        type: 'process:cfilter',
        name: 'cfilter',
        input_shape: [],
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function aggregateProcedure(){
    var id = addOperatorSingleInput('Query Aggregation Module');
    var data = {
        id_operation: id,
        type: 'process:aggregate',
        name: 'aggregate',
        input_shape: [],
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function deleteModule(id_container, id_modal){
    var id = $("#" + id_container).val();
    $('#content').flowchart('deleteOperator', id);
    $("#"+id_modal).modal('toggle');
}

function showDeleteQuery(id){
    $("#delete-module-id").val(id);
    $("#delete-module-warning").hide();
    $("#delete-module-perform").show();
    if (metadata[id]['query_metadata'].length > 0){
        $('#query-builder-delete').queryBuilder({
            allow_empty: true,

            //default_filter: 'name',
            sort_filters: true,

            filters: metadata[id]['query_metadata']
        });
        if(!jQuery.isEmptyObject(metadata[id]['query'])){
          $('#query-builder-delete').queryBuilder('setRules', metadata[id]['query']);
        }else{
          $('#query-builder-delete').queryBuilder('setRules', {condition: "AND", rules: []});
        }
        $("#delete-module-warning").hide();
    }else{
        $("#delete-module-warning").show();
        $("#delete-module-perform").hide();
    }
    $("#deleteDataModal").modal();
}

function showFilterQuery(id){
    $("#filter-module-id").val(id);
    $("#filter-module-warning").hide();
    $("#filter-module-perform").show();
    if (metadata[id]['query_metadata'].length > 0){
        $('#query-builder-filter').queryBuilder({
            allow_empty: true,

            //default_filter: 'name',
            sort_filters: true,

            filters: metadata[id]['query_metadata']
        });
        if(!jQuery.isEmptyObject(metadata[id]['query'])){
          $('#query-builder-filter').queryBuilder('setRules', metadata[id]['query']);
        }else{
          $('#query-builder-filter').queryBuilder('setRules', {condition: "AND", rules: []});
        }
        $("#filter-module-warning").hide();
    }else{
        $("#filter-module-warning").show();
        $("#filter-module-perform").hide();
    }
    $("#filterDataModal").modal();
}

function showJoinQuery(id){
  $("#join-module-id").val(id);
  $("#join-module-warning").hide();
  $("#join-module-perform").show();
  if(metadata[id]['input_metadata'].length == 2){
    $("#left-join-dataset").empty();
    $("#right-join-dataset").empty();

    $.each(metadata[id]['input_metadata'][0]['shape'], function(index, value){
      $('#left-join-dataset').append($('<option>', {
        value: index,
        text: index
      }));
    });

    $.each(metadata[id]['input_metadata'][1]['shape'], function(index, value){
      $('#right-join-dataset').append($('<option>', {
        value: index,
        text: index
      }));
    });

    $("#join-input-left").show();
    $("#join-input-right").show();
    $("#join-input-how").show();
    $("#join-module-warning").show();
  }else{
    $("#join-module-warning").show();
    $("#join-module-perform").hide();
    $("#join-input-left").hide();
    $("#join-input-right").hide();
    $("#join-input-how").hide();
  }
  $("#joinDataModal").modal();
}

function showConfigFile(id){
    var filename = metadata[id]['name'];
    $("#config-file-name").html(filename);
    $("#config-file-id").val(id);
    $("#configFileModal").modal();
}

function showAppendData(id){
    $("#config-file-id").val(id);
    $("#appendDataModal").modal();
}

function showColumnFilter(id){
    $("#column-filter-id").val(id);
    if (!jQuery.isEmptyObject(metadata[id]['input_shape'])){
        $("#column-picker").html("");
        $.each(metadata[id]['input_shape'], function(index, value){
            $("#column-picker").append(
                '<label class="custom-control custom-checkbox"><input type="checkbox" class="custom-control-input" name="columns[]" value="' + index + '" checked><span class="custom-control-indicator"></span><span class="custom-control-description">' + index + '</span></label><br>'
            );
        });
        $("#column-filter-module-warning").hide();
    }else{
        $("#column-filter-module-warning").show();
        $("#column-filter-module-perform").hide();
    }
    $("#columnFilterModal").modal();
}

function showAggregate(id){
    $.each(metadata[id]['input_shape'], function(index, value){
        $("#columns-group-by").append('<option value="' + index + '">' + index + '</option>');
        $("#column-aggregate").append('<option value="' + index + '">' + index + '</option>');
    });
    $("#queryAggregateModal").modal();
}

function remakeOutputFeet(id, output_feet){
  var data = $('#content').flowchart('getData');
  var new_feet = {};
  for(var i = 0; i < output_feet; i++){
      new_feet['output_' + (i + 1)] = {'label': 'Output'}
  }
  var link = [];
  $.each(data['links'], function(index, item){
    if(item['fromOperator'] == id){
      link.push({
        "id": index,
        "value": item
      });
    }
  });
  data['operators'][id]['properties']['outputs'] = new_feet;
  $('#content').flowchart('deleteOperator', id);
  $('#content').flowchart('createOperator', id, data['operators'][id]);
  link.forEach(function(item, index){
    $('#content').flowchart('createLink', item['id'], item['value']);
  });
}

function updateConfigFile(){
    var id = $("#config-file-id").val();
    var output_feet = $("#file-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#configFileModal").modal('hide');
}

function performDeleteModule(){
    var id = $("#delete-module-id").val();
    var result = $('#query-builder-delete').queryBuilder('getRules', {
      get_flags: true,
      skip_empty: true
    });

    if (!$.isEmptyObject(result)) {
      metadata[id]['query'] = result;
    }
    $("#deleteDataModal").modal('hide');
}

function performFilterModule(){
    var id = $("#filter-module-id").val();
    var result = $('#query-builder-filter').queryBuilder('getRules', {
      get_flags: true,
      skip_empty: true
    });

    if (!$.isEmptyObject(result)) {
      metadata[id]['query'] = result;
    }
    $("#filterDataModal").modal('hide');
}

function performJoinModule(){
    var id = $("#join-module-id").val();
    var how = $("#how").val();
    var left = $("#left-join-dataset").val();
    var right = $("#right-join-dataset").val();
    metadata[id]['metadata'] = {
        how: how,
        left: left,
        right: right
    };
    $("#joinDataModal").modal('hide');
}

function performColumnFilterModule(){
    var id = $("#column-filter-id").val();
    var column_list = {};
    $("input[name='columns[]']:checked").each( function () {
        
        column_list[$(this).val()] = metadata[id]['input_shape'][$(this).val()];
    });
    metadata[id]['shape'] = column_list;
    $("#columnFilterModal").modal('hide');
}