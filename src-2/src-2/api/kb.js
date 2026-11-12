import { get, post, del } from '../utils/axios.js';

/**
 * 文件上传接口
 * @param {File} file - 文件对象
 * @returns {Promise} - 上传结果
 */
export const uploadFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await post('/knowledge/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000 // 60秒
    });

    return response;
  } catch (error) {
    console.error('文件上传失败:', error);
    throw error;
  }
};

/**
 * 获取文件列表接口
 * @returns {Promise} - 文件列表
 */
export const getFileList = async () => {
  try {
    const response = await get('/knowledge/files');
    return response;
  } catch (error) {
    console.error('获取文件列表失败:', error);
    throw error;
  }
};

/**
 * 智能问答接口
 * @param {Object} data - 问答数据
 * @param {string} data.question - 问题内容
 * @param {any[]} [data.history] - 历史对话记录，可选
 * @returns {Promise} - 问答结果
 */
export const askQuestion = async (data) => {
  try {
    const response = await post('/knowledge/ask', data);
    return response;
  } catch (error) {
    console.error('智能问答失败:', error);
    throw error;
  }
};

/**
 * 删除文件接口
 * @param {string} filename - 存储的文件名
 * @returns {Promise} - 删除结果
 */
export const deleteFile = async (filename) => {
  try {
    const response = await del(`/knowledge/delete/${encodeURIComponent(filename)}`);
    return response;
  } catch (error) {
    console.error('删除文件失败:', error);
    throw error;
  }
};

/**
 * 文档上传接口（兼容旧接口）
 * @param {File} file - 文件
 * @param {string} [description=''] - 文件描述
 * @returns {Promise} - 上传结果
 */
export const uploadDocument = async (file, description = '') => {
  try {
    return await uploadFile(file);
  } catch (error) {
    console.error('文档上传失败:', error);
    throw error;
  }
};

/**
 * 知识库API对象
 */
const kbAPI = {
  uploadFile,
  getFileList,
  askQuestion,
  deleteFile,
  uploadDocument // 兼容旧接口
};

export default kbAPI;