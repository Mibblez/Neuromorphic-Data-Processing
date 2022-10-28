# import pytest
from plotting_utils import get_plotting_data
from plotting_utils.get_plotting_data import DataStorage
import pytest


def test_spatial_csv_bool_no_color():
    spatial_csv_data = get_plotting_data.SpatialCsvData.from_csv(
        "tests/test_data/OnOff-X-Y-Timestamp.csv", DataStorage.BOOL
    )

    assert spatial_csv_data.polarities == [True, False, False, True, True, True, True, True, False, False]
    assert spatial_csv_data.x_positions == [82, 17, 86, 69, 78, 94, 45, 45, 91, 86]
    assert spatial_csv_data.y_positions == [78, 71, 37, 104, 75, 30, 12, 12, 32, 84]
    assert spatial_csv_data.timestamps == [0, 4, 6, 8, 9, 9, 10, 11, 17, 19]
    assert spatial_csv_data.polarities_color == []


def test_spatial_csv_no_bool_color():
    spatial_csv_data = get_plotting_data.SpatialCsvData.from_csv(
        "tests/test_data/OnOff-X-Y-Timestamp.csv", DataStorage.COLOR
    )

    assert spatial_csv_data.polarities == []
    assert spatial_csv_data.x_positions == [82, 17, 86, 69, 78, 94, 45, 45, 91, 86]
    assert spatial_csv_data.y_positions == [78, 71, 37, 104, 75, 30, 12, 12, 32, 84]
    assert spatial_csv_data.timestamps == [0, 4, 6, 8, 9, 9, 10, 11, 17, 19]
    assert spatial_csv_data.polarities_color == ["g", "r", "r", "g", "g", "g", "g", "g", "r", "r"]


def test_spatial_csv_bool_color():
    spatial_csv_data = get_plotting_data.SpatialCsvData.from_csv(
        "tests/test_data/OnOff-X-Y-Timestamp.csv", DataStorage.BOOL_AND_COLOR
    )

    assert spatial_csv_data.polarities == [True, False, False, True, True, True, True, True, False, False]
    assert spatial_csv_data.x_positions == [82, 17, 86, 69, 78, 94, 45, 45, 91, 86]
    assert spatial_csv_data.y_positions == [78, 71, 37, 104, 75, 30, 12, 12, 32, 84]
    assert spatial_csv_data.timestamps == [0, 4, 6, 8, 9, 9, 10, 11, 17, 19]
    assert spatial_csv_data.polarities_color == ["g", "r", "r", "g", "g", "g", "g", "g", "r", "r"]


def test_incorrect_format():
    with pytest.raises(ValueError, match="CSV may not be the correct format.\nHeader should be On/Off,X,Y,Timestamp"):
        get_plotting_data.SpatialCsvData.from_csv("tests/test_data/OnOff-X-Y.csv", DataStorage.COLOR)


def test_empty_csv():
    with pytest.raises(ValueError, match="CSV file 'tests/test_data/OnOff-X-Y-Timestamp-NODATA.csv' seems to be empty"):
        get_plotting_data.SpatialCsvData.from_csv("tests/test_data/OnOff-X-Y-Timestamp-NODATA.csv", DataStorage.COLOR)
