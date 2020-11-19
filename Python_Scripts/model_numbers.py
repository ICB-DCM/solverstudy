import os
import pandas as pd

from C import DIR_MODELS

df = pd.read_csv(os.path.join(DIR_MODELS, 'model_summary.tsv'), sep='\t')

print("Column names", df.columns)

print("Number of models:", df.shape[0])
print("Number of model groups:", len(df.short_id.unique()))
print("Number of AMICI importable models:", sum(df.amici_import == 'OK'))
print("Number of COPASI importable models:", sum(~pd.isnull(df.copasi_path)))

df_imp = df[(df.amici_import == 'OK') & (~pd.isnull(df.copasi_path))]
print("Number of importable models:", df_imp.shape[0])
print("Number of model groups:", len(df_imp.short_id.unique()))

df_acc = df_imp[df_imp.accepted]
print("Number of accepted models:", df_acc.shape[0])
print("Number of accepted model groups:", len(df_acc.short_id.unique()))