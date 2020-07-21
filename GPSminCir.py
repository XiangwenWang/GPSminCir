#!/usr/bin/env python
'''
@Author: Xiangwen Wang
@Version: 1.0.5
@Description: A tool to calculate the radius of the smallest circle which covers the given GPS track.
@Input: [[lat1, lon1], [lat2, lon2], [lat3, lon3], ...]
@Output: (O, r), where O and r are respectively the position and the radius of the smallest circle.
'''

import math
import random
from functools import reduce


def distance(A, B):
    lat1, lon1 = A
    lat2, lon2 = B
    R = 6371000
    Haversine = (math.sin(math.radians((lat2 - lat1) / 2)))**2 + \
        math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * \
        (math.sin(math.radians((lon2 - lon1) / 2)))**2
    d = R * 2 * math.atan2(math.sqrt(Haversine), math.sqrt(1 - Haversine))
    return d


def convToCart(latlon):
    R = 6371000  # Earth radius in meters
    lat, lon = math.radians(latlon[0]), math.radians(latlon[1])
    x = R * math.cos(lon) * math.cos(lat)
    y = R * math.sin(lon) * math.cos(lat)
    z = R * math.sin(lat)
    return (x, y, z)


def FindDiaEdge(d_ABC):
    # if it is an obtuse triangle or a right triangle
    # edge AB would be the diameter
    if d_ABC[0]**2 >= d_ABC[1]**2 + d_ABC[2]**2:
        return 0
    # edge BC would be the diameter
    elif d_ABC[1]**2 >= d_ABC[0]**2 + d_ABC[2]**2:
        return 1
    # edge CA would be the diameter
    elif d_ABC[2]**2 >= d_ABC[1]**2 + d_ABC[0]**2:
        return 2
    # if it is an acute triangle
    return -1


def VectorLen(a):
    return math.sqrt(sum(map(lambda x: x**2, a)))


def CalLatLon(P):
    x, y, z = P
    curr_R = VectorLen((x, y, z))
    lat_rad = math.asin(z / curr_R)
    lon_rad = math.atan2(y, x)
    lat = math.degrees(lat_rad)
    lon = math.degrees(lon_rad)
    return (lat, lon)


def findMidEdge(pointpair):
    P1, P2 = pointpair
    P = list(map(lambda x, y: (x + y) / 2.0, P1, P2))
    return CalLatLon(P)


def Cir2Pts(A_s, B_s):
    A, B = convToCart(A_s), convToCart(B_s)
    O = findMidEdge((A, B))
    r = distance(A_s, B_s) / 2.0
    return (O, r)


def VectorPlus(a, b):
    return [x + y for x, y in zip(a, b)]


def VectorMinus(a, b):
    return [x - y for x, y in zip(a, b)]


def VectorTimesScaler(a, k):
    return [x * k for x in a]


def VectorDivScaler(a, k):
    return [x / k for x in a] if k else []


def VectorCross(a, b):
    x = a[1] * b[2] - a[2] * b[1]
    y = a[2] * b[0] - a[0] * b[2]
    z = a[0] * b[1] - a[1] * b[0]
    return (x, y, z)


def VectorDot(a, b):
    return sum(map(lambda x, y: x * y, a, b))


def Print_outlier(data, mincircle):
    NoError = True
    for i in data:
        if not InCircle(i, mincircle):
            print(distance(i, mincircle[0]))
            NoError = False
    if not NoError:
        print('\n%.2f\n' % mincircle[1])


def MinCirTri(A_s, B_s, C_s):
    A, B, C = convToCart(A_s), convToCart(B_s), convToCart(C_s)
    a = VectorMinus(A, C)
    b = VectorMinus(B, C)
    P1_denom = 2 * (VectorLen(VectorCross(a, b))**2)
    if P1_denom:
        P1_part1_1 = VectorTimesScaler(b, VectorLen(a)**2 / P1_denom)
        P1_part1_2 = VectorTimesScaler(a, VectorLen(b)**2 / P1_denom)
        P1_part1 = VectorMinus(P1_part1_1, P1_part1_2)
        P1 = VectorCross(P1_part1, VectorCross(a, b))
        P = VectorPlus(P1, C)
        O = CalLatLon(P)
        r = distance(O, A_s)
    else:
        dist_ABC = (distance(A_s, B_s), distance(B_s, C_s), distance(C_s, A_s))
        dia_edge = FindDiaEdge(dist_ABC)
        edges = ((A, B), (B, C), (C, A))
        O = findMidEdge(edges[dia_edge])
        r = dist_ABC[dia_edge] / 2.0
    return (O, r)


def InCircle(A, minimum_circle):
    __precision__ = 1e-6  # precision is 1e-6 meters
    return distance(A, minimum_circle[0]) <= (minimum_circle[1] + __precision__)


def MinCir_2PtsKnown(data_piece2):
    minimum_circle2 = Cir2Pts(data_piece2[-2], data_piece2[-1])
    all_in_circle = True
    for i in range(0, len(data_piece2) - 2):
        if not InCircle(data_piece2[i], minimum_circle2):
            all_in_circle = False
            break
    if all_in_circle:
        return minimum_circle2
    farthest = [minimum_circle2, 0]
    for i in range(0, len(data_piece2) - 2):
        if InCircle(data_piece2[i], minimum_circle2):
            continue
        curr_circle = MinCirTri(data_piece2[i], data_piece2[-2], data_piece2[-1])
        dist_pt_line = distance(curr_circle[0], minimum_circle2[0])
        if dist_pt_line > farthest[1]:
            farthest = (curr_circle, dist_pt_line)
    minimum_circle2 = farthest[0]
    Print_outlier(data_piece2, minimum_circle2)
    return minimum_circle2


def MinCir_1PtKnown(data_piece1):
    minimum_circle1 = Cir2Pts(data_piece1[0], data_piece1[-1])
    for i in range(1, len(data_piece1) - 1):
        if not InCircle(data_piece1[i], minimum_circle1):
            minimum_circle1 = MinCir_2PtsKnown(data_piece1[0: i + 1] + data_piece1[-1:])
    return minimum_circle1


def MinCir(data):
    data = reduce(lambda x, y: x if y in x else x + [y], [[], ] + data)
    data_num = len(data)
    if not data_num:
        return ((0.0, 0.0), 0.0)
    elif data_num == 1:
        return ((data[0][0], data[0][1]), 0.0)
    elif data_num == 2:
        return Cir2Pts(data[0], data[1])
    random.shuffle(data)
    minimum_circle = Cir2Pts(data[0], data[1])
    for i in range(2, data_num):
        if not InCircle(data[i], minimum_circle):
            minimum_circle = MinCir_1PtKnown(data[0: i + 1])
    Print_outlier(data, minimum_circle)
    return minimum_circle


if __name__ == '__main__':
    GPSpairs = [[51.764865, -0.003145], [51.764865, -0.003145], [51.764865, -0.003145],
                [51.764190, -0.003530], [51.764068, -0.005696], [51.764053, -0.007808],
                [51.764746, -0.008535], [51.764721, -0.009518], [51.765195, -0.010123],
                [51.765911, -0.008958], [51.766136, -0.008505], [51.766223, -0.008480],
                [51.768145, -0.007753], [51.769670, -0.006958], [51.770601, -0.007288],
                [51.771636, -0.008831], [51.770750, -0.009600], [51.770565, -0.011418],
                [51.770065, -0.010070], [51.770303, -0.007841], [51.770760, -0.009571],
                [51.769310, -0.010000], [51.769015, -0.010378], [51.768688, -0.008603],
                [51.769300, -0.006760], [51.768865, -0.004640], [51.768318, -0.004553],
                [51.768175, -0.004941], [51.768263, -0.005660], [51.767528, -0.007475],
                [51.767198, -0.004923], [51.767601, -0.002831], [51.769328, -0.003260],
                [51.768431, -0.003043], [51.767243, -0.002570], [51.767250, -0.001538],
                [51.768086, -0.000623], [51.768410, -0.001870], [51.768086, -0.000815],
                [51.768293, -0.000835], [51.770123, -0.001536], [51.770023, 0.0002330],
                [51.769308, -0.000310], [51.769620, 0.0006250], [51.768848, 0.0016750],
                [51.767821, 0.0012530], [51.767273, -0.000255], [51.765855, -0.000191],
                [51.764588, -0.002303], [51.764640, -0.003210], [51.764971, -0.002791]]
    print(MinCir(GPSpairs))
    # ((51.7682065260781, -0.005385086275948437), 491.02609034476205)
