import pandas as pd 
from src.utils import PATH_INTERIM
from db_utils import db_connect


def readiness(timestamp=None):
    q = """
   SELECT "Dim_Regions"."ShortRegionName" AS "region",
          AVG("dbo_ReadinessLevelHistory"."PercentOfCost") AS "Готовність за касовими видатками", 
          AVG("dbo_ReadinessLevelHistory"."PercentActs") AS "Готовність за актами", 
          "dbo_ReadinessLevelHistory"."TimeStampUpdate"
     FROM "VB"."Dim_Objects"
LEFT JOIN "VB"."Dim_Regions"
       ON "Dim_Objects"."RegionID" = "Dim_Regions"."ID"
LEFT JOIN "VB"."Dim_Places"
       ON "Dim_Objects"."PlaceID" = "Dim_Places"."ID"
LEFT JOIN "VB"."Dim_PlaceType"
       ON "Dim_Places"."PlaceTypeID" = "Dim_PlaceType"."ID"
LEFT JOIN "VB"."dbo_ReadinessLevelHistory"
       ON "Dim_Objects"."ID" = "dbo_ReadinessLevelHistory"."ObjectID"
 GROUP BY "Dim_Regions"."ShortRegionName", "dbo_ReadinessLevelHistory"."TimeStampUpdate"
 ORDER BY "Dim_Regions"."ShortRegionName", "dbo_ReadinessLevelHistory"."TimeStampUpdate";"""
     
    data = db_connect(q, db="PostgreSQL")
    if timestamp is not None:
        mask = data["TimeStampUpdate"].eq(timestamp)
        return data.loc[mask]
    else:
        return data


def allocation(timestamp=None):
    q = """
   SELECT "Dim_Regions"."ShortRegionName" as "region",
          AVG("dbo_FinancingAll"."Amount") as "Обсяг", 
          "Dim_FinancingStage"."Name" as "Тип фінансування",
          "dbo_FinancingAll"."TimeStampUpdate"
     FROM "VB"."Dim_Objects"
LEFT JOIN "VB"."Dim_Regions"
       ON "Dim_Objects"."RegionID" = "Dim_Regions"."ID"
LEFT JOIN "VB"."Dim_Places"
       ON "Dim_Objects"."PlaceID" = "Dim_Places"."ID"
LEFT JOIN "VB"."Dim_PlaceType"
       ON "Dim_Places"."PlaceTypeID" = "Dim_PlaceType"."ID"
LEFT JOIN "VB"."dbo_FinancingAll"
       ON "Dim_Objects"."ID" = "dbo_FinancingAll"."ObjectID"
LEFT JOIN "VB"."Dim_FinancingStage"
       ON "dbo_FinancingAll"."FinancingStageID" = "Dim_FinancingStage"."ID"
LEFT JOIN "VB"."Dim_FinancingTypes"
       ON "dbo_FinancingAll"."FinancingTypeID" = "Dim_FinancingTypes"."ID"
    WHERE "dbo_FinancingAll"."FinancingStageID" IN (2,3) 
      AND "dbo_FinancingAll"."FinancingTypeID" = 18
 GROUP BY "Dim_Regions"."ShortRegionName", "Dim_FinancingStage"."Name", "dbo_FinancingAll"."TimeStampUpdate"
 ORDER BY "Dim_Regions"."ShortRegionName", "Dim_FinancingStage"."Name", "dbo_FinancingAll"."TimeStampUpdate";"""
    
    data = db_connect(q, db="PostgreSQL")
    df = (
        data
        .pivot(index=["region", "TimeStampUpdate"], columns="Тип фінансування", values="Обсяг")
        .fillna(0)
        .reset_index()
    )
    df["p4_08_raw"] = df["Касові видатки"] / df["Профінансовано"] * 100
    
    if timestamp is not None:
        mask = df["TimeStampUpdate"].eq(timestamp)
        return df.loc[mask]
    else:
        return df


def main(latest_date=None):
    if latest_date is not None:
        df1, df2 = allocation(latest_date), readiness(latest_date)
    else:
        df1, df2 = allocation(), readiness()
    df = pd.merge(df1, df2, how="outer", on=["region", "TimeStampUpdate"])
    
    (PATH_INTERIM / "P4").mkdir(parents=True, exist_ok=True)
    df.to_excel(PATH_INTERIM / "P4" / "P04_009.xlsx", index=False)


if __name__ == "__main__":
       main(latest_date="2020-10-02")