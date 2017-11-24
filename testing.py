import tools.FlowProcess as fp
import json

with open('Development/FlowProcess/Metadata/hr-model.json') as data_file:
    metadata = json.load(data_file)
tools = fp.FlowProcess()
tools.set_metadata(metadata)
tools.run()
data = tools.get_current_data()
chart = tools.get_chart()
model = tools.get_model()
data_tables = []
co = 1
for key, value in data.iteritems():
    data_tables.append({
        'count': co,
        'table': value['data'].head(10).to_html(classes='table table-hover')
    })
    co += 1

print {
    'data': data_tables,
    'chart': chart,
    'model': model
}