# first line: 1
@joblib_memory.cache
def load_data_joblib(file_path):
    return pd.read_pickle(file_path)
