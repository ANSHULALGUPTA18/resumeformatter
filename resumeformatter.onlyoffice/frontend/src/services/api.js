import axios from 'axios';

// Use relative URLs for deployed version (same domain)
const API_BASE_URL = '/api';

export const getTemplates = async () => {
  const response = await axios.get(`${API_BASE_URL}/templates`);
  return response.data;
};

export const uploadTemplate = async (formData) => {
  const response = await axios.post(`${API_BASE_URL}/templates`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const formatResumes = async (formData) => {
  const response = await axios.post(`${API_BASE_URL}/format`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const deleteTemplate = async (templateId) => {
  const response = await axios.delete(`${API_BASE_URL}/templates/${templateId}`);
  return response.data;
};

export const downloadFile = (filename) => {
  window.open(`${API_BASE_URL}/download/${filename}`, '_blank');
};

// ===== CAI Contact Endpoints =====
export const getCaiContact = async () => {
  const response = await axios.get(`${API_BASE_URL}/cai-contact`);
  return response.data; // { success, contact: { name, phone, email } }
};

export const saveCaiContact = async (contact) => {
  const response = await axios.post(`${API_BASE_URL}/cai-contact`, contact);
  return response.data; // { success, contact }
};

export const deleteCaiContact = async () => {
  const response = await axios.delete(`${API_BASE_URL}/cai-contact`);
  return response.data; // { success, message }
};
