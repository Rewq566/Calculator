import streamlit as st
import pandas as pd
import os

def rond_omhoog(waarde, beschikbare_waarden):
    beschikbare_waarden = sorted(beschikbare_waarden)

    for v in beschikbare_waarden:
        if waarde <= v:
            return v

    return beschikbare_waarden[-1]  # max als groter dan alles

def converteer_prijs(prijs):

    prijs = str(prijs)

    # verwijder alles behalve cijfers en punten/komma's
    toegestaan = "0123456789,."
    prijs = "".join(c for c in prijs if c in toegestaan)

    # als meerdere punten → laatste is decimal, rest zijn duizendtallen
    if prijs.count(".") > 1:

        delen = prijs.split(".")

        decimal = delen[-1]
        geheel = "".join(delen[:-1])

        prijs = geheel + "." + decimal

    # komma vervangen door punt
    if "," in prijs:
        prijs = prijs.replace(",", ".")

    return float(prijs)

st.set_page_config(page_title="Prijs Calculator", layout="centered")

CSV_MAP = "CSV"

st.title("Prijs Calculator")

# SESSION STATE DEFAULTS

if "breedte" not in st.session_state:
    st.session_state.breedte = 1000

if "hoogte" not in st.session_state:
    st.session_state.hoogte = 1000

if "delen_door" not in st.session_state:
    st.session_state.delen_door = 0.6

if "vermenigvuldigen_met" not in st.session_state:
    st.session_state.vermenigvuldigen_met = 1.21

# CSV bestanden ophalen

if not os.path.exists(CSV_MAP):
    st.error("Map 'csv' bestaat niet")
    st.stop()

files = [f for f in os.listdir(CSV_MAP) if f.endswith(".csv")]

if len(files) == 0:
    st.error("Geen CSV bestanden gevonden")
    st.stop()

selected_file = st.selectbox(
    "Selecteer product",
    files
)

# CSV laden (nu veilig)
df = pd.read_csv(os.path.join(CSV_MAP, selected_file))

df = df.set_index(df.columns[0])
df.columns = df.columns.astype(int)
df.index = df.index.astype(int)

# SIDEBAR

st.sidebar.title("Prijs instellingen")

st.sidebar.number_input(
    "Delen door",
    step=0.01,
    format="%.2f",
    key="delen_door"
)

st.sidebar.number_input(
    "Vermenigvuldigen met",
    step=0.01,
    format="%.2f",
    key="vermenigvuldigen_met"
)

# INPUT

col1, col2 = st.columns(2)

with col1:
    st.number_input(
        "Breedte (mm)",
        min_value=min(df.columns),
        max_value=max(df.columns),
        step=100,
        key="breedte"
    )

with col2:
    st.number_input(
        "Hoogte (mm)",
        min_value=min(df.index),
        max_value=max(df.index),
        step=100,
        key="hoogte"
    )

# BEREKENING

if st.button("Bereken prijs", use_container_width=True):

    ingevoerde_breedte = st.session_state.breedte
    ingevoerde_hoogte = st.session_state.hoogte

    # afronden naar eerstvolgende maat
    breedte = rond_omhoog(ingevoerde_breedte, df.columns)
    hoogte = rond_omhoog(ingevoerde_hoogte, df.index)

    try:

        basis_prijs = df.loc[hoogte, breedte]

        basis_prijs = converteer_prijs(basis_prijs)

        eindprijs = (
            basis_prijs
            / st.session_state.delen_door
            * st.session_state.vermenigvuldigen_met
        )

        st.info(f"Ingevoerde maat: {ingevoerde_breedte} x {ingevoerde_hoogte}")
        st.info(f"Berekende maat: {breedte} x {hoogte}")

        st.success(f"Basisprijs: € {basis_prijs:.2f}")
        st.success(f"Eindprijs: € {eindprijs:.2f}")

    except Exception as e:

        st.error("Deze maat bestaat niet in de tabel")

        st.error(f"Debug info: {e}")
