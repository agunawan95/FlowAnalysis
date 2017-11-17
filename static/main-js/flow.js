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
            }else if(metadata[operatorId]['type'] == 'process:sextract'){
                showStringExtract(operatorId);
            }else if(metadata[operatorId]['type'] == 'process:fillna-aggregate'){
                showFillnaAggregate(operatorId);
            }else if(metadata[operatorId]['type'] == 'process:fillna-oc'){
                showFillnaOC(operatorId);
            }else if(metadata[operatorId]['type'] == 'process:fillna-value'){
                showFillnaValue(operatorId);
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
            }else if(metadata[linkData['toOperator']]['type'] == 'process:cfilter' || metadata[linkData['toOperator']]['type'] == 'process:aggregate' || metadata[linkData['toOperator']]['type'] == 'process:sextract' || metadata[linkData['toOperator']]['type'] == 'process:fillna-aggregate' || metadata[linkData['toOperator']]['type'] == 'process:fillna-oc' || metadata[linkData['toOperator']]['type'] == 'process:fillna-value'){
                metadata[linkData['toOperator']]['input_shape'] = metadata[linkData['fromOperator']]['shape']; 
            }
            return true;
        },
        onLinkDelete: function (linkId, forced) {
            var data = $("#content").flowchart('getData');
            var link = data['links'][linkId];
            if(!(link['toOperator'] in metadata)){
                return true;
            }
            if(!(link['fromOperator'] in metadata)){
                return true;
            }
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
            }else if(metadata[link['toOperator']]['type'] == 'process:cfilter' || metadata[link['toOperator']]['type'] == 'process:aggregate' || metadata[link['toOperator']]['type'] == 'process:sextract' || metadata[link['toOperator']]['type'] == 'process:fillna-aggregation' || metadata[link['toOperator']]['type'] == 'process:fillna-oc' || metadata[link['toOperator']]['type'] == 'process:fillna-value'){
                metadata[link['toOperator']]['input_shape'] = {};
            }
            metadata[link['toOperator']]['shape'] = {};
            return true;
        },
        onOperatorDelete: function (operatorId) {
            delete metadata[operatorId];
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
        group_by: "",
        function: "",
        target: "",
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function stringExtractProcedure(){
    var id = addOperatorSingleInput('String Extract Module');
    var data = {
        id_operation: id,
        type: 'process:sextract',
        name: 'aggregate',
        input_shape: [],
        delimiter: "",
        target: "",
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function fillnaAggregateProcedure(){
    var id = addOperatorSingleInput('Fill NA Aggregate Module');
    var data = {
        id_operation: id,
        type: 'process:fillna-aggregate',
        name: 'fillna-aggregate',
        input_shape: [],
        function: "",
        target: "",
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function fillnaOCProcedure(){
    var id = addOperatorSingleInput('Fill NA With Other Column Module');
    var data = {
        id_operation: id,
        type: 'process:fillna-oc',
        name: 'fillna-oc',
        input_shape: [],
        other: "",
        target: "",
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function fillnaValueProcedure(){
    var id = addOperatorSingleInput('Fill NA With Value Module');
    var data = {
        id_operation: id,
        type: 'process:fillna-value',
        name: 'fillna-value',
        input_shape: [],
        value: "",
        target: "",
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
    var data = $("#content").flowchart('getData');
    $("#delete-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
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
    var data = $("#content").flowchart('getData');
    $("#filter-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
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
  var data = $("#content").flowchart('getData');
  $("#join-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
  $("#joinDataModal").modal();
}

function showConfigFile(id){
    var filename = metadata[id]['name'];
    $("#config-file-name").html(filename);
    $("#config-file-id").val(id);
    var data = $("#content").flowchart('getData');
    $("#file-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
    $("#configFileModal").modal();
}

function showAppendData(id){
    $("#append-file-id").val(id);
    $("#appendDataModal").modal();
    var data = $("#content").flowchart('getData');
    $("#append-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
}

function showColumnFilter(id){
    $("#column-filter-id").val(id);
    if (!jQuery.isEmptyObject(metadata[id]['input_shape'])){
        $("#column-picker").html("");
        $.each(metadata[id]['input_shape'], function(index, value){
            if(!jQuery.isEmptyObject(metadata[id]['shape']) && !(index in metadata[id]['shape'])){
                $("#column-picker").append(
                    '<label class="custom-control custom-checkbox"><input type="checkbox" class="custom-control-input" name="columns[]" value="' + index + '"><span class="custom-control-indicator"></span><span class="custom-control-description">' + index + '</span></label><br>'
                );
            }else{
                $("#column-picker").append(
                    '<label class="custom-control custom-checkbox"><input type="checkbox" class="custom-control-input" name="columns[]" value="' + index + '" checked><span class="custom-control-indicator"></span><span class="custom-control-description">' + index + '</span></label><br>'
                );
            }
        });
        $("#column-filter-module-warning").hide();
    }else{
        $("#column-filter-module-warning").show();
        $("#column-filter-module-perform").hide();
    }
    var data = $("#content").flowchart('getData');
    $("#column-filter-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
    $("#columnFilterModal").modal();
}

function showAggregate(id){
    $("#aggregate-id").val(id);
    if (!jQuery.isEmptyObject(metadata[id]['input_shape'])){
        $("#columns-group-by").html("");
        $("#column-aggregate").html("");
        $.each(metadata[id]['input_shape'], function(index, value){
            $("#columns-group-by").append('<option value="' + index + '">' + index + '</option>');
            $("#column-aggregate").append('<option value="' + index + '">' + index + '</option>');
        });

        if(metadata[id]['target'] != ''){
            $("#column-aggregate option:selected").removeAttr("selected");
            $('#column-aggregate option[value=' + metadata[id]['target'] + ']').attr('selected','selected');
        }

        if(metadata[id]['function'] != ''){
            $("#function-aggregate option:selected").removeAttr("selected");
            $('#function-aggregate option[value=' + metadata[id]['target'] + ']').attr('selected','selected');
        }

        if(metadata[id]['group_by'] != ''){
            $('#columns-group-by').val(metadata[id]['group_by']);
        }

        $("#aggregate-module-warning").hide();
        $("#aggregate-body").show();
    }else{
        $("#aggregate-module-warning").show();
        $("#aggregate-module-perform").hide();
        $("#aggregate-body").hide();
    }
    var data = $("#content").flowchart('getData');
    $("#aggregate-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
    $("#queryAggregateModal").modal();
}

function showStringExtract(id){
    $("#string-extract-id").val(id);
    
    if (!jQuery.isEmptyObject(metadata[id]['input_shape'])){
        $("#string-extract-column").html("");
        $.each(metadata[id]['input_shape'], function(index, value){
            $("#string-extract-column").append('<option value="' + index + '">' + index + '</option>');
        });

        if(metadata[id]['target'] != ''){
            $("#string-extract-column option:selected").removeAttr("selected");
            $('#string-extract-column option[value=' + metadata[id]['target'] + ']').attr('selected','selected');
        }

        if(metadata[id]['delimiter'] != ''){
            $("#delimiter").val(metadata[id]['delimiter']);
        }

        $("#string-extract-module-warning").hide();
        $("#extract-body").show();
    }else{
        $("#aggregate-module-warning").show();
        $("#string-extreact-module-perform").hide();
        $("#extract-body").hide();
    }
    var data = $("#content").flowchart('getData');
    $("#string-extract-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
    $("#stringExtractModal").modal();
}   

function showFillnaAggregate(id){
    $("#fillna-aggregate-id").val(id);
    
    if (!jQuery.isEmptyObject(metadata[id]['input_shape'])){
        $("#fillna-aggregate-column").html("");
        $.each(metadata[id]['input_shape'], function(index, value){
            $("#fillna-aggregate-column").append('<option value="' + index + '">' + index + '</option>');
        });

        if(metadata[id]['target'] != ''){
            $("#fillna-aggregate-column option:selected").removeAttr("selected");
            $('#fillna-aggregate-column option[value=' + metadata[id]['target'] + ']').attr('selected','selected');
        }

        if(metadata[id]['function'] != ''){
            $('#fillna-aggregate-function option[value=' + metadata[id]['function'] + ']').attr('selected','selected');
        }

        $("#fillna-aggregate-module-warning").hide();
        $("#fillna-aggregate-body").show();
    }else{
        $("#fillna-aggregate-module-warning").show();
        $("#fillna-aggregate-module-perform").hide();
        $("#fillna-aggregate-body").hide();
    }
    var data = $("#content").flowchart('getData');
    $("#fillna-aggregate-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
    $("#fillnaAggregateModal").modal();
}   

function showFillnaOC(id){
    $("#fillna-oc-id").val(id);
    
    if (!jQuery.isEmptyObject(metadata[id]['input_shape'])){
        $("#fillna-oc-column").html("");
        $("#fillna-oc-ocolumn").html("");
        $.each(metadata[id]['input_shape'], function(index, value){
            $("#fillna-oc-column").append('<option value="' + index + '">' + index + '</option>');
            $("#fillna-oc-ocolumn").append('<option value="' + index + '">' + index + '</option>');
        });

        if(metadata[id]['target'] != ''){
            $("#fillna-oc-column option:selected").removeAttr("selected");
            $('#fillna-oc-column option[value=' + metadata[id]['target'] + ']').attr('selected','selected');
        }

        if(metadata[id]['other'] != ''){
            $("#fillna-oc-ocolumn option:selected").removeAttr("selected");
            $('#fillna-oc-ocolumn option[value=' + metadata[id]['other'] + ']').attr('selected','selected');
        }

        $("#fillna-oc-module-warning").hide();
        $("#fillna-oc-body").show();
    }else{
        $("#fillna-oc-module-warning").show();
        $("#fillna-oc-module-perform").hide();
        $("#fillna-oc-body").hide();
    }
    var data = $("#content").flowchart('getData');
    $("#fillna-oc-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
    $("#fillnaOCModal").modal();
}

function showFillnaValue(id){
    $("#fillna-value-id").val(id);
    
    if (!jQuery.isEmptyObject(metadata[id]['input_shape'])){
        $("#fillna-value-column").html("");
        $.each(metadata[id]['input_shape'], function(index, value){
            $("#fillna-value-column").append('<option value="' + index + '">' + index + '</option>');
        });

        if(metadata[id]['target'] != ''){
            $("#fillna-value-column option:selected").removeAttr("selected");
            $('#fillna-value-column option[value=' + metadata[id]['target'] + ']').attr('selected','selected');
        }

        if(metadata[id]['value'] != ''){
            $("#fillna-value-val").val(metadata[id]['value']);
        }

        $("#fillna-value-module-warning").hide();
        $("#fillna-value-body").show();
    }else{
        $("#fillna-value-module-warning").show();
        $("#fillna-value-module-perform").hide();
        $("#fillna-value-body").hide();
    }
    var data = $("#content").flowchart('getData');
    $("#fillna-value-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
    $("#fillnaValueModal").modal();
}

function remakeOutputFeet(id, output_feet){
  var data = $('#content').flowchart('getData');
  var new_feet = {};
  for(var i = 0; i < output_feet; i++){
      new_feet['output_' + (i + 1)] = {'label': 'Output'}
  }
  var link = [];
  $.each(data['links'], function(index, item){
    if(item['fromOperator'] == id || item['toOperator'] == id){
      link.push({
        "id": index,
        "value": item
      });
    }
  });
  data['operators'][id]['properties']['outputs'] = new_feet;
  tmp_metadata = metadata[id];
  if(tmp_metadata['type'] == 'process:join'){
      tmp_metadata['input_metadata'] = [];
  }
  $('#content').flowchart('deleteOperator', id);
  $('#content').flowchart('createOperator', id, data['operators'][id]);
  metadata[id] = tmp_metadata;
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
    var output_feet = $("#delete-output-feet").val();
    remakeOutputFeet(id, output_feet);
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
    var output_feet = $("#filter-output-feet").val();
    remakeOutputFeet(id, output_feet);
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
    var output_feet = $("#join-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#joinDataModal").modal('hide');
}

function performAppendModule(){
    var id = $("#append-file-id").val();
    var output_feet = $("#append-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#appendDataModal").modal('hide');
}

function performColumnFilterModule(){
    var id = $("#column-filter-id").val();
    var column_list = {};
    $("input[name='columns[]']:checked").each( function () {
        column_list[$(this).val()] = metadata[id]['input_shape'][$(this).val()];
    });
    metadata[id]['shape'] = column_list;
    var output_feet = $("#column-filter-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#columnFilterModal").modal('hide');
}

function performAggregateModule(){
    var id = $("#aggregate-id").val();
    var group_by = $("#columns-group-by").val();
    if (group_by != null){
        group_by = group_by.toString();
    }else{
        group_by = "";
    }
    var f = $("#aggregate-function").val();
    var target = $("#column-aggregate").val();
    metadata[id]["group_by"] = group_by;
    metadata[id]["target"] = target;
    metadata[id]["function"] = f;
    var output_feet = $("#aggregate-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#queryAggregateModal").modal('hide');
}

function performFillnaAggregateModule(){
    var id = $("#fillna-aggregate-id").val();
    var target = $("#fillna-aggregate-column").val();
    var f = $("#fillna-aggregate-function").val();
    metadata[id]["target"] = target;
    metadata[id]["function"] = f;
    var output_feet = $("#fillna-aggregate-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#fillnaAggregateModal").modal('hide');
}

function performFillnaOCModule(){
    var id = $("#fillna-oc-id").val();
    var target = $("#fillna-oc-column").val();
    var other = $("#fillna-oc-ocolumn").val();
    metadata[id]["target"] = target;
    metadata[id]["other"] = other;
    var output_feet = $("#fillna-oc-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#fillnaOCModal").modal('hide');
}

function performFillnaValueModule(){
    var id = $("#fillna-value-id").val();
    var target = $("#fillna-value-column").val();
    var value = $("#fillna-value-val").val();
    metadata[id]["target"] = target;
    metadata[id]["value"] = value;
    var output_feet = $("#fillna-value-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#fillnaValueModal").modal('hide');
}

function stringExtractPerform(){
    var id = $("#string-extract-id").val();
    var target = $("#string-extract-column").val();
    var delimiter = $("#delimiter").val();
    metadata[id]['target'] = target;
    metadata[id]['delimiter'] = delimiter;
    var output_feet = $("#string-extract-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#stringExtractModal").modal('hide');
}