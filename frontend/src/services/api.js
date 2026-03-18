import axios from 'axios';

const BASE_URL = ''; // Relative path since we serve on the same origin

const api = axios.create({ baseURL: BASE_URL });

export const uploadPDF = (file, onUploadProgress) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('/api/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress,
  });
};

export const getResult = (jobId) => api.get(`/api/result/${jobId}`);

export const getDownloadURL = (jobId) => `${BASE_URL}/api/download/${jobId}`;

export const createProgressStream = (jobId, onEvent, onError, onDone) => {
  const es = new EventSource(`${BASE_URL}/api/progress/${jobId}`);
  es.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      if (data.ping) return;
      onEvent(data);
      if (data.job_status === 'done' || data.job_status === 'error') {
        es.close();
        onDone(data.job_status);
      }
    } catch (err) {
      console.error('SSE parse error', err);
    }
  };
  es.onerror = (err) => {
    es.close();
    onError(err);
  };
  return () => es.close();
};

export default api;
