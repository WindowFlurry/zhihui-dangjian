import { get } from '../utils/axios.js';

/**
 * 服务状态检查
 * @returns {Promise} - 服务状态信息
 */
export const getServiceStatus = async () => {
  try {
    const response = await get('/');
    return response;
  } catch (error) {
    console.error('获取服务状态失败:', error);
    throw error;
  }
};

/**
 * 全局健康检查
 * @returns {Promise} - 全局健康检查结果
 */
export const getGlobalHealth = async () => {
  try {
    const response = await get('/health');
    return response;
  } catch (error) {
    console.error('全局健康检查失败:', error);
    throw error;
  }
};

/**
 * 认证服务健康检查
 * @returns {Promise} - 认证服务健康检查结果
 */
export const getAuthServiceHealth = async () => {
  try {
    const response = await get('/auth/health');
    return response;
  } catch (error) {
    console.error('认证服务健康检查失败:', error);
    throw error;
  }
};

/**
 * 智能体服务健康检查
 * @returns {Promise} - 智能体服务健康检查结果
 */
export const getAgentServiceHealth = async () => {
  try {
    const response = await get('/agent/health');
    return response;
  } catch (error) {
    console.error('智能体服务健康检查失败:', error);
    throw error;
  }
};

/**
 * 知识库服务健康检查
 * @returns {Promise} - 知识库服务健康检查结果
 */
export const getKnowledgeServiceHealth = async () => {
  try {
    const response = await get('/knowledge/health');
    return response;
  } catch (error) {
    console.error('知识库服务健康检查失败:', error);
    throw error;
  }
};

/**
 * 系统服务API对象
 */
const systemAPI = {
  getServiceStatus,
  getGlobalHealth,
  getAuthServiceHealth,
  getAgentServiceHealth,
  getKnowledgeServiceHealth
};

export default systemAPI;