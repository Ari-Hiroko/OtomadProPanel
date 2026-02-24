      // 自由选择执行函数（原生JS，确保不会因为加载顺序失效）
      function executeFreeSelect() {
         var cycleLength = document.getElementById('cycleLengthSelect').value;
         var targetIndex = document.getElementById('targetIndexSelect').value;

         if (!cycleLength || !targetIndex) {
            alert("请先选择循环次数和目标索引！");
            return;
         }

         var jsxCommand = "$._PPP_.selectCustomCycle(" + Number(cycleLength) + ", " + Number(targetIndex) + ")";

         if (window.__adobe_cep__) {
            var csInterface = new CSInterface();
            csInterface.evalScript(jsxCommand, function (result) {
               console.log("ExtendScript 执行完毕，返回值: ", result);
            });
         } else {
            console.log("即将发送给宿主的脚本: ", jsxCommand);
            alert("当前不在 Premiere 环境中，脚本命令已打印到控制台: \n" + jsxCommand);
         }
      }

      // 页面加载回调函数
      function onLoaded() {
         var csInterface = new CSInterface();
         csInterface.evalScript('$._PPP_.getUserName()', function (result) {
            document.getElementById('username').textContent = result;
         });
         csInterface.evalScript('$._PPP_.getVersionString()', function (result) {
            document.getElementById('version_string').textContent = result;
         });
         csInterface.evalScript('$._PPP_.getActiveSequenceName()', function (result) {
            document.getElementById('active_seq').textContent = result;
         });
      }

      // 提供给 ext.js 回调使用的占位函数
      function myUserNameFunction(result) {
         document.getElementById('username').textContent = result;
      }
      function mySetProxyFunction(result) { }
      function myGetProxyFunction(result) {
         var prox = document.getElementById('proxies_on');
         if (prox) prox.textContent = 'Proxies enabled for sequence: ' + result;
      }
      // JSON文件加载功能
      function loadJsonNative() {
         var csInterface = new CSInterface();
         var result = window.cep.fs.showOpenDialog(false, false, "Select extracted_notes.json", "", ["json"]);

         if (result.err === 0 && result.data.length > 0) {
            var filePath = result.data[0];

            var safePath = filePath.replace(/\\/g, "\\\\").replace(/"/g, "\\\"");

            csInterface.evalScript('$._PPP_.importJSONFromPath("' + safePath + '")');
         }
      }

      // 给全局作用域添加函数
      window.loadJsonNative = loadJsonNative;
      window.tieba = function () {
         var csInterface = new CSInterface();
         if (confirm("111真关注吗")) {
            // 調用系統瀏覽器開啟 URL，這樣你的插件面板還能保持原樣
            csInterface.openURLInDefaultBrowser("https://tieba.baidu.com/f?kw=mizzle");
         }
      };
      window.openExternalSite = function (url, title) {
         var csInterface = new CSInterface();
         csInterface.openURLInDefaultBrowser(url);
      };

      // 拖拽处理函数
      window.dragHandler = function (event) {
         event.dataTransfer.setData("text", event.target.id);
      };

      // evalScript函数
      window.evalScript = function (script) {
         var csInterface = new CSInterface();
         csInterface.evalScript(script);
      };

      // 为所有按钮绑定点击事件
      $("#copypresets").on("click", function (e) {
         e.preventDefault();
         var csInterface = new CSInterface();
         var OSVersion = csInterface.getOSInformation();
         var path = csInterface.getSystemPath(SystemPath.EXTENSION);

         csInterface.evalScript('$._PPP_.getUserName()', myUserNameFunction);

         if (OSVersion) {
            if (OSVersion.indexOf("Windows") >= 0) {
               var initPath = 'C:\\Users\\' + username.innerHTML;
               var sep = '\\\\';
               path = path.replace(/\//g, sep);
            } else {
               var initPath = '/Users/' + username.innerHTML;
               var sep = '/';
            }

            path = path + sep + 'payloads' + sep + 'Effect\ Presets\ and\ Custom\ Items.prfpset';

            var readResult = window.cep.fs.readFile(path);

            if (0 == readResult.err) {
               var addOutPath = '/Documents/Adobe/Premiere\ Pro/22.0/Profile-' + username.innerHTML +
                  '/Effect\ Presets\ and\ Custom\ Items.prfpset';
               var fullOutPath = initPath + addOutPath;
               var writeResult = window.cep.fs.writeFile(fullOutPath, readResult.data);
               var resultMsg = "";

               if (0 == writeResult.err) {
                  resultMsg = "Successfully copied effect presets from panel to current user configuration.";
               } else {
                  resultMsg = "Failed to copy effect presets.";
               }

               var postToEventPanel = '$._PPP_.updateEventPanel(\'';
               postToEventPanel += resultMsg;
               postToEventPanel += '\'';
               postToEventPanel += ')';

               csInterface.evalScript(postToEventPanel);
            }
         }
      });

      $("#toggleproxy").on("click", function (e) {
         e.preventDefault();
         var csInterface = new CSInterface();
         csInterface.evalScript('$._PPP_.toggleProxyState()', mySetProxyFunction);
         csInterface.evalScript('$._PPP_.getProjectProxySetting()', myGetProxyFunction);
      });

      $("#checkforums").on("click", function (e) {
         e.preventDefault();
         var csInterface = new CSInterface();
         csInterface.openURLInDefaultBrowser("https://forums.adobe.com/community/premiere/sdk");
      });

      $("#openfolder").on("click", function (e) {
         e.preventDefault();
         var csInterface = new CSInterface();
         var OSVersion = csInterface.getOSInformation();
         var path = csInterface.getSystemPath(SystemPath.EXTENSION);

         if (OSVersion) {
            if (OSVersion.indexOf("Windows") >= 0) {
               var sep = '\\';
               path = path.replace(/\//g, sep);
               window.cep.process.createProcess('C:\\Windows\\explorer.exe', path);
            } else {
               window.cep.process.createProcess('/usr/bin/open', path);
            }
         }
      });

      $("#openlogfilefolder").on("click", function (e) {
         e.preventDefault();
         var csInterface = new CSInterface();
         var OSVersion = csInterface.getOSInformation();
         var userDataPath = csInterface.getSystemPath(SystemPath.USER_DATA);
         var justTheFirstBit = userDataPath.split('A');
         var actualDestinationPath = justTheFirstBit[0];

         if (OSVersion) {
            if (OSVersion.indexOf("Windows") >= 0) {
               actualDestinationPath = actualDestinationPath + "AppData/Roaming/Adobe/Premiere Pro/22.0/logs";
               var sep = '\\';
               actualDestinationPath = actualDestinationPath.replace(/\//g, sep);
               window.cep.process.createProcess('C:\\Windows\\explorer.exe', actualDestinationPath);
            } else {
               actualDestinationPath = actualDestinationPath + "Preferences/Adobe/Premiere Pro/22.0/logs";
               window.cep.process.createProcess('/usr/bin/open', actualDestinationPath);
            }
         }
      });

      $("#readAPIdocs").on("click", function (e) {
         e.preventDefault();
         var csInterface = new CSInterface();
         csInterface.openURLInDefaultBrowser("http://ppro.aenhancers.com");
      });

      $("#newseqfrompreset").on("click", function (e) {
         e.preventDefault();
         var csInterface = new CSInterface();
         var OSVersion = csInterface.getOSInformation();
         var path = csInterface.getSystemPath(SystemPath.EXTENSION);

         if (OSVersion) {
            if (OSVersion.indexOf("Windows") >= 0) {
               var sep = '\\\\';
               path = path.replace(/\//g, sep);
            } else {
               var sep = '/';
            }

            path = path + sep + 'payloads' + sep + 'PProPanel.sqpreset';

            var pre = '$._PPP_.createSequenceFromPreset(\'';
            var post = '\'';
            var postpost = ')';

            var whole_megillah = pre + path + post + postpost;

            csInterface.evalScript(whole_megillah);
         }
      });

      $("#renderusingdefaultpreset").on("click", function (e) {
         e.preventDefault();
         var csInterface = new CSInterface();
         var OSVersion = csInterface.getOSInformation();
         var path = csInterface.getSystemPath(SystemPath.EXTENSION);

         if (OSVersion) {
            if (OSVersion.indexOf("Windows") >= 0) {
               var sep = '\\\\';
               path = path.replace(/\//g, sep);
            } else {
               var sep = '/';
            }

            path = path + sep + 'payloads' + sep + 'example.epr';

            var pre = '$._PPP_.render(\'';
            var post = '\'';
            var postpost = ')';

            var whole_megillah = pre + path + post + postpost;

            csInterface.evalScript(whole_megillah);
         }
      });

      $("#stitchusingdefaultpreset").on("click", function (e) {
         e.preventDefault();
         var csInterface = new CSInterface();
         var OSVersion = csInterface.getOSInformation();
         var path = csInterface.getSystemPath(SystemPath.EXTENSION);

         if (OSVersion) {
            if (OSVersion.indexOf("Windows") >= 0) {
               var sep = '\\\\';
               path = path.replace(/\//g, sep);
            } else {
               var sep = '/';
            }

            path = path + sep + 'payloads' + sep + 'example.epr';

            var pre = '$._PPP_.stitch(\'';
            var post = '\'';
            var postpost = ')';

            var whole_megillah = pre + path + post + postpost;

            csInterface.evalScript(whole_megillah);
         }
      });

      $("#transcodeexternal").on("click", function (e) {
         e.preventDefault();
         var csInterface = new CSInterface();
         var OSVersion = csInterface.getOSInformation();
         var path = csInterface.getSystemPath(SystemPath.EXTENSION);

         if (OSVersion) {
            if (OSVersion.indexOf("Windows") >= 0) {
               var sep = '\\\\';
               path = path.replace(/\//g, sep);
            } else {
               var sep = '/';
            }

            path = path + sep + 'payloads' + sep + 'example.epr';

            var pre = '$._PPP_.transcodeExternal(\'';
            var post = '\'';
            var postpost = ')';

            var whole_megillah = pre + path + post + postpost;

            csInterface.evalScript(whole_megillah);
         }
      });

      $("#saveaspng").on("click", function (e) {
         e.preventDefault();
         var csInterface = new CSInterface();
         var OSVersion = csInterface.getOSInformation();
         var path = csInterface.getSystemPath(SystemPath.EXTENSION);

         if (OSVersion) {
            if (OSVersion.indexOf("Windows") >= 0) {
               var sep = '\\\\';
               path = path.replace(/\//g, sep);
            } else {
               var sep = '/';
            }

            path = path + sep + 'payloads' + sep + 'png.epr';

            var pre = '$._PPP_.exportCurrentFrameAsPNG(\'';
            var post = '\'';
            var postpost = ')';

            var whole_megillah = pre + path + post + postpost;

            csInterface.evalScript(whole_megillah);
         }
      });

      $("#ingest").on("click", function (e) {
         e.preventDefault();
         var csInterface = new CSInterface();
         var OSVersion = csInterface.getOSInformation();
         var path = csInterface.getSystemPath(SystemPath.EXTENSION);

         if (OSVersion) {
            if (OSVersion.indexOf("Windows") >= 0) {
               var sep = '\\\\';
               path = path.replace(/\//g, sep);
            } else {
               var sep = '/';
            }

            path = path + sep + 'payloads' + sep + 'example.epr';

            var pre = '$._PPP_.ingestFiles(\'';
            var post = '\'';
            var postpost = ');';

            var whole_megillah = pre + path + post + postpost;

            csInterface.evalScript(whole_megillah);
         }
      });

      $("#transcodeusingdefaultpreset").on("click", function (e) {
         e.preventDefault();
         var csInterface = new CSInterface();
         var OSVersion = csInterface.getOSInformation();
         var path = csInterface.getSystemPath(SystemPath.EXTENSION);

         if (OSVersion) {
            if (OSVersion.indexOf("Windows") >= 0) {
               var sep = '\\\\';
               path = path.replace(/\//g, sep);
            } else {
               var sep = '/';
            }

            path = path + sep + 'payloads' + sep + 'example.epr';

            var pre = '$._PPP_.transcode(\'';
            var post = '\'';
            var postpost = ')';

            var whole_megillah = pre + path + post + postpost;

            csInterface.evalScript(whole_megillah);
         }
      });

      // 页面加载回调函数
      function onLoaded() {
         // 初始化用户名、版本号等信息
         var csInterface = new CSInterface();
         csInterface.evalScript('$._PPP_.getUserName()', function (result) {
            document.getElementById('username').textContent = result;
         });
         csInterface.evalScript('$._PPP_.getVersionString()', function (result) {
            document.getElementById('version_string').textContent = result;
         });
         csInterface.evalScript('$._PPP_.getActiveSequenceName()', function (result) {
            document.getElementById('active_seq').textContent = result;
         });
      }

      // 定义回调函数
      function myUserNameFunction(result) {
         document.getElementById('username').textContent = result;
      }

      function mySetProxyFunction(result) {
         // 处理代理状态设置结果
      }

      function myGetProxyFunction(result) {
         document.getElementById('proxies_on').textContent = 'Proxies enabled for sequence: ' + result;
      }

      document.body.onbeforeunload = function () {
         var csInterface = new CSInterface();
         var OSVersion = csInterface.getOSInformation();
         var appVersion = csInterface.hostEnvironment.appVersion;
         var versionAsFloat = parseFloat(appVersion);

         csInterface.evalScript('$._PPP_.closeLog()');

         if (versionAsFloat < 10.3) {
            var path = "file:///Library/Application Support/Adobe/CEP/extensions/PProPanel/payloads/onbeforeunload.html";

            if (OSVersion.indexOf("Windows") >= 0) {
               path = "file:///C:/Program%20Files%20(x86)/Common%20Files/Adobe/CEP/extensions/PProPanel/payloads/onbeforeunload.html"
            }
            csInterface.openURLInDefaultBrowser(path);
         }
      };
