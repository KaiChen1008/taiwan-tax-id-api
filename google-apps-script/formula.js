/**
 * Lookup Unified Business Number (UBN/BAN) by company name.
 * Usage: =GET_TAX_ID("TSMC")
 * 
 * @param {string} companyName Company name or keyword.
 * @return {string} Unified Business Number (Multiple results separated by comma).
 * @customfunction
 */
function GET_TAX_ID(companyName) {
  if (!companyName) return "";

  const url = `https://gov.kaichenl.com/get_ubn?name=${encodeURIComponent(companyName)}`;

  try {
    const response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    const data = JSON.parse(response.getContentText());

    if (!data || data.length === 0) return "查無資料";

    // Return the BAN directly if there's only one result
    if (data.length === 1) return data[0].ban;

    // Return "BAN CompanyName" for multiple results to facilitate comparison
    return data.map(d => `${d.ban} ${d.businessNm}`).join("\n");

  } catch (e) {
    return "Error: " + e.message;
  }
}
