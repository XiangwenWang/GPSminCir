# GPSminCir
GPSminCir is a package for calculating the position and the radius of the smallest circle which covers a given GPS track.

Installation
------------

GPSminCir can be installed via pip:
```
pip install GPSminCir
```

Usage
-----
The MinCir function takes an GPS-coordinate-pair array as input, and will return the position (in the format of GPS coordinates) and radius (in meters) of the smallest circle.

Input: [[lat1, lon1], [lat2, lon2], [lat3, lon3], ...]

Output: (O, r), where O and r are respectively the position and the radius of the smallest circle.

For example:
```python
import GPSminCir
GPSpairs = [[51.764865, -0.003145], [51.764865, -0.003145], [51.764865, -0.003145],
                [51.764190, -0.003530], [51.764068, -0.005696], [51.764053, -0.007808],
                [51.764746, -0.008535], [51.764721, -0.009518], [51.765195, -0.010123]]
res = GPSminCir.MinCir(GPSpairs)
print(res)
```
The output would be:
```
((51.765030051641155, -0.006633987247802714), 240.80316686855755)
```

