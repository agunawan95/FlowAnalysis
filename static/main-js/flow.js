function deleteOperation(){
    $('#content').flowchart('deleteSelected');
}

function showProperties(){
    var id = $('#content').flowchart('getSelectedOperatorId');
    alert(id);
}

var process_list = [
    {
        id: "filter-module",
        process_id: "process:filter",
        background: "bg-success",
        image: "img/query-filter.png",
        name: "Filter Module",
        type: "query",
        tag: "filter, query"
    },
    {
        id: "cfilter-module",
        process_id: "process:cfilter",
        background: "bg-success",
        image: "img/query-filter.png",
        name: "Column Filter Module",
        type: "query",
        tag: "column, filter, query"
    },
    {
        id: "delete-module",
        process_id: "process:delete",
        background: "bg-danger",
        image: "img/query-delete.png",
        name: "Delete Module",
        type: "query",
        tag: "delete, query"
    },
    {
        id: "update-module",
        process_id: "process:update-column",
        background: "bg-warning",
        image: "img/query-update.png",
        name: "Update Column Module",
        type: "query",
        tag: "update, column, query"
    },
    {
        id: "update-value-module",
        process_id: "process:update-value",
        background: "bg-warning",
        image: "img/query-update.png",
        name: "Update Column With Value Module",
        type: "query",
        tag: "update, value, query"
    },
    {
        id: "join-module",
        process_id: "process:join",
        background: "bg-dark",
        image: "img/query-join.png",
        name: "Join Data Module",
        type: "query",
        tag: "join, merge, query"
    },
    {
        id: "append-module",
        process_id: "process:append",
        background: "bg-dark",
        image: "img/query-append.png",
        name: "Append Module",
        type: "query",
        tag: "append, merge, query"
    },
    {
        id: "aggregate-module",
        process_id: "process:aggregate",
        background: "bg-success",
        image: "img/query-aggregate.png",
        name: "Aggregate Module",
        type: "query",
        tag: "aggregate, math, query"
    },
    {
        id: "formula-module",
        process_id: "process:formula",
        background: "bg-dark",
        image: "img/tool-formula.png",
        name: "Formula Module",
        type: "tool",
        tag: "formula, equation, math, tool"
    },
    {
        id: "fillna-aggregate-module",
        process_id: "process:fillna-aggregate",
        background: "bg-dark",
        image: "img/tool-fillna.png",
        name: "Fill NA With Aggregate",
        type: "tool",
        tag: "fillna, aggregate, tool"
    },
    {
        id: "fillna-oc-module",
        process_id: "process:fillna-oc",
        background: "bg-dark",
        image: "img/tool-fillna.png",
        name: "Fill NA With Other Column",
        type: "tool",
        tag: "fillna, column, tool"
    },
    {
        id: "fillna-value-module",
        process_id: "process:fillna-value",
        background: "bg-dark",
        image: "img/tool-fillna.png",
        name: "Fill NA With Value",
        type: "tool",
        tag: "fillna, value, tool"
    },
    {
        id: "factorize-module",
        process_id: "process:factorize",
        background: "bg-dark",
        image: "img/tool-factorize.png",
        name: "Factorize Module",
        type: "tool",
        tag: "factorize, transform, tool"
    },
    {
        id: "correlation-matrix-module",
        process_id: "chart:cm",
        background: "bg-dark",
        image: "img/chart-corr_matrix.png",
        name: "Correlation Matrix Module",
        type: "chart",
        tag: "correlation, matrix, chart"
    },
    {
        id: "decision-tree-module",
        process_id: "model:dt",
        background: "bg-dark",
        image: "img/model-tree.png",
        name: "Decision Tree Module",
        type: "model",
        tag: "decision, tree, model"
    }
];

function initDraggable(){
    $('.draggable').draggable({
        revert: "invalid",
        appendTo: 'body',
        stack: ".draggable",
        helper: 'clone'
    });
    $('.droppable').droppable({
        accept: ".draggable",
        drop: function (event, ui) {
            leftPosition  = ui.offset.left - $(this).offset().left;
            topPosition   = ui.offset.top - $(this).offset().top;
            var id = ui.draggable.attr("data-process");
            if(id == "process:delete"){
                deleteProcedure(leftPosition, topPosition);
            }else if(id == "process:filter"){
                filterProcedure(leftPosition, topPosition);
            }else if(id == "process:cfilter"){
                columnFilterProcedure(leftPosition, topPosition);
            }else if(id == "process:append"){
                appendProcedure(leftPosition, topPosition);
            }else if(id == "process:update-column"){
                updateColumnProcedure(leftPosition, topPosition);
            }else if(id == "process:update-value"){
                updateValueProcedure(leftPosition, topPosition);
            }else if(id == "process:join"){
                joinProcedure(leftPosition, topPosition);
            }else if(id == "process:aggregate"){
                aggregateProcedure(leftPosition, topPosition);
            }else if(id == "process:formula"){
                formulaProcedure(leftPosition, topPosition);
            }else if(id == "process:fillna-aggregate"){
                fillnaAggregateProcedure(leftPosition, topPosition);
            }else if(id == "process:fillna-oc"){
                fillnaOCProcedure(leftPosition, topPosition);
            }else if(id == "process:fillna-value"){
                fillnaValueProcedure(leftPosition, topPosition);
            }else if(id == "process:factorize"){
                factorizeProcedure(leftPosition, topPosition);
            }else if(id == "chart:cm"){
                correlationMatrixProcedure(leftPosition, topPosition);
            }else if(id == "model:dt"){
                decisionTreeProcedure(leftPosition, topPosition);
            }
        }
    });
}

function init_accordion(){
    $("#process-container").hide();
    $("#accordion").show();
    $("#query-content").html("");
    $("#tool-content").html("");
    $("#chart-content").html("");
    $("#model-content").html("");
    for(var i in process_list){
        data = process_list[i];
        if(data['type'] == 'query'){
            $("#query-content").append('<br><div class="card text-white ' + data['background'] + ' draggable" id="' + data['id'] + '" data-process="' + data['process_id'] + '"><div class="card-body"><div class="text-center"><img src="/static/' + data['image'] + '" alt="" width="32"><p style="font-size: 12px; margin:0;"> ' + data['name'] + '</p></div></div></div>');
        }else if(data['type'] == 'tool'){
            $("#tool-content").append('<br><div class="card text-white ' + data['background'] + ' draggable" id="' + data['id'] + '" data-process="' + data['process_id'] + '"><div class="card-body"><div class="text-center"><img src="/static/' + data['image'] + '" alt="" width="32"><p style="font-size: 12px; margin:0;"> ' + data['name'] + '</p></div></div></div>');
        }else if(data['type'] == 'chart'){
            $("#chart-content").append('<br><div class="card text-white ' + data['background'] + ' draggable" id="' + data['id'] + '" data-process="' + data['process_id'] + '"><div class="card-body"><div class="text-center"><img src="/static/' + data['image'] + '" alt="" width="32"><p style="font-size: 12px; margin:0;"> ' + data['name'] + '</p></div></div></div>');
        }else if(data['type'] == 'model'){
            $("#model-content").append('<br><div class="card text-white ' + data['background'] + ' draggable" id="' + data['id'] + '" data-process="' + data['process_id'] + '"><div class="card-body"><div class="text-center"><img src="/static/' + data['image'] + '" alt="" width="32"><p style="font-size: 12px; margin:0;"> ' + data['name'] + '</p></div></div></div>');
        }
    }
}

$(document).ready(function(){
    init_accordion();
    $("#process-search").keyup(function(){
        var str = $("#process-search").val();
        $("#process-container").html("");
        for(var i in process_list){
            data = process_list[i];
            if(data['tag'].indexOf(str) >= 0){
                $("#process-container").append('<div class="card text-white ' + data['background'] + ' draggable" id="' + data['id'] + '" data-process="' + data['process_id'] + '"><div class="card-body"><div class="text-center"><img src="/static/' + data['image'] + '" alt="" width="32"><p style="font-size: 12px; margin:0;"> ' + data['name'] + '</p></div></div></div><hr>');
            }
        }
        $("#process-container").show();
        $("#accordion").hide();
        if(str == ''){
            init_accordion();
        }
        initDraggable();
    });

    initDraggable();

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
            }else if(metadata[operatorId]['type'] == 'process:fillna-aggregate'){
                showFillnaAggregate(operatorId);
            }else if(metadata[operatorId]['type'] == 'process:fillna-oc'){
                showFillnaOC(operatorId);
            }else if(metadata[operatorId]['type'] == 'process:fillna-value'){
                showFillnaValue(operatorId);
            }else if(metadata[operatorId]['type'] == 'process:formula'){
                showFormulaModule(operatorId);
            }else if (metadata[operatorId]['type'] == 'process:factorize'){
                showFactorizeModule(operatorId);
            }else if(metadata[operatorId]['type'] == 'process:update-column'){
                showUpdateQuery(operatorId);
            }else if (metadata[operatorId]['type'] == 'process:update-value'){
                showUpdateValue(operatorId);
            }else if(metadata[operatorId]['type'] == 'model:dt'){
                showDecisionTreeModule(operatorId);
            }
            return true;
        },
        onLinkCreate: function (linkId, linkData) {
            if(metadata[linkData['toOperator']]['type'] == 'process:delete' || metadata[linkData['toOperator']]['type'] == 'process:filter' || metadata[linkData['toOperator']]['type'] == 'process:update-column' || metadata[linkData['toOperator']]['type'] == 'process:update-value'){
                $.ajax({
                    type: "POST",
                    contentType: "application/json; charset=utf-8",
                    url: "/api/query/metadata",
                    data: JSON.stringify({'data': metadata[linkData['fromOperator']]['shape']}),
                    success: function (res) {
                        metadata[linkData['toOperator']]['query_metadata'] = res;
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
              if(metadata[linkData['toOperator']]['type'] == 'process:append' && metadata[linkData['toOperator']]['input_metadata'].length == 2){
                var left_data = metadata[linkData['toOperator']]['input_metadata'][0]['shape'];
                var right_data = metadata[linkData['toOperator']]['input_metadata'][1]['shape'];
                var same = true;
            
                $.each(right_data, function(index, value){
                    if(!(index in left_data)){
                        same = false;
                    }
                });
            
                if(same){
                    metadata[linkData['toOperator']]['shape'] = left_data;
                }else{
                    // Error
                }
              }
              // metadata[linkData['toOperator']]['shape'] = metadata[linkData['fromOperator']]['shape'];
            }else if(metadata[linkData['toOperator']]['type'] == 'process:cfilter' || metadata[linkData['toOperator']]['type'] == 'process:aggregate' || metadata[linkData['toOperator']]['type'] == 'process:sextract' || metadata[linkData['toOperator']]['type'] == 'process:fillna-aggregate' || metadata[linkData['toOperator']]['type'] == 'process:fillna-oc' || metadata[linkData['toOperator']]['type'] == 'process:fillna-value' || metadata[linkData['toOperator']]['type'] == 'process:formula' || metadata[linkData['toOperator']]['type'] == 'process:factorize' || metadata[linkData['toOperator']]['type'] == 'process:cmerge' || metadata[linkData['toOperator']]['type'] == 'model:dt'){
                metadata[linkData['toOperator']]['input_shape'] = metadata[linkData['fromOperator']]['shape']; 
            }
            metadata[linkData['fromOperator']]['link'].push(linkData['toOperator']);
            return true;
        },
        onLinkDelete: function (linkId, forced) {
            var data = $("#content").flowchart('getData');
            var link = data['links'][linkId];
            if(!(link['toOperator'] in metadata)){
                var index = metadata[link['fromOperator']]['link'].indexOf(link['toOperator']);
                metadata[link['fromOperator']]['link'].splice(index, 1);
                return true;
            }
            if(!(link['fromOperator'] in metadata)){
                return true;
            }
            var index = metadata[link['fromOperator']]['link'].indexOf(link['toOperator']);
            metadata[link['fromOperator']]['link'].splice(index, 1);
            if(metadata[link['toOperator']]['type'] == 'process:delete' || metadata[link['toOperator']]['type'] == 'process:filter' || metadata[link['toOperator']]['type'] == 'process:update-column' || metadata[link['toOperator']]['type'] == 'process:update-value'){
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
            }else if(metadata[link['toOperator']]['type'] == 'process:cfilter' || metadata[link['toOperator']]['type'] == 'process:aggregate' || metadata[link['toOperator']]['type'] == 'process:sextract' || metadata[link['toOperator']]['type'] == 'process:fillna-aggregation' || metadata[link['toOperator']]['type'] == 'process:fillna-oc' || metadata[link['toOperator']]['type'] == 'process:fillna-value' || metadata[link['toOperator']]['type'] == 'process:formula' || metadata[link['toOperator']]['type'] == 'process:factorize' || metadata[link['toOperator']]['type'] == 'process:cmerge' || metadata[link['toOperator']]['type'] == 'model:dt'){
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

function addOperatorSingleInput(operatorName, left, top){
    var operatorId = 'created_operator_' + operatorI;
    var operatorData = {
        top: top,
        left: left,
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

function addOutputOperator(operatorName, left, top){
    var operatorId = 'created_operator_' + operatorI;
    var operatorData = {
        top: top,
        left: left,
        properties: {
            title:  operatorName,
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
    return operatorId;
    }

function addOperatorTwoInput(operatorName, left, top){
    var operatorId = 'created_operator_' + operatorI;
    var operatorData = {
        top: top,
        left: left,
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

function deleteProcedure(left, top){
    var id = addOperatorSingleInput('Delete Module', left, top);
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

function filterProcedure(left, top){
    var id = addOperatorSingleInput('Filter Module', left, top);
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

function joinProcedure(left, top){
    var id = addOperatorTwoInput('Join Module', left, top);
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

function appendProcedure(left, top){
    var id = addOperatorTwoInput('Append Module', left, top);
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

function columnFilterProcedure(left, top){
    var id = addOperatorSingleInput('Column Filter Module', left, top);
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

function aggregateProcedure(left, top){
    var id = addOperatorSingleInput('Query Aggregation Module', left, top);
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

function fillnaAggregateProcedure(left, top){
    var id = addOperatorSingleInput('Fill NA Aggregate Module', left, top);
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

function fillnaOCProcedure(left, top){
    var id = addOperatorSingleInput('Fill NA With Other Column Module', left, top);
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

function fillnaValueProcedure(left, top){
    var id = addOperatorSingleInput('Fill NA With Value Module', left, top);
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

function formulaProcedure(left, top){
    var id = addOperatorSingleInput('Formula Module', left, top);
    var data = {
        id_operation: id,
        type: 'process:formula',
        name: 'formula',
        input_shape: {},
        formula: "",
        new_name: "",
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function factorizeProcedure(left, top){
    var id = addOperatorSingleInput('Factorize Module', left, top);
    var data = {
        id_operation: id,
        type: 'process:factorize',
        name: 'factorize',
        input_shape: {},
        target: "",
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function updateColumnProcedure(left, top){
    var id = addOperatorSingleInput('Update Column Module', left, top);
    var data = {
        id_operation: id,
        type: 'process:update-column',
        name: 'update-column',
        query_metadata: {},
        query: {},
        target: "",
        into: "",
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function updateValueProcedure(left, top){
    var id = addOperatorSingleInput('Update Value Module', left, top);
    var data = {
        id_operation: id,
        type: 'process:update-value',
        name: 'update-value',
        query_metadata: {},
        query: {},
        target: "",
        into: "",
        shape: {},
        link: []
    };
    metadata[id] = data;
}

function correlationMatrixProcedure(left, top){
    var id = addOutputOperator('Correlation Matrix Module', left, top);
    var data = {
        id_operation: id,
        type: 'chart:cm',
        name: 'cm'
    };
    metadata[id] = data;
}

function decisionTreeProcedure(left, top){
    var id = addOutputOperator('Decision Tree Module', left, top);
    var data = {
        id_operation: id,
        type: 'model:dt',
        name: 'dt',
        input_shape: {},
        target: ""
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

function showUpdateQuery(id){
    $("#update-module-id").val(id);
    $("#update-module-warning").hide();
    $("#update-module-perform").show();
    if (metadata[id]['query_metadata'].length > 0){
        $('#query-builder-update').queryBuilder({
            allow_empty: true,
            sort_filters: true,
            filters: metadata[id]['query_metadata']
        });
        if(!jQuery.isEmptyObject(metadata[id]['query'])){
          $('#query-builder-update').queryBuilder('setRules', metadata[id]['query']);
        }else{
          $('#query-builder-update').queryBuilder('setRules', {condition: "AND", rules: []});
        }

        $.each(metadata[id]['shape'], function(index, value){
            $("#update-target").append('<option value="' + index + '">' + index + '</option>');
            $("#update-to-column").append('<option value="' + index + '">' + index + '</option>');
        });

        $("#update-module-warning").hide();
        $("#update-column-body").show();
    }else{
        $("#update-module-warning").show();
        $("#update-column-body").hide();
        $("#update-module-perform").hide();
    }
    var data = $("#content").flowchart('getData');
    $("#update-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
    $("#updateDataModal").modal();
}

function showUpdateValue(id){
    $("#update-value-id").val(id);
    $("#update-value-warning").hide();
    $("#update-value-perform").show();
    if (metadata[id]['query_metadata'].length > 0){
        $('#query-builder-update-value').queryBuilder({
            allow_empty: true,
            sort_filters: true,
            filters: metadata[id]['query_metadata']
        });
        if(!jQuery.isEmptyObject(metadata[id]['query'])){
          $('#query-builder-update-value').queryBuilder('setRules', metadata[id]['query']);
        }else{
          $('#query-builder-update-value').queryBuilder('setRules', {condition: "AND", rules: []});
        }

        $.each(metadata[id]['shape'], function(index, value){
            $("#update-target-column").append('<option value="' + index + '">' + index + '</option>');
        });

        $("#update-value-warning").hide();
        $("#update-value-body").show();
    }else{
        $("#update-value-warning").show();
        $("#update-value-body").hide();
        $("#update-value-perform").hide();
    }
    var data = $("#content").flowchart('getData');
    $("#update-value-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
    $("#updateValueModal").modal();
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
        $("#column-filter-module-perform").hide();
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

function showFormulaModule(id){
    $("#formula-id").val(id);
    
    if (!jQuery.isEmptyObject(metadata[id]['input_shape'])){
        var tag = [];
        $.each(metadata[id]['input_shape'], function(index, value){
            tag.push(index);
        });
        var availableTags = tag;
          function split( val ) {
            return val.split( /[+, -, *, /]\s*/ );
          }
          function extractLast( term ) {
            return split( term ).pop();
          }
       
          $( "#formula-input" )
            .on( "keydown", function( event ) {
              if ( event.keyCode === $.ui.keyCode.TAB &&  $( this ).autocomplete( "instance" ).menu.active ) {
                event.preventDefault();
              }
            })
            .autocomplete({
              minLength: 0,
              source: function( request, response ) {
                response( $.ui.autocomplete.filter(
                  availableTags, extractLast( request.term ) ) );
              },
              focus: function() {
                return false;
              },
              select: function( event, ui ) {
                var terms = split( this.value );
                terms.pop();
                terms.push( ui.item.value );
                terms.push( "" );
                this.value = terms.join( " " );
                return false;
              }
            });
        $("#formula-module-warning").hide();
        $("#formula-body").show();
        $("#formula-module-perform").show();
    }else{
        $("#formula-module-warning").show();
        $("#formula-module-perform").hide();
        $("#formula-body").hide();
    }
    var data = $("#content").flowchart('getData');
    $("#formula-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
    $("#formulaModal").modal();
}

function showFactorizeModule(id){
    $("#factorize-id").val(id);
    if (!jQuery.isEmptyObject(metadata[id]['input_shape'])){
        $("#factorize-column").html("");
        $.each(metadata[id]['input_shape'], function(index, value){
            $("#factorize-column").append('<option value="' + index + '">' + index + '</option>');
        });
        $("#factorize-module-warning").hide();
        $("#factorize-body").show();
    }else{
        $("#factorize-module-warning").show();
        $("#factorize-module-perform").hide();
        $("#factorize-body").hide();
    }
    var data = $("#content").flowchart('getData');
    $("#factorize-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
    $("#factorizeModal").modal();
}

function showDecisionTreeModule(id){
    $("#dt-id").val(id);
    if (!jQuery.isEmptyObject(metadata[id]['input_shape'])){
        $("#dt-target").html("");
        $.each(metadata[id]['input_shape'], function(index, value){
            $("#dt-target").append('<option value="' + index + '">' + index + '</option>');
        });
        $("#dt-module-warning").hide();
        $("#dt-body").show();
    }else{
        $("#dt-module-warning").show();
        $("#dt-module-perform").hide();
        $("#dt-body").hide();
    }
    var data = $("#content").flowchart('getData');
    $("#dt-output-feet").val(Object.keys(data['operators'][id]['properties']['outputs']).length);
    $("#decisionTreeModal").modal();
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
  if(tmp_metadata['type'] == 'process:join' || tmp_metadata['type'] == 'process:append'){
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

function performUpdateModule(){
    var id = $("#update-module-id").val();
    var result = $('#query-builder-update').queryBuilder('getRules', {
      get_flags: true,
      skip_empty: true
    });

    if (!$.isEmptyObject(result)) {
      metadata[id]['query'] = result;
    }

    var target = $("#update-target").val();
    var into = $("#update-to-column").val();
    metadata[id]['target'] = target;
    metadata[id]['into'] = into;

    var output_feet = $("#update-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#updateDataModal").modal('hide');
}

function performUpdateValueModule(){
    var id = $("#update-value-id").val();
    var result = $('#query-builder-update-value').queryBuilder('getRules', {
      get_flags: true,
      skip_empty: true
    });

    if (!$.isEmptyObject(result)) {
      metadata[id]['query'] = result;
    }

    var target = $("#update-target-column").val();
    var into = $("#update-to-value").val();
    metadata[id]['target'] = target;
    metadata[id]['into'] = into;

    var output_feet = $("#update-value-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#updateValueModal").modal('hide');
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
    var left_data = jQuery.extend(true, {}, metadata[id]['input_metadata'][0]['shape']);
    var right_data = jQuery.extend(true, {}, metadata[id]['input_metadata'][1]['shape']);
    var final_data = {};
    if(left == right){
        final_data[left] = left_data[left];
        delete left_data[left];
        delete right_data[right];
    }
    $.each(left_data, function(index, value){
        if(index in right_data){
            final_data["x_" + index] = left_data[index];
        }else{
            final_data[index] = left_data[index];
        }
    });
    $.each(right_data, function(index, value){
        if(index in left_data){
            final_data["y_" + index] = right_data[index];
        }else{
            final_data[index] = right_data[index];
        }
    });
    metadata[id]['shape'] = final_data;
    var output_feet = $("#join-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#joinDataModal").modal('hide');
}

function performAppendModule(){
    var id = $("#append-file-id").val();

    var left_data = metadata[id]['input_metadata'][0]['shape'];
    var right_data = metadata[id]['input_metadata'][1]['shape'];
    var same = true;

    $.each(right_data, function(index, value){
        if(!(index in left_data)){
            same = false;
        }
    });

    if(same){
        metadata[id]['shape'] = left_data;
    }else{
        // Error
    }

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

    shape = metadata[id]["input_shape"];
    final_data = {};

    if(group_by.includes(",")){
        tmp = group_by.split(",");
        for(var i in tmp){
            key = tmp[i];
            final_data[key] = shape[tmp[i]];
        }
    }else{
        final_data[group_by] = shape[group_by];
    }

    final_data[f + "_" + target] = shape[target];

    metadata[id]['shape'] = final_data;

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
    metadata[id]['shape'] = metadata[id]['input_shape'];
    remakeOutputFeet(id, output_feet);
    $("#fillnaAggregateModal").modal('hide');
}

function performFillnaOCModule(){
    var id = $("#fillna-oc-id").val();
    var target = $("#fillna-oc-column").val();
    var other = $("#fillna-oc-ocolumn").val();
    metadata[id]["target"] = target;
    metadata[id]["other"] = other;
    metadata[id]['shape'] = metadata[id]['input_shape'];
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
    metadata[id]['shape'] = metadata[id]['input_shape'];
    var output_feet = $("#fillna-value-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#fillnaValueModal").modal('hide');
}

function performFormulaModule(){
    var id = $("#formula-id").val();
    var formula = $("#formula-input").val();
    var new_name = $("#formula-column").val();
    metadata[id]['formula'] = formula;
    metadata[id]['new_name'] = new_name;
    metadata[id]['shape'] = metadata[id]['input_shape'];
    metadata[id]['shape'][new_name] = 'int64';
    var output_feet = $("#formula-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#formulaModal").modal('hide');
}

function performFactorizeModule(){
    var id = $("#factorize-id").val();
    var target = $("#factorize-column").val();
    metadata[id]['target'] = target;
    metadata[id]['shape'] = metadata[id]['input_shape'];
    var output_feet = $("#factorize-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#factorizeModal").modal('hide');
}

function performDecisionTreeModule(){
    var id = $("#dt-id").val();
    var target = $("#dt-target").val();
    metadata[id]['target'] = target;
    metadata[id]['shape'] = metadata[id]['input_shape'];
    var output_feet = $("#dt-output-feet").val();
    remakeOutputFeet(id, output_feet);
    $("#decisionTreeModal").modal('hide');
}

function getMetadata(){
    console.log(JSON.stringify(metadata));
    return metadata;
}

function getSchema(){
    var data = $("#content").flowchart('getData');
    console.log(JSON.stringify(data));
    return data;
}

function submit_post_via_hidden_form(url, params) {
    var f = $("<form target='_blank' method='POST' style='display:none;'></form>").attr({
        action: url
    }).appendTo(document.body);

    for (var i in params) {
        if (params.hasOwnProperty(i)) {
            $('<input type="hidden" />').attr({
                name: i,
                value: params[i]
            }).appendTo(f);
        }
    }

    f.submit();
    f.remove();
}

function sendData(){
    var metadata = getMetadata();
    var schema = getSchema();
    submit_post_via_hidden_form(
        '/report',
        {
            metadata: JSON.stringify(metadata)
        }
    );
}