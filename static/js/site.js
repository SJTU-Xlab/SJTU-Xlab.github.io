(() => {
  "use strict";
  const requests = new Map();
  function showStatus(message, isError = false) {
    let status = document.getElementById("site-status");
    if (!status) {
      status = document.createElement("div");
      status.id = "site-status";
      (document.body || document.documentElement).appendChild(status);
    }
    status.textContent = message;
    status.hidden = false;
    status.classList.toggle("site-status-error", isError);
    status.setAttribute("role", isError ? "alert" : "status");
    status.setAttribute("aria-live", "polite");
  }
  async function loadJSON(url) {
    if (!requests.has(url)) {
      requests.set(url, fetch(url).then(response => {
        if (!response.ok) throw new Error(`数据请求失败：${response.status} ${url}`);
        return response.json();
      }).catch(error => {
        requests.delete(url);
        throw error;
      }));
    }
    return requests.get(url);
  }
  function reportError(error) {
    console.error(error);
    showStatus("加载失败，请检查网络后刷新页面。地图还需要腾讯地图服务及有效的域名授权。", true);
  }
  window.XLab = {
    loadJSON, showStatus, reportError,
    clearStatus() {
      const status = document.getElementById("site-status");
      if (status) status.hidden = true;
    }
  };
  window.addEventListener("error", event => {
    if (event.target instanceof HTMLScriptElement && event.target.src.includes("map.qq.com/")) {
      reportError(new Error("腾讯地图 SDK 加载失败"));
    }
  }, true);
  document.addEventListener("DOMContentLoaded", () => {
    if (document.documentElement.dataset.mapPage && !window.TMap) {
      reportError(new Error("腾讯地图 SDK 不可用"));
    }
  });
})();
