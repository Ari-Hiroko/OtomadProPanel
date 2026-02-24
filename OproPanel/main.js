document.addEventListener("DOMContentLoaded", function () {
   // Re-attaching event listeners for dynamically added fluent-buttons
   $("#copypresets").on("click", function (e) {
      e.preventDefault();

      var csInterface = new CSInterface();
      var OSVersion = csInterface.getOSInformation();
      var path = csInterface.getSystemPath(SystemPath.EXTENSION);

      csInterface.evalScript("$._PPP_.getUserName()", function (username) {
         if (OSVersion) {
            var initPath;
            if (OSVersion.indexOf("Windows") >= 0) {
               initPath = "C:\Users" + username;
               var sep = "";
               path = path.replace(/\//g, sep);
            } else {
               initPath = "/Users/" + username;
               var sep = "/";
            }

            path =
               path +
               sep +
               "payloads" +
               sep +
               "Effect\ Presets\ and\ Custom\ Items.prfpset";

            var readResult = window.cep.fs.readFile(path);

            if (0 == readResult.err) {
               var addOutPath =
                  "/Documents/Adobe/Premiere\ Pro/22.0/Profile-" +
                  username +
                  "/Effect\ Presets\ and\ Custom\ Items.prfpset";
               var fullOutPath = initPath + addOutPath;
               var writeResult = window.cep.fs.writeFile(
                  fullOutPath,
                  readResult.data,
               );
               var resultMsg =
                  0 == writeResult.err
                     ? "成功复制效果预设。"
                     : "复制效果预设失败。";
               csInterface.evalScript(
                  "$._PPP_.updateEventPanel('" + resultMsg + "')",
               );
            }
         }
      });
   });

   $("#toggleproxy").on("click", function (e) {
      e.preventDefault();
      var csInterface = new CSInterface();
      csInterface.evalScript(
         "$._PPP_.toggleProxyState()",
         mySetProxyFunction,
      );
      csInterface.evalScript(
         "$._PPP_.getProjectProxySetting()",
         myGetProxyFunction,
      );
   });

   $("#checkforums").on("click", function (e) {
      e.preventDefault();
      new CSInterface().openURLInDefaultBrowser(
         "https://forums.adobe.com/community/premiere/sdk",
      );
   });

   $("#openfolder").on("click", function (e) {
      e.preventDefault();
      var csInterface = new CSInterface();
      var path = csInterface.getSystemPath(SystemPath.EXTENSION);
      if (csInterface.getOSInformation().indexOf("Windows") >= 0) {
         window.cep.process.createProcess(
            "C:\Windows\explorer.exe",
            path.replace(/\//g, ""),
         );
      } else {
         window.cep.process.createProcess("/usr/bin/open", path);
      }
   });

   $("#openlogfilefolder").on("click", function (e) {
      e.preventDefault();
      var csInterface = new CSInterface();
      var userDataPath = csInterface.getSystemPath(SystemPath.USER_DATA);
      var actualDestinationPath = userDataPath.split("A")[0];

      if (csInterface.getOSInformation().indexOf("Windows") >= 0) {
         actualDestinationPath +=
            "AppData/Roaming/Adobe/Premiere Pro/22.0/logs";
         window.cep.process.createProcess(
            "C:\Windows\explorer.exe",
            actualDestinationPath.replace(/\//g, ""),
         );
      } else {
         actualDestinationPath += "Preferences/Adobe/Premiere Pro/22.0/logs";
         window.cep.process.createProcess(
            "/usr/bin/open",
            actualDestinationPath,
         );
      }
   });

   $("#readAPIdocs").on("click", function (e) {
      e.preventDefault();
      new CSInterface().openURLInDefaultBrowser(
         "http://ppro.aenhancers.com",
      );
   });

   $("#newseqfrompreset").on("click", function (e) {
      e.preventDefault();
      var csInterface = new CSInterface();

      // 获取扩展路径并拼接预设文件路径
      var path = csInterface.getSystemPath(SystemPath.EXTENSION) + "/payloads/PProPanel.sqpreset";

      // 使用 JSON.stringify 自动处理字符串转义并加上引号
      var script = "$._PPP_.createSequenceFromPreset(" + JSON.stringify(path) + ")";

      // 调用执行
      csInterface.evalScript(script);
   });

   $("#renderusingdefaultpreset").on("click", function (e) {
      e.preventDefault();
      var csInterface = new CSInterface();
      var path = csInterface.getSystemPath(SystemPath.EXTENSION) + "/payloads/example.epr";
      csInterface.evalScript("$._PPP_.render(" + JSON.stringify(path) + ")");
   });

   $("#stitchusingdefaultpreset").on("click", function (e) {
      e.preventDefault();
      var csInterface = new CSInterface();
      var path = csInterface.getSystemPath(SystemPath.EXTENSION) + "/payloads/example.epr";
      csInterface.evalScript("$._PPP_.stitch(" + JSON.stringify(path) + ")");
   });

   $("#transcodeexternal").on("click", function (e) {
      e.preventDefault();
      var csInterface = new CSInterface();
      var path = csInterface.getSystemPath(SystemPath.EXTENSION) + "/payloads/example.epr";
      csInterface.evalScript("$._PPP_.transcodeExternal(" + JSON.stringify(path) + ")");
   });

   $("#saveaspng").on("click", function (e) {
      e.preventDefault();
      var csInterface = new CSInterface();
      var path = csInterface.getSystemPath(SystemPath.EXTENSION) + "/payloads/png.epr";
      csInterface.evalScript("$._PPP_.exportCurrentFrameAsPNG(" + JSON.stringify(path) + ")");
   });

   $("#ingest").on("click", function (e) {
      e.preventDefault();
      var csInterface = new CSInterface();
      var path = csInterface.getSystemPath(SystemPath.EXTENSION) + "/payloads/example.epr";
      csInterface.evalScript("$._PPP_.ingestFiles(" + JSON.stringify(path) + ")");
   });

   $("#transcodeusingdefaultpreset").on("click", function (e) {
      e.preventDefault();
      var csInterface = new CSInterface();
      var path = csInterface.getSystemPath(SystemPath.EXTENSION) + "/payloads/example.epr";
      csInterface.evalScript("$._PPP_.transcode(" + JSON.stringify(path) + ")");
   });

   document.body.onbeforeunload = function () {
      var csInterface = new CSInterface();
      csInterface.evalScript("$._PPP_.closeLog()");
   };
})
// function loadJsonNative() {
//    var csInterface = new CSInterface();
//    var result = window.cep.fs.showOpenDialog(false, false, "Select extracted_notes.json", "", ["json"]);

//    if (result.err === 0 && result.data.length > 0) {
//       var filePath = result.data[0];

//       // 关键修复：同时转义反斜杠和双引号，防止拼接 evalScript 字符串时发生断裂
//       var safePath = filePath.replace(/\\/g, "\\\\").replace(/"/g, "\\\"");

//       // 调用放置在 $._PPP_ 命名空间下的函数
//       csInterface.evalScript('$._PPP_.importJSONFromPath("' + safePath + '")');
//    }
// }
function loadJsonNative() {
   var fileInput = document.getElementById('jsonFileInput');
   
   // 清空之前的选择记录，确保重复选择同一个文件时仍能触发 onchange 事件
   fileInput.value = '';
   
   fileInput.onchange = function(event) {
      var file = event.target.files[0];
      if (!file) return;
      
      // CEP 环境下的 File 对象自带 .path 属性，直接获取系统绝对路径
      var filePath = file.path;
      
      if (filePath) {
         var csInterface = new CSInterface();
         // 转义反斜杠和双引号，防止拼接 evalScript 字符串时断裂
         var safePath = filePath.replace(/\\/g, "\\\\").replace(/"/g, "\\\"");
         
         csInterface.evalScript('$._PPP_.importJSONFromPath("' + safePath + '")');
      } else {
         alert("Error: 无法获取文件的本地路径。");
      }
   };
   
   // 模拟点击，唤起原生的文件选择窗口
   fileInput.click();
}
function tieba() {
   // 獲取插件與 Adobe 宿主通信的接口
   var cs = new CSInterface();

   if (confirm("111真关注吗")) {
      // 調用系統瀏覽器開啟 URL，這樣你的插件面板還能保持原樣
      cs.openURLInDefaultBrowser("https://tieba.baidu.com/f?kw=mizzle");
   }

}
function openExternalSite(url, confirmMsg) {
   var cs = new CSInterface();
   if (confirm(confirmMsg)) {
      cs.openURLInDefaultBrowser(url);
   }
}
