import csv

class RngPC:

    seedsbase1 = [2100005341, 1700015771, 247163863, 891644838, 1352476256, 1563244181, 1528068162, 511705468, 1739927914, 398147329, 1278224951, 20980264, 1178761637, 802909981, 1130639188, 1599606659, 952700148, -898770777, -1097979074, -2013480859, -338768120, -625456464, -2049746478, -550389733, -5384772, -128808769, -1756029551, 1379661854, 904938180, -1209494558, -1676357703, -1287910319, 1653802906, 393811311, -824919740, 1837641861, 946029195, 1248183957, -1684075875, -2108396259, -681826312, 1003979812, 1607786269, -585334321, 1285195346, 1997056081, -106688232, 1881479866, 476193932, 307456100, 1290745818, 162507240, -213809065, -1135977230, -1272305475, 1484222417, -1559875058, 1407627502, 1206176750, -1537348094, 638891383, 581678511, 1164589165, -1436620514, 1412081670, -1538191350, -284976976, 706005400]
    seedsbase2 = [10259, 24563, 11177, 56952, 46197, 49826, 27077, 1257, 44164, 56565, 31009, 46618, 64397, 46089, 58119, 13090, 19496, 47700, 21163, 16247, 574, 18658, 60495, 42058, 40532, 13649, 8049, 25369, 9373, 48949, 23157, 32735, 29605, 44013, 16623, 15090, 43767, 51346, 28485, 39192, 40085, 32893, 41400, 1267, 15436, 33645, 37189, 58137, 16264, 59665, 53663, 11528, 37584, 18427, 59827, 49457, 22922, 24212, 62787, 56241, 55318, 9625, 57622, 7580, 56469, 49208, 41671, 36458]

    seed = 0

    def __init__(self, seedID):
        # Initialise RNG Array List of Lists
        self.rngArrays = []
        rngArrays = self.rngArrays
        for i in range(0, 68):
            rngArrays.append([])

        # Import initial RNG values for each array on each seed
        with open("../Data/RngBase.csv") as rngBase:
            rngFileReader = csv.reader(rngBase, delimiter=",")
            row = list(rngFileReader)[seedID]
            rngID = 0
            for column in row:
                rngArrays[rngID].append(int(column))
                rngID += 1

        for i in range(0, 68):
            self.seed = rngArrays[i][0]
            for j in range(0, 10000):
                rngArrays[i].append(self.__rngRoll(i, self.seed))

    def __s32(self, n):
        n = n & 0xffffffff
        return (n ^ 0x80000000) - 0x80000000

    def __updateSeed(self, value):
        self.seed = value

    def __rngRoll(self, index, current_value):
        temp = self.__s32(self.__s32(current_value) * self.__s32(self.seedsbase1[index]) ^ self.seedsbase2[index])
        temp = temp
        temp = self.__s32((temp >> 0x10) + (temp << 0x10))
        self.__updateSeed(temp)
        temp = temp & 0x7fffffff
        return temp
