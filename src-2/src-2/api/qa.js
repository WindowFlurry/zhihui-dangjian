import { post } from '../utils/axios.js';

/**
 * 智能问答接口，
 * @param {string} question - 用户问题
 * @param {string} sessionId - 会话ID，用于多轮对话（可选）
 * @returns {Promise} - 问答结果
 */
/**
 * 上传文件接口（与知识库上传文件接口相同）
 * @param {File} file - 文件
 * @param {string} description - 文件描述（可选）
 * @returns {Promise} - 上传结果
 */
export const uploadFile = async (file, description = '') => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await post('/knowledge/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000 
    });

    return response;
  } catch (error) {
    console.error('文件上传失败:', error);
    throw error;
  }
};

/**
 * 智能问答接口，
 * @param {string} question - 用户问题
 * @param {string} sessionId - 会话ID，用于多轮对话（可选）
 * @returns {Promise} - 问答结果
 */
export const askQuestion = async (question, sessionId = '') => {
  try {
    // 验证参数
    if (!question || typeof question !== 'string' || question.trim() === '') {
      throw new Error('问题不能为空');
    }

    const requestData = {
      question: question.trim()
    };

    // 如果提供了sessionId，则添加到请求数据中
    if (sessionId && typeof sessionId === 'string') {
      requestData.session_id = sessionId;
    }

    console.log('准备发送智能问答请求:', {
      url: '/knowledge/ask',
      data: requestData
    });

    // 发送POST请求到智能问答接口
    const response = await post('/knowledge/ask', requestData, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 30000
    });

    console.log('智能问答请求成功，响应数据:', response);

    // 返回处理后的响应数据
    return processQAResponse(response);
  } catch (error) {
    console.error('智能问答请求失败:', error);
    throw new Error(`智能问答请求失败: ${error.message}`);
  }
};

/**
 * 处理智能问答响应数据
 * @param {Object} response - 原始响应数据
 * @returns {Object} - 处理后的结构化数据
 */
const processQAResponse = (response) => {
  // 基础响应结构
  const result = {
    answer: response.answer || '',
    sources: response.sources || [],
    session_id: response.session_id || ''
  };

  return result;
};

export const qa = {
  askQuestion,
  uploadFile
};

export default {
  askQuestion,
  uploadFile,
  qa
};