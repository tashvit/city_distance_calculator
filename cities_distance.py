# Calculates the distance between two cities and allows
# the user to specify a unit of distance.
# This program calculates distance using latitude and longitude coordinates.

import re
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from bs4 import BeautifulSoup
from math import radians, cos, sin, asin, sqrt
from requests import get


class CityCruiserUi(QMainWindow):
    """Program's view (GUI)"""

    def __init__(self, model):
        """View initializer"""
        super().__init__()
        self._model = model
        # Set main window properties
        self.setWindowTitle("City Cruiser")
        # self.setFixedSize(235, 235)
        # Set central widget and general layout
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        # Create the display, drop downs and button
        self._create_display()
        self._units_dropdown()
        self._cities_dropdowns(self._model.city_names)
        self._create_button()
        self._connect_signals()

    def _create_display(self):
        """Create the display"""
        # Create top label
        self.toplabel = QLabel()
        self.toplabel.setText("Calculate distance between 2 cities")
        self.toplabel.setFont(QtGui.QFont("Sanserif", 11))
        self.toplabel.setAlignment(Qt.AlignCenter)
        # Create the display widget
        self.display = QLineEdit()
        # Set display's properties
        self.display.setFont(QtGui.QFont("Sanserif", 11))
        self.display.setFixedHeight(30)
        self.display.setAlignment(Qt.AlignCenter)
        self.display.setReadOnly(True)
        # Add the display to the general layout
        self.generalLayout.addWidget(self.toplabel)
        self.generalLayout.addWidget(self.display)

    def _units_dropdown(self):
        """Create units combobox"""
        self.units_combobox = QComboBox()
        units = ["Kilometers", "Miles"]
        self.units_combobox.addItems(units)
        self.units_combobox.setFont(QtGui.QFont("Sanserif", 11))
        # Units label
        self.units_label = QLabel()
        self.units_label.setText("Units of distance")
        self.units_label.setFont(QtGui.QFont("Sanserif", 11))
        # Add widgets to general layout
        self.generalLayout.addWidget(self.units_label)
        self.generalLayout.addWidget(self.units_combobox)

    def _cities_dropdowns(self, city_info):
        """Create combobox widgets for cities"""
        self.city1_combobox = QComboBox()
        self.city1_combobox.setFont(QtGui.QFont("Sanserif", 11))
        self.city2_combobox = QComboBox()
        self.city2_combobox.setFont(QtGui.QFont("Sanserif", 11))

        # Combo box 2 and 3
        self.city1_lbl = QLabel()
        self.city1_lbl.setText("Pick City One: ")
        self.city1_lbl.setFont(QtGui.QFont("Sanserif", 11))
        self.city1_combobox.addItems(city_info)

        self.city2_lbl = QLabel()
        self.city2_lbl.setText("Pick City Two: ")
        self.city2_lbl.setFont(QtGui.QFont("Sanserif", 11))
        self.city2_combobox.addItems(city_info)

        # Add combo boxes to general layout
        self.generalLayout.addWidget(self.city1_lbl)
        self.generalLayout.addWidget(self.city1_combobox)
        self.generalLayout.addWidget(self.city2_lbl)
        self.generalLayout.addWidget(self.city2_combobox)

    def _create_button(self):
        self.button = QPushButton("Calculate Distance")
        self.button.setFont(QtGui.QFont("Sanserif", 11))
        self.button.setStyleSheet("background-color : rgb(207,225,255)")
        self.generalLayout.addWidget(self.button)

    def set_display_text(self, text):
        """Set display's text"""
        self.display.setText(text)

    def clear_display(self):
        """Clears the display's text"""
        self.set_display_text("")

    def _get_city1_coor(self):
        """Get city 1 coordinates"""
        city1_coor = self._model.get_coordinates(
            expression=self.city1_combobox.currentText())
        return city1_coor

    def _get_city2_coor(self):
        """Get city 2 coordinates"""
        city2_coor = self._model.get_coordinates(
            expression=self.city2_combobox.currentText())
        return city2_coor

    def _calculate_result(self):
        """Get distance"""
        self.clear_display()
        result = self._model.get_distance(
            city1=self._get_city1_coor(), city2=self._get_city2_coor())
        if self.units_combobox.currentText() == "Kilometers":
            self.set_display_text(f"{result:1.4f} Km")
        else:
            self.set_display_text(f"{((result/6371) * 3956):1.4f} Miles")

    def _connect_signals(self):
        """Connect signals and slots"""
        self.button.clicked.connect(self._calculate_result)


class CityCruiserModel:
    """Program's model to handle operations"""

    def __init__(self):
        self.res = get("https://en.wikipedia.org/wiki/List_of_cities_by_elevation")
        self.soup = BeautifulSoup(self.res.text, "lxml")
        self.info_list = self.soup.select("tr")
        self.city_names = []
        self.cities = []
        self._get_city_names()

    def _get_city_names(self):
        self.info_list.pop(0)
        self.info_list.pop(0)
        for self.index, self.info in enumerate(self.info_list):
            try:
                self.location = self.info_list[self.index]
                country = self.location.select("td")[0].getText()
                city = self.location.select("td")[1].getText()
                self.city_names.append(f"{city}, {country}")
                self.cities.append(city)
            except IndexError:
                pass

    def get_coordinates(self, expression):
        for city in self.cities:
            if city in expression:
                city_url = f"https://en.wikipedia.org/wiki/{city}"
                res = get(city_url)
                soup = BeautifulSoup(res.text, "lxml")
                latitude = soup.select(".latitude")[0].text[0:-1]
                longitude = soup.select(".longitude")[0].text[0:-1]
                # Use regex to split and convert DMS into decimal degrees
                pattern = r"[^\W]+"
                lat = re.findall(pattern, latitude)
                # Set Seconds to be zero if latitude has no Seconds
                lat += ["0"] * (3 - len(lat))
                # Decimal degrees = Degrees + (Minutes/60) + (Seconds/3600)
                lat_decimal = int(lat[0]) + (int(lat[1]) / 60) + (int(lat[2]) / 3600)
                long = re.findall(pattern, longitude)
                # Set Seconds to be zero if longitude has no Seconds
                long += ["0"] * (3 - len(long))
                long_decimal = int(long[0]) + (int(long[1]) / 60) + (int(long[2]) / 3600)
                coordinates = lat_decimal, long_decimal
                return coordinates
        raise Exception("City not found")

    @staticmethod
    def get_distance(city1, city2):
        """Calculates distance between cities"""
        lat1 = radians(city1[0])
        long1 = radians(city1[1])
        lat2 = radians(city2[0])
        long2 = radians(city2[1])

        # Using Haversine formula
        lat_diff = lat2 - lat1
        long_diff = long2 - long1
        a = sin(lat_diff / 2) ** 2 + cos(lat1) * cos(lat2) * sin(long_diff / 2) ** 2
        c = 2 * asin(sqrt(a))

        # Radius of earth in kilometers. Use 3956 for miles
        r = 6371
        # Calculate the result
        distance = c * r
        return distance


def main():
    """Main function"""
    # Create an instance of QApplication
    citycruiser = QApplication(sys.argv)
    # Create instances of model and controller
    model = CityCruiserModel()
    # Show the program's GUI
    view = CityCruiserUi(model)
    view.show()
    # Execute the program's main loop
    sys.exit(citycruiser.exec_())


if __name__ == '__main__':
    main()
