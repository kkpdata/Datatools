import sqlite3
conn = sqlite3.connect("normtraject 19-1 - GEKBinvoer_HBN01_220171130_EUR-STE.rtd")

# conn.row_factory = sqlite3.Row
cursor = conn.cursor()

x = []
y = []
z = []

# Name, GrassCoverErosionInwardsCalculationEntityId
for row in cursor.execute("SELECT Name, GrassCoverErosionInwardsCalculationEntityId "
                          "FROM GrassCoverErosionInwardsCalculationEntity "
                          "ORDER BY Name"):
    x.append(row)

# GrassCoverErosionInwardsCalculationEntityId, GrassCoverErosionInwardsOutputEntityId
for row in cursor.execute("SELECT GrassCoverErosionInwardsCalculationEntityId, GrassCoverErosionInwardsOutputEntityId, "
                          "WaveHeight, Probability "
                          "FROM GrassCoverErosionInwardsOutputEntity "
                          "ORDER BY GrassCoverErosionInwardsCalculationEntityId"):
    y.append(row)

# GrassCoverErosionInwardsOutputEntityId, DikeHeight
for row in cursor.execute("SELECT GrassCoverErosionInwardsOutputEntityId, DikeHeight "
                          "FROM GrassCoverErosionInwardsDikeHeightOutputEntity "
                          "ORDER BY GrassCoverErosionInwardsDikeHeightOutputEntityId"):
    z.append(row)
h = 0
i = 0
j = 0
k = 0
naam =[]
q = []
xy = []
yzHeight = []
yzWave = []
yzProb = []
calc = 0

while i < len(x):
    while j < len(y):
        if y[j][0] == x[i][1]:
            xy.append(y[j][1]) # vul lijst met id
            naam.append(x[i][0]) # vul lijst met vaknamen
            # print(str(x[i][0]) + chr(9) + str(y[j][1]))
            calc = 1 # er is een berekening uitgevoerd
        j = j + 1
    if calc == 0:
        xy.append(str(999))
    calc = 0
    j = 0
    i = i + 1

while h < len(xy):
    while k < len(z):
        if xy[h] == z[k][0]:
            yzHeight.append(z[k][1])
            #yzWave.append(y[h][2])
            #yzProb.append(y[h][3])
            # print(str(y[i][1]) + chr(9) + str(z[k][1]))
            calc = 1
        k = k + 1
    if calc == 0:
        yzHeight.append(str(999))
        # yzWave.append(str(999))
        # yzProb.append(str(999))
    calc = 0
    k = 0
    h = h + 1

h = 0
k = 0
while h < len(xy):
    while k < len(y):
        if xy[h] == y[k][1]:
            yzWave.append(y[k][2])
            yzProb.append(y[k][3])
            # print(str(y[i][1]) + chr(9) + str(z[k][1]))
            calc = 1
        k = k + 1
    if calc == 0:
        yzWave.append(999)
        yzProb.append(999)
    calc = 0
    k = 0
    h = h + 1

print(x)
print(xy)
print(yzHeight)
print(yzWave)
print(yzProb)

file = open('Resultaat.txt', 'w')
file.write('profiel' + chr(9) + 'dijkhoogte bij HBN' + chr(9) + 'golfhoogte' + chr(9) + 'faalkans' + '\n')
for idx, val in enumerate(xy):
    file.write(str(x[idx][0]) + chr(9) + str(yzHeight[idx]).replace('.',',') + chr(9) +
               str(yzWave[idx]).replace('.',',') + chr(9) + str(yzProb[idx]).replace('.',',') + '\n')
