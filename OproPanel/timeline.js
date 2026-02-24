/**
 * 1. 数据配置区 (自上而下填写即可)
 */
const timelineData = [
   {
      year: "2026",
      open: true, // true 表示默认展开，false 表示收起
      items: [
         {
            version: "v0.05",
            date: "2026/2/25",
            content: "修了json功能，并且加了一个确认框，同时将native改成普通input"
         },
         {
            version: "v0.04",
            date: "2026/2/24",
            content: "byd，我修了一堆bug，终于把兼容改完了，现在至少2023和2024可以正常使用，我认为这值得单开一个版本号庆祝一下，因为累死我了"
         },
         {
            version: "v0.03",
            date: "2026/2/24",
            content: "增加自由选择函数、（主要由@SHBRX）紧急更新PR2024以下兼容版本、优化选择函数方法、增加这个没什么用的更新说明，甚至为了写这玩意单独做了一套css+js（"
         },
         {
            version: "v0.02",
            date: "2026/2/24",
            content: "增加大量迫真广告、界面升级为Fluent UI，此版本存在大量bug，不建议使用"
         },
         {
            version: "v0.01",
            date: "2026/2/20",
            content: "第一版本发布 含有json对轨功能"
         }
      ]
   },
   {
      year: "2025",
      open: false,
      items: [
         {
            version: "预览版",
            date: "2025/3",
            content: "早期预览版 只能实现左右抽"
         }
      ]
   }
];

/**
 * 2. 核心逻辑区 (通过 #UpC 自动注入 HTML)
 */
document.addEventListener('DOMContentLoaded', () => {
   // 定位到你的容器
   const upCard = document.getElementById('UpC');
   if (!upCard) return; // 如果没找到就退出

   const header = upCard.querySelector('.card-header');
   if (!header) return;

   // Fluent UI 的展开箭头 SVG
   const chevronSVG = `<svg class="timeline-chevron" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg"><path d="M5.15 3.15a.5.5 0 0 1 .7 0l4.5 4.5a.5.5 0 0 1 0 .7l-4.5 4.5a.5.5 0 0 1-.7-.7L9.29 8 5.15 3.85a.5.5 0 0 1 0-.7z" /></svg>`;

   // 拼装时间轴 HTML 字符串
   let timelineHTML = `<div class="fluent-timeline">`;

   timelineData.forEach(group => {
      timelineHTML += `
            <details class="timeline-group" ${group.open ? 'open' : ''}>
                <summary class="timeline-year-header">
                    ${chevronSVG} 📅 ${group.year}
                </summary>
                <div class="timeline-items">
        `;

      group.items.forEach(item => {
         timelineHTML += `
                    <div class="timeline-item">
                        <div class="timeline-card">
                            <div class="timeline-meta">
                                <span class="version-badge">${item.version}</span>
                                <span class="date">${item.date}</span>
                            </div>
                            <div class="timeline-body">
                                <p>${item.content}</p>
                            </div>
                        </div>
                    </div>
            `;
      });

      timelineHTML += `
                </div>
            </details>
        `;
   });

   timelineHTML += `</div>`;

   // 防呆设计：如果你的 HTML 里还残留着旧的 .fluent-timeline，先把它删了
   const oldTimeline = upCard.querySelector('.fluent-timeline');
   if (oldTimeline) oldTimeline.remove();

   // 将生成的时间轴精准插入到 <div class="card-header"> 的正下方
   header.insertAdjacentHTML('afterend', timelineHTML);
});

document.addEventListener("DOMContentLoaded", function () {
   var csInterface = new CSInterface();

   // --- 新增：版本检测与跳转 ---
   const hostEnv = csInterface.getHostEnvironment();
   if (hostEnv && hostEnv.appVersion) {
      const majorVersion = parseInt(hostEnv.appVersion.split('.')[0]);
      // 关键修改：只有当版本低于 25 且 当前页面不是 compat_index.html 时，才进行跳转
      if (majorVersion < 25 && !window.location.href.includes("compat_index.html")) {
         window.location.href = "compat_index.html";
      }

}});