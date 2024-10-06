import { API_HOST } from './config.js';

async function checkResponse(response) {
  if (response.status === 500) {
    throw new Error('Server error: 500');
  }
  return response.json();
}

export async function listDevices(platform) {
  const response = await fetch(`${API_HOST}${platform}/serials`);
  return checkResponse(response);
}

export async function connectDevice(platform, serial, wdaUrl, maxDepth) {
  const response = await fetch(`${API_HOST}${platform}/${serial}/connect?wdaUrl=${wdaUrl}&maxDepth=${maxDepth}`, {
    method: 'POST'
  });
  return checkResponse(response);
}

export async function fetchScreenshot(platform, serial) {
  const response = await fetch(`${API_HOST}${platform}/${serial}/screenshot`);
  return checkResponse(response);
}

export async function fetchHierarchy(platform, serial) {
  const response = await fetch(`${API_HOST}${platform}/${serial}/hierarchy`);
  return checkResponse(response);
}