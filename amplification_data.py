"""
カルテ、レセプトデータの量を任意の倍数に増幅させる
"""

import datetime
from pathlib import Path
import pandas as pd
from dateutil.relativedelta import relativedelta

# レセプトデータの増幅
def receipt_amplification(input_path, output_path, num):
    if not output_path.exists():
        output_path.mkdir(parents=True)

    for file in input_path.glob('**/*.UKE'):
        # print(file)
        with open(file, encoding='cp932') as f:
            rows = f.readlines()

        # 請求年月
        IR = [row for row in rows if row.startswith('IR')]
        month_d = datetime.datetime.strptime(str(IR).split(',')[7],
                                             '%Y%m') - relativedelta(
            months=1)
        if IR[0].split(",")[1] == '1':
            sk = '社保'
        elif IR[0].split(",")[1] == '2':
            sk = '国保'
        folder_name = month_d.strftime('%Y%m')
        outdir = output_path.joinpath(folder_name)
        if not outdir.exists():
            outdir.mkdir(parents=True)

        header = rows[0]
        footer = rows[-1]

        rows.pop(0)
        rows.pop(-1)

        outfile = outdir/f'{file.name.replace(".UKE", "")}{sk}.UKE'
        outtext = header
        for i in range(num):
            for row in rows:
                outtext += row
        outtext += footer

        with open(outfile, mode='x') as f:
            f.write(outtext)

# カルテデータの増幅
def karte_amplification(input_path, output_path, num):
    if not output_path.exists():
        output_path.mkdir(parents=True)

    files = input_path.glob('**/*.csv')

    for file in files:
        l = []
        df = pd.read_csv(file, engine='python', encoding='cp932', dtype='object')
        for i in range(num):
            l.append(df)
        out_df = pd.concat(l)
        out_file = output_path/file.name
        out_df.to_csv(out_file, index=False, encoding='cp932')

def maege(input_path, output_path):
    if not output_path.exists():
        output_path.mkdir(parents=True)

    files = input_path.glob('**/*.csv')
    list_isi = []
    list_kango = []
    list_syuzyutukiroku = []
    list_syuzyutureki = []

    for file in files:
        df = pd.read_csv(file, engine='python', encoding='cp932', dtype='object')
        if '医師記録' in file.name:
            list_isi.append(df)
        elif '看護記録' in file.name:
            list_kango.append(df)
        elif '手術記録' in file.name:
            list_syuzyutukiroku.append(df)
        elif '手術歴' in file.name:
            list_syuzyutureki.append(df)

    def output(filename, target_list):
        outdf = pd.concat(target_list)
        outdf.to_csv(filename, index=False, encoding='cp932')

    output(output_path/'医師記録.csv', list_isi)
    output(output_path/'看護記録.csv', list_kango)
    output(output_path/'手術記録.csv', list_syuzyutukiroku)
    output(output_path/'手術歴.csv', list_syuzyutureki)

if __name__ == '__main__':
    input_path = Path.cwd()/'split_karte'
    output_path = input_path/'marge'
    maege(input_path, output_path)
