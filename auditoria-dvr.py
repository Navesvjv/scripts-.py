import os

caminho = f'D:/'

dias = os.listdir(caminho)
dias.sort()
dias.remove('$RECYCLE.BIN')
dias.remove('System Volume Information')

with open('C:/Projetos/relatorio-2tab/listadvr-parte1.txt', 'w') as file:
    for dia in dias:
        splt = dia.split('-')
        cameras = os.listdir(f'{caminho}{dia}/')
        cameras.sort()
        for camera in cameras:
            file.write(f'\n ============= {splt[2]}/{splt[1]}/{splt[0]} --> [{camera}] =============\n\n')
            arquivos = os.listdir(f'{caminho}{dia}/{camera}/')
            arquivos.sort()
            for arq in arquivos:
                file.write(f'{arq}\n')