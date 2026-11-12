import axios from 'axios';

/**
 * 创建axios实例
 */
const instance = axios.create({
  baseURL: 'http://localhost:5000', // 开发环境基础URL
  timeout: 30000, // 超时时间30秒
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * 请求拦截器
 * 在发送请求之前做些什么
 */
instance.interceptors.request.use(
  config => {
    // 可以在这里添加token等认证信息
    // 例如：config.headers.Authorization = `Bearer ${getToken()}`;
    return config;
  },
  error => {
    // 处理请求错误
    console.error('请求配置错误:', error);
    return Promise.reject(error);
  }
);

/**
 * 响应拦截器
 * 对响应数据做点什么
 */
instance.interceptors.response.use(
  response => {
    // 直接返回data部分，简化使用
    return response.data;
  },
  error => {
    // 处理响应错误
    if (error.response) {
      // 服务器返回了错误状态码
      console.error(`HTTP错误: ${error.response.status} ${error.response.statusText}`);
    } else if (error.request) {
      // 请求已发送但未收到响应
      console.error('没有收到响应:', error.request);
    } else {
      // 设置请求时发生了错误
      console.error('请求配置错误:', error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * 封装GET请求
 * @param {string} url - 请求URL
 * @param {Object} params - 请求参数
 * @param {Object} config - 额外配置
 * @returns {Promise} - 请求结果Promise
 */
export const get = (url, params = {}, config = {}) => {
  return instance.get(url, { params, ...config });
};

/**
 * 封装POST请求
 * @param {string} url - 请求URL
 * @param {Object} data - 请求数据
 * @param {Object} config - 额外配置
 * @returns {Promise} - 请求结果Promise
 */
export const post = (url, data = {}, config = {}) => {
  return instance.post(url, data, config);
};

/**
 * 封装PUT请求
 * @param {string} url - 请求URL
 * @param {Object} data - 请求数据
 * @param {Object} config - 额外配置
 * @returns {Promise} - 请求结果Promise
 */
export const put = (url, data = {}, config = {}) => {
  return instance.put(url, data, config);
};

/**
 * 封装DELETE请求
 * @param {string} url - 请求URL
 * @param {Object} params - 请求参数
 * @param {Object} config - 额外配置
 * @returns {Promise} - 请求结果Promise
 */
export const del = (url, params = {}, config = {}) => {
  return instance.delete(url, { params, ...config });
};

// 导出默认对象和实例
export default instance;
export { instance };