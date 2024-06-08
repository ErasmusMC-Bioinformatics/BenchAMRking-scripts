from lib.sample_organiser import SampleOrganiser
import pandas as pd
from pathlib import Path
from defines import *


if __name__ == '__main__':

    # organises files and samples
    samples = SampleOrganiser()

    # writes out sample overview to see if any are missing or wrongly typed/ named
    samples.write_out_sample_overview()

    file_name = Path.joinpath(OUTPUT_DIR / Path('comparison_all.xlsx'))

    if file_name.exists():
        file_name.unlink()  # deletes file if it exists

    with pd.ExcelWriter(file_name) as excel_engine:
        samples.create_comparison(excel_writer=excel_engine,
                                  sheet_name=f"all",
                                  cluster=True, binary=False, typing=True, corr=False, remove_front_parahentis=False)

        samples.create_comparison(excel_writer=excel_engine,
                                  sheet_name=f"all_binary",
                                  cluster=True, binary=True, typing=True, corr=False, remove_front_parahentis=False)


