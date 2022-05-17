import pandas as pd

def results_to_csv(schedule_list, csv_file, columns):
    """
    form PanDas dataframe with results and (optional) writes it into .csv file
    @param schedule_list: list of elements [[DATA1, WELL1, PARAM1, PARAM2, ...], [DATA2, ...], ...]
    @param csv_file: path to .csv file to save PanDas dataframe with results
    @param columns: list of columns in output .csv file
    @return: PanDas dataframe with results
    """
    result = pd.DataFrame(schedule_list)
    result.columns = columns
    result.to_csv(csv_file, sep=";", header=columns)
    return result
