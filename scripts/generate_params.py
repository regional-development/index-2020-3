import os 
import pandas as pd 
from src.utils import ROOT
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())
URL = os.environ.get("GSHEET")
COLUMNS_MAP = {"Параметр нижнього рівня": "Параметр", "Розпорядник основного набору": "Розпорядник"}
COLUMNS = ["Параметр", "Опис параметру (показника) нижнього рівня", "Розпорядник"]


if __name__ == "__main__":
    df = pd.read_csv(URL).rename(columns=COLUMNS_MAP)
    df.sort_values("Параметр").loc[:, COLUMNS].to_csv(ROOT / "docs" / "_assets" / "params.csv", index=False)