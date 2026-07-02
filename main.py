import csv

import duckdb
import streamlit as st

# Ref: Singapore Department of Statistics. (2023). Indicators On Population, Annual (2026) [Dataset]. data.gov.sg


class DuckDBConnection:
    def __init__(self, csv_path):
        self.duckdb = duckdb.connect()
        self.csv_path = csv_path
        self.duckdb.sql(
            f"""
            CREATE OR REPLACE VIEW raw AS
            SELECT * FROM read_csv('{self.csv_path}', header=True)
            """
        )

    def get_population(self, data_series: tuple):
        return self.duckdb.sql(
            f"""
            WITH unpivoted AS (
                UNPIVOT (
                    SELECT DataSeries, COLUMNS('201[5-9]|202[0-5]')
                    FROM raw
                    WHERE DataSeries IN {data_series}
                )
                ON COLUMNS('201[5-9]|202[0-5]')
                INTO NAME Year VALUE Population
            )
            SELECT
                DataSeries as Type,
                Year,
                Population
            FROM unpivoted
            ORDER BY Year ASC;
            """
        )


def do_streamlit():
    st.header("SG Population")
    conn = DuckDBConnection(csv_path="IndicatorsOnPopulationAnnual.csv")
    df = conn.get_population(
        ("Total Population", "Resident Population", "Non-Resident Population")
    ).pl()
    st.line_chart(df, x="Year", y="Population", color="Type")
    df = conn.get_population(
        ("Singapore Citizen Population", "Permanent Resident Population")
    ).pl()
    st.line_chart(df, x="Year", y="Population", color="Type")
    conn = DuckDBConnection(
        csv_path="SingaporeResidentsByAgeGroupEthnicGroupAndSexAtEndJuneAnnual.csv"
    )
    df = conn.get_population(
        (
            "Total Residents",
            "Total Malays",
            "Total Chinese",
            "Total Indians",
            "Other Ethnic Groups (Total)",
        )
    ).pl()
    st.line_chart(df, x="Year", y="Population", color="Type")


if __name__ == "__main__":
    do_streamlit()
