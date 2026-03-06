/**
 * Company Name → Unified Business Number (UBN) Lookup
 * API Endpoint: https://gov.kaichenl.com/get_ubn?name=COMPANY_NAME
 * Reads from Column A, writes results to Column B.
 */

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("🔍 Tax ID Lookup")
    .addItem("Start Lookup", "batchQueryBan")
    .addItem("Clear Column B Results", "clearResults")
    .addToUi();
}

function batchQueryBan() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const ui = SpreadsheetApp.getUi();

  const lastRow = sheet.getRange("A:A").getValues()
    .filter(r => r[0] !== "").length;

  if (lastRow === 0) {
    ui.alert("A欄沒有資料！");
    return;
  }

  const confirm = ui.alert(
    "開始查詢",
    `共 ${lastRow} 筆，確定開始？`,
    ui.ButtonSet.OK_CANCEL
  );
  if (confirm !== ui.Button.OK) return;

  const names = sheet.getRange(1, 1, lastRow).getValues();
  let success = 0, notFound = 0, error = 0;

  for (let i = 0; i < names.length; i++) {
    const name = String(names[i][0]).trim();
    if (!name) continue;

    // Skip if result already exists (allows resuming interrupted runs)
    const existing = sheet.getRange(i + 1, 2).getValue();
    if (existing !== "") continue;

    try {
      const url = `https://gov.kaichenl.com/get_ubn?name=${encodeURIComponent(name)}`;
      const response = UrlFetchApp.fetch(url, {
        method: "GET",
        muteHttpExceptions: true,
      });

      const code = response.getResponseCode();
      const body = response.getContentText();

      if (code === 200) {
        const data = JSON.parse(body);
        const ubn = data.ubn ?? data.ban ?? data.result ?? body.trim();
        sheet.getRange(i + 1, 2).setValue(ubn || "查無資料");
        ubn ? success++ : notFound++;
      } else if (code === 404) {
        sheet.getRange(i + 1, 2).setValue("查無資料");
        notFound++;
      } else {
        sheet.getRange(i + 1, 2).setValue(`錯誤 ${code}`);
        error++;
      }

    } catch (e) {
      sheet.getRange(i + 1, 2).setValue("連線失敗");
      error++;
    }

    // Update progress in spreadsheet title every 10 rows
    if ((i + 1) % 10 === 0) {
      SpreadsheetApp.getActiveSpreadsheet()
        .rename(`查詢中 ${i + 1}/${lastRow}...`);
    }

    Utilities.sleep(200);
  }

  ui.alert("完成！",
    `✅ 成功：${success} 筆\n❌ 查無：${notFound} 筆\n⚠️ 錯誤：${error} 筆`,
    ui.ButtonSet.OK);
}

function clearResults() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const ui = SpreadsheetApp.getUi();
  const confirm = ui.alert("確定清除B欄所有結果？", ui.ButtonSet.OK_CANCEL);
  if (confirm === ui.Button.OK) {
    const lastRow = sheet.getLastRow();
    if (lastRow > 0) sheet.getRange(1, 2, lastRow).clearContent();
  }
}
