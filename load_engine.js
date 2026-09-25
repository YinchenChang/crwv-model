// 在 node 中載入引擎（核對腳本用）：CO 來自 company.json，再依序執行 segA、segB；以間接 eval 放入全域。
const fs = require('fs'), path = require('path');
module.exports = function loadEngine(dir = __dirname) {
  (0, eval)('var COMPANY_DATA = ' + fs.readFileSync(path.join(dir, 'company.json'), 'utf8') + ';\n' +
    fs.readFileSync(path.join(dir, 'segA.js'), 'utf8') + '\nvar ' + fs.readFileSync(path.join(dir, 'segB.js'), 'utf8'));  // segB 在建置中接續模板宣告鏈，node 中補 var
};
