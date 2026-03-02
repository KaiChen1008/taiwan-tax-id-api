from fastapi import FastAPI, Query, HTTPException
import pandas as pd
from typing import List, Dict
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gov ID Lookup API")

# 全域變數，存放資料
# 結構: { "營業人名稱": ["統一編號1", "統一編號2"] }
name_to_ubn_map: Dict[str, List[str]] = {}


@app.on_event("startup")
async def load_data():
    global name_to_ubn_map
    logger.info("正在載入 data.csv (約 300MB)，請稍候...")
    try:
        # 讀取必要欄位
        df = pd.read_csv(
            "data.csv",
            usecols=["營業人名稱", "統一編號"],
            skiprows=[1],  # 跳過第二行 (index 1) 的 metadata
            dtype={"統一編號": str, "營業人名稱": str},
        )

        # 移除 NaN 值，避免後續處理出錯
        df = df.dropna(subset=["營業人名稱", "統一編號"])

        # 使用 groupby 快速建立名稱對應 UBN 列表的字典
        name_to_ubn_map = df.groupby("營業人名稱")["統一編號"].apply(list).to_dict()
        logger.info(f"載入完成，共計 {len(name_to_ubn_map)} 個不重複名稱。")
    except Exception as e:
        logger.error(f"載入資料失敗: {e}")
        raise e


@app.get("/")
def read_root():
    return {"message": "Welcome to Gov ID Lookup API. Use /get_ubn?name=名稱"}


@app.get("/get_ubn")
async def get_ubn(name: str = Query(..., description="要查詢的營業人名稱")):
    name = name.strip()
    ubns = name_to_ubn_map.get(name)
    if not ubns:
        raise HTTPException(status_code=404, detail="找不到該營業人的統一編號")
    return ubns


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
