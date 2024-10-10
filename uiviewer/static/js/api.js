import { API_HOST } from './config.js';

async function checkResponse(response) {
  if (response.status === 500) {
    throw new Error('Server error: 500');
  }
  return response.json();
}

export async function getVersion() {
  const response = await fetch(`${API_HOST}version`);
  return checkResponse(response);
}

export async function listDevices(platform) {
  const response = await fetch(`${API_HOST}${platform}/serials`);
  return checkResponse(response);
}

export async function connectDevice(platform, serial, wdaUrl, maxDepth) {
  let url = `${API_HOST}${platform}/${serial}/connect`;

  if (platform === 'ios') {
    const queryParams = [];
    if (wdaUrl) {
      queryParams.push(`wdaUrl=${encodeURIComponent(wdaUrl)}`);
    }
    if (maxDepth) {
      queryParams.push(`maxDepth=${encodeURIComponent(maxDepth)}`);
    }

    if (queryParams.length > 0) {
      url += `?${queryParams.join('&')}`;
    }
  }

  const response = await fetch(url, {
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

export async function fetchXpathLite(platform, treeData, nodeId) {
  const response = await fetch(`${API_HOST}${platform}/hierarchy/xpathLite`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      tree_data: treeData,
      node_id: nodeId
    })
  });

  return checkResponse(response);
}