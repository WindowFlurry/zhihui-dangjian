from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许所有来源的CORS请求

# 测试接口
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify(message='Flask backend is running')

# agent相关接口
@app.route('/agent/tasks', methods=['POST'])
def create_task():
    data = request.json
    # 模拟创建任务
    return jsonify(id=1, status='created', data=data)

@app.route('/agent/tasks', methods=['GET'])
def get_task_list():
    # 模拟返回任务列表
    return jsonify([{'id': 1, 'title': '任务1', 'status': 'running'}])

@app.route('/agent/tasks/<int:task_id>', methods=['GET'])
def get_task_detail(task_id):
    # 模拟返回任务详情
    return jsonify(id=task_id, title=f'任务{task_id}', status='running', result='任务结果')

@app.route('/agent/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    # 模拟更新任务
    return jsonify(id=task_id, status='updated', data=data)

@app.route('/agent/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    # 模拟删除任务
    return jsonify(id=task_id, status='deleted')

@app.route('/agent/tasks/<int:task_id>/start', methods=['POST'])
def start_task(task_id):
    # 模拟启动任务
    return jsonify(id=task_id, status='started')

@app.route('/agent/tasks/<int:task_id>/stop', methods=['POST'])
def stop_task(task_id):
    # 模拟停止任务
    return jsonify(id=task_id, status='stopped')

# qa相关接口
@app.route('/qa/ask', methods=['POST'])
def ask_question():
    data = request.json
    # 模拟智能问答
    return jsonify(answer='这是一个模拟的回答', session_id='test-session-id')

@app.route('/qa/upload', methods=['POST'])
def upload_file():
    # 模拟文件上传
    return jsonify(message='文件上传成功')

# agent chat接口
@app.route('/agent/chat', methods=['POST'])
def agent_chat():
    data = request.json
    # 模拟agent聊天
    return jsonify(output='这是一个模拟的agent回答')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)