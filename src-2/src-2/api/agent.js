import { post, get, put, del } from '../utils/axios.js';

/**
 * 创建任务
 * @param {Object} data - 任务数据
 * @param {string} [data.workflow_type] - 工作流类型，默认'default_workflow'
 * @param {Object} data.task_data - 任务数据
 * @param {string} data.task_data.query - 查询内容
 * @returns {Promise} - 创建结果
 */
export const createTask = async (data) => {
  try {
    const response = await post('/agent/tasks', data);
    return response;
  } catch (error) {
    console.error('创建任务失败:', error);
    throw error;
  }
};

/**
 * 获取任务列表
 * @returns {Promise} - 任务列表
 */
export const getTaskList = async () => {
  try {
    const response = await get('/agent/tasks');
    return response;
  } catch (error) {
    console.error('获取任务列表失败:', error);
    throw error;
  }
};

/**
 * 获取任务详情
 * @param {string} taskId - 任务ID
 * @returns {Promise} - 任务详情
 */
export const getTaskDetail = async (taskId) => {
  try {
    const response = await get(`/agent/tasks/${taskId}`);
    return response;
  } catch (error) {
    console.error('获取任务详情失败:', error);
    throw error;
  }
};

/**
 * 更新任务
 * @param {string} taskId - 任务ID
 * @param {Object} data - 更新数据
 * @param {string} data.action - 操作类型，如'resume'
 * @param {any} [data.resume_data] - 恢复数据
 * @returns {Promise} - 更新结果
 */
export const updateTask = async (taskId, data) => {
  try {
    const response = await put(`/agent/tasks/${taskId}`, data);
    return response;
  } catch (error) {
    console.error('更新任务失败:', error);
    throw error;
  }
};

/**
 * 删除任务
 * @param {string} taskId - 任务ID
 * @returns {Promise} - 删除结果
 */
export const deleteTask = async (taskId) => {
  try {
    const response = await del(`/agent/tasks/${taskId}`);
    return response;
  } catch (error) {
    console.error('删除任务失败:', error);
    throw error;
  }
};

/**
 * 启动任务
 * @param {string} taskId - 任务ID
 * @returns {Promise} - 启动结果
 */
export const startTask = async (taskId) => {
  try {
    const response = await post(`/agent/tasks/${taskId}/start`);
    return response;
  } catch (error) {
    console.error('启动任务失败:', error);
    throw error;
  }
};

/**
 * 停止任务
 * @param {string} taskId - 任务ID
 * @returns {Promise} - 停止结果
 */
export const stopTask = async (taskId) => {
  try {
    const response = await post(`/agent/tasks/${taskId}/stop`);
    return response;
  } catch (error) {
    console.error('停止任务失败:', error);
    throw error;
  }
};

/**
 * 执行Agent任务（兼容旧接口）
 * @param {string} input - 用户输入内容
 * @param {string} [command='default_workflow'] - 工作流类型
 * @returns {Promise} - 响应结果
 */
export const runAgentTask = async (input, command = 'default_workflow') => {
  try {
    const taskData = {
      workflow_type: command,
      task_data: {
        query: input
      }
    };
    const response = await createTask(taskData);
    return response;
  } catch (error) {
    console.error('执行Agent任务失败:', error);
    throw error;
  }
};

/**
 * Agent聊天（兼容旧接口）
 * @param {Object} data - 聊天数据
 * @param {string} data.content - 聊天内容
 * @returns {Promise} - 聊天结果
 */
export const agentChat = async (data) => {
  try {
    return await runAgentTask(data.content);
  } catch (error) {
    console.error('Agent聊天失败:', error);
    throw error;
  }
};

// 导出默认对象
const agentAPI = {
  createTask,
  getTaskList,
  getTaskDetail,
  updateTask,
  deleteTask,
  startTask,
  stopTask,
  runAgentTask,
  agentChat
};

export default agentAPI;