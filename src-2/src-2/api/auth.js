// 导入项目中已有的axios实例
import { post, get, put, del } from '../utils/axios.js';

/**
 * 注册接口
 * @param {Object} data - 注册参数
 * @param {string} data.phone_number - 手机号
 * @param {string} data.password - 密码
 * @returns {Promise} - 注册结果Promise
 */
export const register = async (data) => {
  try {
    // 验证必填字段
    if (!data.phone_number || !data.password) {
      throw new Error('请填写手机号和密码');
    }
    
    // 验证手机号格式
    const phoneRegex = /^1[3-9]\d{9}$/;
    if (!phoneRegex.test(data.phone_number)) {
      throw new Error('请输入正确的手机号格式');
    }
    
    // 发送注册请求 - 使用正确的API路径
    const response = await post('/auth/register', data);
    return response;
  } catch (error) {
    console.error('注册失败:', error);
    throw error;
  }
};

/**
 * 登录接口
 * @param {Object} data - 登录参数
 * @param {string} data.phone_number - 手机号
 * @param {string} data.password - 密码
 * @returns {Promise} - 登录结果Promise
 */
export const login = async (data) => {
  try {
    // 验证必填字段
    if (!data.phone_number || !data.password) {
      throw new Error('请输入手机号和密码');
    }
    
    // 验证手机号格式
    const phoneRegex = /^1[3-9]\d{9}$/;
    if (!phoneRegex.test(data.phone_number)) {
      throw new Error('请输入正确的手机号格式');
    }
    
    // 发送登录请求 - 使用正确的API路径
    const response = await post('/auth/login', data);
    
    // 登录成功后保存用户信息到localStorage
    if (response.success) {
      localStorage.setItem('isLoggedIn', 'true');
      localStorage.setItem('phoneNumber', response.phone_number || data.phone_number);
      localStorage.setItem('session_id', response.session_id);
    }
    
    return response;
  } catch (error) {
    console.error('登录失败:', error);
    throw error;
  }
};

/**
 * 退出登录
 */
export const logout = async () => {
  try {
    // 发送退出登录请求
    await post('/auth/logout');
    
    // 清除localStorage中的用户信息
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('phoneNumber');
    localStorage.removeItem('session_id');
  } catch (error) {
    console.error('退出登录失败:', error);
    // 即使API调用失败，也清除本地存储
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('phoneNumber');
    localStorage.removeItem('session_id');
    throw error;
  }
};

/**
 * 获取当前登录用户信息
 * @returns {Object|null} - 用户信息或null（未登录）
 */
export const getCurrentUser = () => {
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
  if (!isLoggedIn) {
    return null;
  }
  
  return {
    phoneNumber: localStorage.getItem('phoneNumber'),
    sessionId: localStorage.getItem('session_id')
  };
};

/**
 * 获取用户信息
 * @returns {Promise} - 用户信息
 */
export const getUserInfo = async () => {
  try {
    const response = await get('/auth/user_info');
    return response;
  } catch (error) {
    console.error('获取用户信息失败:', error);
    throw error;
  }
};

/**
 * 更新用户信息
 * @param {Object} data - 用户信息
 * @param {string} [data.username] - 用户名
 * @returns {Promise} - 更新结果
 */
export const updateUserInfo = async (data) => {
  try {
    const response = await put('/auth/user_info', data);
    return response;
  } catch (error) {
    console.error('更新用户信息失败:', error);
    throw error;
  }
};

/**
 * 组织认证
 * @param {Object} data - 组织认证信息
 * @param {string} data.phone_number - 手机号
 * @param {string} data.real_name - 真实姓名
 * @returns {Promise} - 组织认证结果
 */
export const verifyOrganization = async (data) => {
  try {
    // 验证必填字段
    if (!data.phone_number || !data.real_name) {
      throw new Error('请填写手机号和真实姓名');
    }
    
    const response = await post('/auth/organization/verify', data);
    return response;
  } catch (error) {
    console.error('组织认证失败:', error);
    throw error;
  }
};

/**
 * 获取组织认证信息
 * @returns {Promise} - 组织认证信息
 */
export const getOrganizationInfo = async () => {
  try {
    const response = await get('/auth/organization/verify');
    return response;
  } catch (error) {
    console.error('获取组织认证信息失败:', error);
    throw error;
  }
};

/**
 * 发送短信验证码
 * @param {Object} data - 发送短信验证码参数
 * @param {string} data.phone_number - 手机号
 * @returns {Promise} - 发送短信验证码结果
 */
export const sendSmsCode = async (data) => {
  try {
    // 验证必填字段
    if (!data.phone_number) {
      throw new Error('请填写手机号');
    }
    
    const response = await post('/auth/send_sms', data);
    return response;
  } catch (error) {
    console.error('发送短信验证码失败:', error);
    throw error;
  }
};

/**
 * 验证短信验证码
 * @param {Object} data - 验证短信验证码参数
 * @param {string} data.phone_number - 手机号
 * @param {string} data.sms_code - 短信验证码
 * @returns {Promise} - 验证短信验证码结果
 */
export const verifySmsCode = async (data) => {
  try {
    // 验证必填字段
    if (!data.phone_number || !data.sms_code) {
      throw new Error('请填写手机号和短信验证码');
    }
    
    const response = await post('/auth/verify_sms', data);
    return response;
  } catch (error) {
    console.error('验证短信验证码失败:', error);
    throw error;
  }
};

/**
 * 重置密码
 * @param {Object} data - 重置密码参数
 * @param {string} data.phone_number - 手机号
 * @param {string} data.sms_code - 短信验证码
 * @param {string} data.new_password - 新密码
 * @returns {Promise} - 重置密码结果
 */
export const resetPassword = async (data) => {
  try {
    // 验证必填字段
    if (!data.phone_number || !data.sms_code || !data.new_password) {
      throw new Error('请填写手机号、短信验证码和新密码');
    }
    
    const response = await post('/auth/reset_password', data);
    return response;
  } catch (error) {
    console.error('重置密码失败:', error);
    throw error;
  }
};

/**
 * 修改密码
 * @param {Object} data - 修改密码参数
 * @param {string} data.old_password - 旧密码
 * @param {string} data.new_password - 新密码
 * @returns {Promise} - 修改密码结果
 */
export const changePassword = async (data) => {
  try {
    // 验证必填字段
    if (!data.old_password || !data.new_password) {
      throw new Error('请填写旧密码和新密码');
    }
    
    const response = await post('/auth/change_password', data);
    return response;
  } catch (error) {
    console.error('修改密码失败:', error);
    throw error;
  }
};

/**
 * 更新简历信息
 * @param {Object} data - 简历信息
 * @param {string} data.real_name - 真实姓名
 * @param {string} data.party_branch - 党支部
 * @param {string} data.party_position - 党内职务
 * @returns {Promise} - 更新简历信息结果
 */
export const updateResume = async (data) => {
  try {
    // 验证必填字段
    if (!data.real_name || !data.party_branch || !data.party_position) {
      throw new Error('请填写完整的简历信息');
    }
    
    const response = await put('/auth/resume', data);
    return response;
  } catch (error) {
    console.error('更新简历信息失败:', error);
    throw error;
  }
};

/**
 * 获取简历信息
 * @returns {Promise} - 简历信息
 */
export const getResume = async () => {
  try {
    const response = await get('/auth/resume');
    return response;
  } catch (error) {
    console.error('获取简历信息失败:', error);
    throw error;
  }
};

/**
 * 验证用户是否已登录
 * @returns {boolean} - 是否已登录
 */
export const isAuthenticated = () => {
  return localStorage.getItem('isLoggedIn') === 'true';
};

// 导出默认对象
const authAPI = {
  register,
  login,
  logout,
  getCurrentUser,
  isAuthenticated
};

export default authAPI;