import { API_HOST } from './config.js';

export async function listDevices(platform) {
  const response = await fetch(`${API_HOST}${platform}/serials`);
  return response.json();
}

export async function connectDevice(platform, serial, wdaUrl) {
  const response = await fetch(`${API_HOST}${platform}/${serial}/init?wdaUrl=${wdaUrl}`, {
    method: 'POST'
  });
  return response.json();
}

export async function fetchScreenshot(platform, serial) {
  const response = await fetch(`${API_HOST}${platform}/${serial}/screenshot`);
  return response.json();
}

export async function fetchHierarchy(platform, serial) {
  const response = await fetch(`${API_HOST}${platform}/${serial}/hierarchy`);
  return response.json();
}