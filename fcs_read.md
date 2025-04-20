# CyTOF: read fcs files and test cofactors
MKim

    <style>
        .bk-notebook-logo {
            display: block;
            width: 20px;
            height: 20px;
            background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAABx0RVh0U29mdHdhcmUAQWRvYmUgRmlyZXdvcmtzIENTNui8sowAAAOkSURBVDiNjZRtaJVlGMd/1/08zzln5zjP1LWcU9N0NkN8m2CYjpgQYQXqSs0I84OLIC0hkEKoPtiH3gmKoiJDU7QpLgoLjLIQCpEsNJ1vqUOdO7ppbuec5+V+rj4ctwzd8IIbbi6u+8f1539dt3A78eXC7QizUF7gyV1fD1Yqg4JWz84yffhm0qkFqBogB9rM8tZdtwVsPUhWhGcFJngGeWrPzHm5oaMmkfEg1usvLFyc8jLRqDOMru7AyC8saQr7GG7f5fvDeH7Ej8CM66nIF+8yngt6HWaKh7k49Soy9nXurCi1o3qUbS3zWfrYeQDTB/Qj6kX6Ybhw4B+bOYoLKCC9H3Nu/leUTZ1JdRWkkn2ldcCamzrcf47KKXdAJllSlxAOkRgyHsGC/zRday5Qld9DyoM4/q/rUoy/CXh3jzOu3bHUVZeU+DEn8FInkPBFlu3+nW3Nw0mk6vCDiWg8CeJaxEwuHS3+z5RgY+YBR6V1Z1nxSOfoaPa4LASWxxdNp+VWTk7+4vzaou8v8PN+xo+KY2xsw6une2frhw05CTYOmQvsEhjhWjn0bmXPjpE1+kplmmkP3suftwTubK9Vq22qKmrBhpY4jvd5afdRA3wGjFAgcnTK2s4hY0/GPNIb0nErGMCRxWOOX64Z8RAC4oCXdklmEvcL8o0BfkNK4lUg9HTl+oPlQxdNo3Mg4Nv175e/1LDGzZen30MEjRUtmXSfiTVu1kK8W4txyV6BMKlbgk3lMwYCiusNy9fVfvvwMxv8Ynl6vxoByANLTWplvuj/nF9m2+PDtt1eiHPBr1oIfhCChQMBw6Aw0UulqTKZdfVvfG7VcfIqLG9bcldL/+pdWTLxLUy8Qq38heUIjh4XlzZxzQm19lLFlr8vdQ97rjZVOLf8nclzckbcD4wxXMidpX30sFd37Fv/GtwwhzhxGVAprjbg0gCAEeIgwCZyTV2Z1REEW8O4py0wsjeloKoMr6iCY6dP92H6Vw/oTyICIthibxjm/DfN9lVz8IqtqKYLUXfoKVMVQVVJOElGjrnnUt9T9wbgp8AyYKaGlqingHZU/uG2NTZSVqwHQTWkx9hxjkpWDaCg6Ckj5qebgBVbT3V3NNXMSiWSDdGV3hrtzla7J+duwPOToIg42ChPQOQjspnSlp1V+Gjdged7+8UN5CRAV7a5EdFNwCjEaBR27b3W890TE7g24NAP/mMDXRWrGoFPQI9ls/MWO2dWFAar/xcOIImbbpA3zgAAAABJRU5ErkJggg==);
        }
    </style>
    <div>
        <a href="https://bokeh.org" target="_blank" class="bk-notebook-logo"></a>
        <span id="dd924601-cd3d-44f3-b1e1-dff0048db989">Loading BokehJS ...</span>
    </div>

    Unable to display output for mime type(s): application/javascript, application/vnd.bokehjs_load.v0+json

# Reading fcs files in a directory

    [Sample(v3.0, Tet2_194_CD3_CD28.fcs, 71 channels, 30562 events),
     Sample(v3.0, Tet2_194_LPS.fcs, 71 channels, 33507 events),
     Sample(v3.0, Tet2_194_VEH.fcs, 71 channels, 14994 events),
     Sample(v3.0, Tet2_205_CD3_CD28.fcs, 71 channels, 23737 events),
     Sample(v3.0, Tet2_205_LPS.fcs, 71 channels, 28403 events),
     Sample(v3.0, Tet2_205_VEH.fcs, 71 channels, 18004 events)]

# all fcs data combined as a DataFrame

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead th {
        text-align: right;
    }
</style>

|  | Time | Event_length | CD45_89Y | 102Pd | 104Pd | 105Pd | 106Pd | 108Pd | 110Pd | HLADR_111Cd | ... | 208Pb | CD16_209Bi | Center | Offset | Width | Residual | beadDist | bc_separation_dist | mahalanobis_dist | sample_id |
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| 0 | 661.041992 | 22.0 | 412.645020 | 25.777630 | 840.156738 | 62.351097 | 621.207642 | 35.149330 | 663.321167 | 3.907504 | ... | 0.000000 | 2.712706 | 665.995483 | 63.749474 | 41.665462 | 99.399338 | 146.214340 | 0.427387 | 2.119524 | Tet2_194_CD3_CD28.fcs |
| 1 | 1606.848999 | 30.0 | 86.169205 | 19.263371 | 754.377319 | 63.770561 | 702.919067 | 34.960449 | 615.405823 | 17.882900 | ... | 0.039206 | 0.574640 | 1014.872131 | 83.073563 | 74.469383 | 120.216301 | 84.530914 | 0.421493 | 2.356081 | Tet2_194_CD3_CD28.fcs |
| 2 | 2134.166992 | 27.0 | 235.820526 | 43.977959 | 682.236694 | 61.585442 | 506.093597 | 29.748413 | 420.823425 | 22.905087 | ... | 0.107103 | 1.655213 | 1008.516785 | 116.714310 | 89.460983 | 135.712341 | 155.546814 | 0.357073 | 2.992274 | Tet2_194_CD3_CD28.fcs |
| 3 | 2726.041992 | 34.0 | 401.721039 | 17.634621 | 486.760681 | 45.908226 | 421.965057 | 32.385147 | 372.157776 | 18.211843 | ... | 0.000000 | 0.000000 | 1193.339722 | 84.541939 | 87.027130 | 153.430710 | 123.058891 | 0.387981 | 1.092942 | Tet2_194_CD3_CD28.fcs |
| 4 | 3270.702881 | 26.0 | 340.457306 | 21.509212 | 665.266113 | 50.862789 | 549.097961 | 21.249895 | 520.453430 | 4.582990 | ... | 2.780666 | 0.446503 | 871.395264 | 84.206436 | 65.056786 | 101.099045 | 139.366653 | 0.431778 | 2.244912 | Tet2_194_CD3_CD28.fcs |

<p>5 rows × 72 columns</p>
</div>

# trimmed channels that are not used

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead th {
        text-align: right;
    }
</style>

|  | CD45_89Y | HLADR_111Cd | CD3_112Cd | CD4_114Cd | CD8_116Cd | CD196_141Pr | CD19_142Nd | CD127_143Nd | CD38_144Nd | CD1c_145Nd | ... | IgM_172Yb | CD184_173Yb | CD279_174Yb | TNFa_175Lu | CD56_176Yb | CD45_195Pt | CD45_196Pt | CD45_198Pt | CD16_209Bi | sample_id |
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| 0 | 412.645020 | 3.907504 | 78.869453 | 0.064539 | 45.691082 | 3.176548 | 0.000000 | 3.065427 | 17.981371 | 1.267487 | ... | 2.797745 | 5.964279 | 2.519733 | 0.423804 | 0.622348 | 2.881647 | 0.000000 | 0.0 | 2.712706 | Tet2_194_CD3_CD28.fcs |
| 1 | 86.169205 | 17.882900 | 96.898453 | 0.000000 | 36.989292 | 0.000000 | 0.000000 | 0.126138 | 26.494999 | 0.000000 | ... | 0.646155 | 0.039602 | 0.018124 | 84.315346 | 1.118604 | 3.115852 | 2.533583 | 0.0 | 0.574640 | Tet2_194_CD3_CD28.fcs |
| 2 | 235.820526 | 22.905087 | 35.147606 | 38.417339 | 0.718573 | 0.000000 | 1.577704 | 2.337688 | 5.960651 | 0.000000 | ... | 0.000000 | 0.667073 | 11.242700 | 0.941599 | 0.012648 | 1.672839 | 0.748688 | 0.0 | 1.655213 | Tet2_194_CD3_CD28.fcs |
| 3 | 401.721039 | 18.211843 | 168.439880 | 4.329476 | 181.127151 | 0.000000 | 1.589560 | 3.125704 | 32.871078 | 0.000000 | ... | 7.390351 | 34.851997 | 2.578116 | 3.053176 | 0.000000 | 0.000000 | 0.111948 | 0.0 | 0.000000 | Tet2_194_CD3_CD28.fcs |
| 4 | 340.457306 | 4.582990 | 103.852966 | 50.595531 | 0.000000 | 0.000000 | 0.000000 | 9.441140 | 8.959432 | 0.000000 | ... | 0.667570 | 140.122437 | 0.000000 | 4.926303 | 0.758325 | 0.010309 | 0.000000 | 0.0 | 0.446503 | Tet2_194_CD3_CD28.fcs |

<p>5 rows × 44 columns</p>
</div>

    (149207, 44)

# Plot marker densit plot with various cofactors

## With a cofactor = 1.0

![](figures_for_cofactor/Tet2_cofactor_1.0.png)

## With a cofactor = 6.0

![](figures_for_cofactor/Tet2_cofactor_6.0.png)
