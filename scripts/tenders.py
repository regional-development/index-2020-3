import pandas as pd 
from src.utils import PATH_INTERIM
from db_utils import db_connect


ADMIN_REGIONS = {
    "02100000000" : "Вінницька",
    "03100000000" : "Волинська",
    "04100000000" : "Дніпропетровська",
    "05100000000" : "Донецька",
    "06100000000" : "Житомирська",
    "07100000000" : "Закарпатська",
    "08100000000" : "Запорізька",
    "09100000000" : "Івано-Франківська",
    "10100000000" : "Київська",
    "11100000000" : "Кіровоградська",
    "12100000000" : "Луганська",
    "13100000000" : "Львівська",
    "14100000000" : "Миколаївська", 
    "15100000000" : "Одеська",
    "16100000000" : "Полтавська",
    "17100000000" : "Рівненська",
    "18100000000" : "Сумська",
    "19100000000" : "Тернопільська",
    "20100000000" : "Харківська",
    "21100000000" : "Херсонська",
    "22100000000" : "Хмельницька",
    "23100000000" : "Черкаська",
    "24100000000" : "Чернівецька",
    "25100000000" : "Чернігівська",
}


def make_prozorro_dataset(start_date, end_date):
    q = """
    SELECT [DateInserted], 
           [tenderID_UA], 
           [ProzorroTenderID], 
           [status],
           [date], 
           [dateModified], 
           [tenderPeriod_startDate], 
           [tenderPeriod_endDate], 
           [procurementMethod], 
           [procurementMethodType], 
           [value_amount], 
           [BudgetName], 
           [BudgetCode], 
           [DepartmentalClassificationCode], 
           [classification_id]
      FROM [Prozorro].[dbo].[obl_disposers_proc_V1];"""
    
    df = db_connect(q)
    df["DATE_FROM_ID"] = pd.to_datetime(
        df["tenderID_UA"].str.extract(
            "UA-(\d{4}\-\d{2}\-\d{2})-", expand=False
            )
        )
    data = df.loc[
        df["DATE_FROM_ID"].between(start_date, end_date) & 
        df["status"].eq("complete")
    ].copy()

    open_procurements = (
        data
        .loc[data["procurementMethod"].eq("open")]
        .groupby("BudgetCode")["value_amount"].sum()
        .rename('open')
    )
    all_procurements = (
        data
        .groupby('BudgetCode')["value_amount"].sum()
        .rename('all')
    )
    
    result = pd.concat([open_procurements, all_procurements], axis=1).reset_index()
    result["p2_06_raw"] = result["open"] / result["all"]
    result["region"] = result["BudgetCode"].map(ADMIN_REGIONS)
    
    (PATH_INTERIM / "P2").mkdir(parents=True, exist_ok=True)
    result.to_excel(PATH_INTERIM / "P2" / "P02_007.xlsx", index=False)


if __name__ == "__main__":
    make_prozorro_dataset("2020-07-01", "2020-09-30")