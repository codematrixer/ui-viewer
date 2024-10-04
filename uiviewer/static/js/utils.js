export function saveToLocalStorage(key, value) {
    localStorage.setItem(key, value);
  }
  
  export function getFromLocalStorage(key, defaultValue) {
    return localStorage.getItem(key) || defaultValue;
  }
  
  export function copyToClipboard(value) {
    if (typeof value === 'object') {
      value = JSON.stringify(value, null, 2);
    }
  
    if (value === null || value === undefined || value === '') {
      value = '';
    }
  
    const textarea = document.createElement('textarea');
    textarea.value = value;
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      return true;
    } catch (err) {
      return false;
    } finally {
      document.body.removeChild(textarea);
    }
  }